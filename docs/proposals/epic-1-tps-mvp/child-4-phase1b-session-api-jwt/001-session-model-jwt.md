# Stage 1: Session Model + JWT Utils

**Objective**: Реализовать модель сессии и утилиты JWT в `core/session.py`, добавить секрет в `Settings`.
**Duration**: ~1 час
**Dependencies**: Child #3 завершён (Pool Manager доступен)

## Detailed Steps

### Step 1.1: Добавить зависимость `python-jose`

**Action**: Добавить `python-jose[cryptography]` в `requirements.txt`.

**Implementation**:
```
# requirements.txt — добавить строку:
python-jose[cryptography]
```

**Verification**:
- [ ] `pip install -r requirements.txt` проходит без ошибок
- [ ] `from jose import jwt` работает в REPL

**Success Criteria**:
- ✅ Пакет установлен и импортируется

---

### Step 1.2: Добавить `tps_jwt_secret` в `Settings`

**Action**: Расширить `core/config.py` — добавить поле `tps_jwt_secret` и `tps_jwt_algorithm`.

**Implementation**:
```python
# core/config.py
class Settings(BaseSettings):
    # ... existing fields ...
    tps_jwt_secret: str = "change-me-in-production"
    tps_jwt_algorithm: str = "HS256"
```

Добавить в `.env.example`:
```
TPS_JWT_SECRET=change-me-in-production
```

**Verification**:
- [ ] `settings.tps_jwt_secret` читается из `Settings()`
- [ ] Переменная окружения `TPS_JWT_SECRET=secret python -c "from core.config import settings; print(settings.tps_jwt_secret)"` выводит `secret`

**Success Criteria**:
- ✅ Секрет конфигурируется через env var

---

### Step 1.3: Реализовать `core/session.py`

**Action**: Написать `SessionPayload`, `create_token`, `verify_token`.

**Implementation**:
```python
# core/session.py
from datetime import datetime, timezone
from typing import Optional

from jose import JWTError, jwt
from pydantic import BaseModel

from .config import settings


class SessionPayload(BaseModel):
    sub: str                  # всегда "session"
    container_id: str
    pack_id: str
    exercise_id: Optional[str] = None
    exp: int                  # unix timestamp


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
    """Decode and validate JWT. Returns None on any error."""
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
```

**Verification**:
- [ ] `create_token("abc", "rustlings", 3600)` возвращает непустую строку
- [ ] `verify_token(token)` возвращает `SessionPayload` с правильными полями
- [ ] `verify_token("invalid")` возвращает `None`
- [ ] `verify_token` с истёкшим токеном (exp в прошлом) возвращает `None`

**Success Criteria**:
- ✅ Round-trip create → verify работает корректно
- ✅ Невалидный/истёкший токен → `None`

---

## Testing Plan

### Manual Tests (REPL)
```python
from core.session import create_token, verify_token

token = create_token("container123", "rustlings", 3600, "intro1")
payload = verify_token(token)
assert payload.container_id == "container123"
assert payload.pack_id == "rustlings"
assert payload.exercise_id == "intro1"

assert verify_token("garbage") is None
```

### Edge Cases
- Токен с `exercise_id=None` (shell без упражнения)
- Токен с TTL=0 (истекает немедленно) → `verify_token` возвращает `None`

## Rollback Plan

Файлы `core/session.py` и `core/config.py` изолированы. При проблемах — `git revert` изменений, приложение продолжает работать (session.py был заглушкой).

## Definition of Done

- [ ] `python-jose[cryptography]` добавлен в `requirements.txt`
- [ ] `tps_jwt_secret` и `tps_jwt_algorithm` в `Settings`
- [ ] `TPS_JWT_SECRET` добавлен в `.env.example`
- [ ] `create_token` возвращает валидный JWT
- [ ] `verify_token` возвращает `SessionPayload` или `None`
- [ ] Ручные тесты пройдены
