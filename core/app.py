import asyncio
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel

from .config import settings
from .pack_registry import PackRegistry, PackConfig
from .pool_manager import PoolManager, InMemoryStore
from .session import create_token, verify_token
from .ws_proxy import handle_ws

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Terminal Pool Service", version="0.3.0")

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


class SessionRequest(BaseModel):
    pack_id: str
    exercise_id: Optional[str] = None


class SessionResponse(BaseModel):
    session_token: str
    ws_url: str
    expires_at: str


# ---------------------------------------------------------------------------
# API routes — packs
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
# API routes — sessions
# ---------------------------------------------------------------------------

@app.post("/api/sessions", response_model=SessionResponse)
async def create_session(body: SessionRequest):
    pack = registry.get(body.pack_id)
    if pack is None:
        raise HTTPException(status_code=404, detail="Pack not found")

    container_id = await pool_manager.allocate(body.pack_id)
    if container_id is None:
        raise HTTPException(status_code=503, detail={"error": "no_capacity"})

    ttl_sec = pack.pool.session_timeout_sec
    token = create_token(container_id, body.pack_id, ttl_sec, body.exercise_id)
    expires_at = (datetime.now(timezone.utc) + timedelta(seconds=ttl_sec)).isoformat()

    return SessionResponse(
        session_token=token,
        ws_url=f"/ws/{token}",
        expires_at=expires_at,
    )


@app.delete("/api/sessions/{token}", status_code=204)
async def delete_session(token: str):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    await pool_manager.release(payload.pack_id, payload.container_id)


# ---------------------------------------------------------------------------
# WebSocket — token-authenticated PTY session
# ---------------------------------------------------------------------------

@app.websocket("/ws/{token}")
async def websocket_session(websocket: WebSocket, token: str):
    payload = verify_token(token)
    if payload is None:
        await websocket.close(code=4401)
        return

    remaining_ttl = payload.exp - int(time.time())
    if remaining_ttl <= 0:
        await websocket.close(code=4401)
        return

    try:
        await asyncio.wait_for(
            handle_ws(websocket, payload.container_id),
            timeout=float(remaining_ttl),
        )
    except asyncio.TimeoutError:
        logger.info("Session TTL expired for container %s.", payload.container_id[:12])
        try:
            await websocket.close(code=4401)
        except Exception:
            pass
    finally:
        await pool_manager.release(payload.pack_id, payload.container_id)


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
