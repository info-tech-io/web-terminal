import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Optional

import docker
import docker.errors

from .pack_registry import PackConfig

logger = logging.getLogger(__name__)

_REPLENISH_INTERVAL_SEC = 5


# ---------------------------------------------------------------------------
# Storage abstraction
# ---------------------------------------------------------------------------

class PoolStore(ABC):
    """Abstract pool state storage.

    Concrete implementations: InMemoryStore (default), RedisStore (future).
    """

    @abstractmethod
    async def get_all(self, pack_id: str) -> dict[str, str]:
        """Return {container_id: state} for the pack."""

    @abstractmethod
    async def set_state(self, pack_id: str, container_id: str, state: str) -> None:
        """Set container state ("warm" or "busy")."""

    @abstractmethod
    async def remove(self, pack_id: str, container_id: str) -> None:
        """Remove container from the pool."""

    @abstractmethod
    async def allocate_warm(self, pack_id: str) -> Optional[str]:
        """Atomically pick a warm container and mark it busy.

        Returns container_id or None if no warm containers available.
        """


class InMemoryStore(PoolStore):
    def __init__(self) -> None:
        self._data: dict[str, dict[str, str]] = {}
        self._lock = asyncio.Lock()

    async def get_all(self, pack_id: str) -> dict[str, str]:
        async with self._lock:
            return dict(self._data.get(pack_id, {}))

    async def set_state(self, pack_id: str, container_id: str, state: str) -> None:
        async with self._lock:
            self._data.setdefault(pack_id, {})[container_id] = state

    async def remove(self, pack_id: str, container_id: str) -> None:
        async with self._lock:
            self._data.get(pack_id, {}).pop(container_id, None)

    async def allocate_warm(self, pack_id: str) -> Optional[str]:
        async with self._lock:
            pool = self._data.get(pack_id, {})
            for cid, state in pool.items():
                if state == "warm":
                    pool[cid] = "busy"
                    return cid
            return None


# ---------------------------------------------------------------------------
# Pool Manager
# ---------------------------------------------------------------------------

class PoolManager:
    def __init__(self, store: PoolStore) -> None:
        self._store = store
        self._docker: docker.DockerClient | None = None
        self._packs: dict[str, PackConfig] = {}
        self._replenish_locks: dict[str, asyncio.Lock] = {}

    def _get_docker(self) -> docker.DockerClient:
        if self._docker is None:
            self._docker = docker.from_env()
        return self._docker

    def set_packs(self, packs: dict[str, PackConfig]) -> None:
        """Register pack configurations. Called once after PackRegistry.load_all()."""
        self._packs = packs
        for pack_id in packs:
            self._replenish_locks[pack_id] = asyncio.Lock()

    async def warm_count(self, pack_id: str) -> int:
        pool = await self._store.get_all(pack_id)
        return sum(1 for s in pool.values() if s == "warm")

    async def busy_count(self, pack_id: str) -> int:
        pool = await self._store.get_all(pack_id)
        return sum(1 for s in pool.values() if s == "busy")

    async def allocate(self, pack_id: str) -> Optional[str]:
        """Return a warm container_id marked busy, or None if pool is empty."""
        container_id = await self._store.allocate_warm(pack_id)
        if container_id:
            logger.info("Allocated %s for pack %s", container_id[:12], pack_id)
            asyncio.create_task(self._replenish(pack_id))
        return container_id

    async def release(self, pack_id: str, container_id: str) -> None:
        """Destroy the container and replenish the pool."""
        logger.info("Releasing %s (pack %s)", container_id[:12], pack_id)
        await self._store.remove(pack_id, container_id)
        await asyncio.to_thread(self._destroy_container, container_id)
        asyncio.create_task(self._replenish(pack_id))

    async def initialize(self) -> None:
        """Warm up all pack pools at startup."""
        for pack_id in self._packs:
            asyncio.create_task(self._replenish(pack_id))

    async def replenish_loop(self) -> None:
        """Background task: keep all pools at target size."""
        logger.info("Replenish loop started (interval=%ds).", _REPLENISH_INTERVAL_SEC)
        while True:
            await asyncio.sleep(_REPLENISH_INTERVAL_SEC)
            for pack_id in list(self._packs):
                await self._replenish(pack_id)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _replenish(self, pack_id: str) -> None:
        """Ensure warm pool is at target size (protected by per-pack lock)."""
        lock = self._replenish_locks.get(pack_id)
        if lock is None:
            return
        async with lock:
            pack = self._packs.get(pack_id)
            if pack is None:
                return
            warm = await self.warm_count(pack_id)
            busy = await self.busy_count(pack_id)
            needed = pack.pool.size - warm - busy
            if needed <= 0:
                return
            logger.info("Replenishing %d container(s) for pack %s.", needed, pack_id)
            for _ in range(needed):
                cid = await asyncio.to_thread(self._start_warm_container, pack)
                if cid:
                    await self._store.set_state(pack_id, cid, "warm")

    def _start_warm_container(self, pack: PackConfig) -> Optional[str]:
        try:
            container = self._get_docker().containers.run(
                pack.image_tag,
                tty=True,
                stdin_open=True,
                detach=True,
                command="/bin/bash",
                labels={"tps.pack": pack.id},
            )
            logger.info("Started warm container %s (pack %s).", container.id[:12], pack.id)
            return container.id
        except docker.errors.ImageNotFound:
            logger.error(
                "Image '%s' not found for pack %s. Build it first.",
                pack.image_tag,
                pack.id,
            )
            return None
        except Exception as exc:
            logger.error("Failed to start container for pack %s: %s", pack.id, exc)
            return None

    def _destroy_container(self, container_id: str) -> None:
        try:
            self._get_docker().containers.get(container_id).remove(force=True)
            logger.info("Container %s destroyed.", container_id[:12])
        except docker.errors.NotFound:
            logger.debug("Container %s already gone.", container_id[:12])
        except Exception as exc:
            logger.warning("Could not destroy container %s: %s", container_id[:12], exc)
