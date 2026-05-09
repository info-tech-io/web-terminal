import json
import logging
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ExerciseConfig(BaseModel):
    id: str
    label: str
    description: str = ""


class PoolConfig(BaseModel):
    size: int = 3
    session_timeout_sec: int = 3600


class SourceConfig(BaseModel):
    repo: str
    branch: str = "main"
    clone_depth: int = 1


class PackConfig(BaseModel):
    id: str
    display_name: str
    description: str = ""
    image_tag: str
    pool: PoolConfig
    source: Optional[SourceConfig] = None
    exercises: list[ExerciseConfig] = []


class PackRegistry:
    def __init__(self, packs_dir: Path) -> None:
        self._packs_dir = packs_dir
        self._packs: dict[str, PackConfig] = {}

    def load_all(self) -> None:
        self._packs.clear()
        for pack_json in sorted(self._packs_dir.glob("*/pack.json")):
            try:
                data = json.loads(pack_json.read_text(encoding="utf-8"))
                pack = PackConfig(**data)
                self._packs[pack.id] = pack
                logger.info("Loaded pack: %s", pack.id)
            except Exception as exc:
                logger.warning("Failed to load pack from %s: %s", pack_json, exc)
        logger.info("Pack registry: %d pack(s) loaded.", len(self._packs))

    def get(self, pack_id: str) -> Optional[PackConfig]:
        return self._packs.get(pack_id)

    def all(self) -> list[PackConfig]:
        return list(self._packs.values())
