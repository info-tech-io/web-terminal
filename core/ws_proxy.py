import asyncio
import json
import logging

import docker
from fastapi import WebSocket, WebSocketDisconnect

from .config import settings

logger = logging.getLogger(__name__)


def _get_or_create_container(client: docker.DockerClient):
    """Gets the running container or creates a new one."""
    try:
        container = client.containers.get(settings.tps_container_name)
        if container.status != "running":
            logger.info("Container exists but is not running. Starting...")
            container.start()
        else:
            logger.info("Attaching to existing running container.")
        return container
    except docker.errors.NotFound:
        logger.info("Container '%s' not found. Creating...", settings.tps_container_name)
        container = client.containers.run(
            settings.tps_image_name,
            name=settings.tps_container_name,
            tty=True,
            stdin_open=True,
            detach=True,
            command="/bin/bash",
        )
        logger.info("Container '%s' created.", settings.tps_container_name)
        return container


async def handle_ws(websocket: WebSocket) -> None:
    """Handle a WebSocket connection: bridge browser ↔ Docker PTY."""
    await websocket.accept()
    logger.info("WebSocket connection accepted.")

    client = docker.from_env()
    try:
        container = await asyncio.to_thread(_get_or_create_container, client)

        exec_instance = await asyncio.to_thread(
            client.api.exec_create,
            container.id,
            "bash",
            stdout=True,
            stderr=True,
            stdin=True,
            tty=True,
        )
        exec_id = exec_instance["Id"]

        raw_socket = await asyncio.to_thread(
            client.api.exec_start, exec_id, tty=True, socket=True
        )
        sock = raw_socket._sock
        sock.setblocking(False)
        logger.info("Attached to container exec instance.")

        async def container_to_ws() -> None:
            loop = asyncio.get_event_loop()
            try:
                while True:
                    data = await loop.sock_recv(sock, 4096)
                    if not data:
                        break
                    await websocket.send_text(data.decode("utf-8", errors="ignore"))
            except Exception as exc:
                logger.debug("container→ws ended: %s", exc)

        async def ws_to_container() -> None:
            loop = asyncio.get_event_loop()
            try:
                while True:
                    raw = await websocket.receive_bytes()
                    # Resize control message: {"type":"resize","cols":N,"rows":M}
                    try:
                        msg = json.loads(raw)
                        if msg.get("type") == "resize":
                            await asyncio.to_thread(
                                client.api.exec_resize,
                                exec_id,
                                height=int(msg["rows"]),
                                width=int(msg["cols"]),
                            )
                            continue
                    except (json.JSONDecodeError, KeyError, ValueError):
                        pass
                    await loop.sock_sendall(sock, raw)
            except WebSocketDisconnect:
                logger.debug("ws→container: client disconnected")
            except Exception as exc:
                logger.debug("ws→container ended: %s", exc)

        await asyncio.gather(container_to_ws(), ws_to_container())

    except Exception as exc:
        logger.error("WS handler error: %s", exc)
    finally:
        logger.info("WebSocket handler finished.")
