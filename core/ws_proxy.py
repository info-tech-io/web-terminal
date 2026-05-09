import asyncio
import json
import logging

import docker
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


async def handle_ws(websocket: WebSocket, container_id: str) -> None:
    """Handle a WebSocket connection: bridge browser ↔ Docker PTY.

    Args:
        websocket: FastAPI WebSocket connection.
        container_id: ID of the pre-allocated container from the pool.
    """
    await websocket.accept()
    logger.info("WebSocket accepted for container %s.", container_id[:12])

    client = docker.from_env()
    try:
        container = await asyncio.to_thread(client.containers.get, container_id)

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
        logger.info("Attached to exec on container %s.", container_id[:12])

        async def container_to_ws() -> None:
            loop = asyncio.get_event_loop()
            try:
                while True:
                    data = await loop.sock_recv(sock, 4096)
                    if not data:
                        break
                    await websocket.send_bytes(data)
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
        logger.info("WebSocket handler finished for container %s.", container_id[:12])
