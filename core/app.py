import asyncio
import logging

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel

from .config import settings
from .pack_registry import PackRegistry, PackConfig
from .pool_manager import PoolManager, InMemoryStore
from .ws_proxy import handle_ws

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Terminal Pool Service", version="0.2.0")

templates = Jinja2Templates(directory="templates")

# Singletons
registry = PackRegistry(settings.packs_dir)
pool_manager = PoolManager(InMemoryStore())


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

@app.on_event("startup")
async def startup() -> None:
    registry.load_all()
    pool_manager.set_packs({p.id: p for p in registry.all()})
    await pool_manager.initialize()
    asyncio.create_task(pool_manager.replenish_loop())
    logger.info("TPS startup complete.")


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------

class PackSummary(BaseModel):
    id: str
    display_name: str
    description: str
    pool_size: int
    pool_warm: int
    pool_busy: int


class PackDetail(PackSummary):
    image_tag: str
    exercises: list


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

@app.get("/api/packs", response_model=list[PackSummary])
async def list_packs():
    result = []
    for pack in registry.all():
        result.append(PackSummary(
            id=pack.id,
            display_name=pack.display_name,
            description=pack.description,
            pool_size=pack.pool.size,
            pool_warm=await pool_manager.warm_count(pack.id),
            pool_busy=await pool_manager.busy_count(pack.id),
        ))
    return result


@app.get("/api/packs/{pack_id}", response_model=PackDetail)
async def get_pack(pack_id: str):
    pack = registry.get(pack_id)
    if pack is None:
        raise HTTPException(status_code=404, detail="Pack not found")
    return PackDetail(
        id=pack.id,
        display_name=pack.display_name,
        description=pack.description,
        image_tag=pack.image_tag,
        pool_size=pack.pool.size,
        pool_warm=await pool_manager.warm_count(pack.id),
        pool_busy=await pool_manager.busy_count(pack.id),
        exercises=[e.model_dump() for e in pack.exercises],
    )


# ---------------------------------------------------------------------------
# UI + legacy WS (to be replaced in Child #4)
# ---------------------------------------------------------------------------

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await handle_ws(websocket)
