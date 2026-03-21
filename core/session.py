from datetime import datetime, timezone
from typing import Optional

from jose import JWTError, jwt
from pydantic import BaseModel

from .config import settings


class SessionPayload(BaseModel):
    sub: str
    container_id: str
    pack_id: str
    exercise_id: Optional[str] = None
    exp: int


def create_token(
    container_id: str,
    pack_id: str,
    ttl_sec: int,
    exercise_id: Optional[str] = None,
) -> str:
    now = int(datetime.now(timezone.utc).timestamp())
    payload = {
        "sub": "session",
        "container_id": container_id,
        "pack_id": pack_id,
        "exercise_id": exercise_id,
        "exp": now + ttl_sec,
    }
    return jwt.encode(payload, settings.tps_jwt_secret, algorithm=settings.tps_jwt_algorithm)


def verify_token(token: str) -> Optional[SessionPayload]:
    """Decode and validate JWT. Returns None on any error (invalid, expired, wrong sub)."""
    try:
        data = jwt.decode(
            token,
            settings.tps_jwt_secret,
            algorithms=[settings.tps_jwt_algorithm],
        )
        if data.get("sub") != "session":
            return None
        return SessionPayload(**data)
    except (JWTError, Exception):
        return None
