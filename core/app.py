import logging

import docker
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

from .config import settings
from .ws_proxy import handle_ws

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Terminal Pool Service", version="0.1.0")

templates = Jinja2Templates(directory="templates")


def _build_image_if_missing() -> None:
    client = docker.from_env()
    try:
        client.images.get(settings.tps_image_name)
        logger.info("Docker image '%s' already exists.", settings.tps_image_name)
    except docker.errors.ImageNotFound:
        logger.info("Building Docker image '%s'...", settings.tps_image_name)
        client.images.build(path=".", dockerfile="Dockerfile", tag=settings.tps_image_name, rm=True)
        logger.info("Image '%s' built successfully.", settings.tps_image_name)


@app.on_event("startup")
async def startup() -> None:
    import asyncio
    await asyncio.to_thread(_build_image_if_missing)


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await handle_ws(websocket)
