# Stage 2: API Endpoints

**Objective**: Реализовать `POST /api/sessions` и `DELETE /api/sessions/{token}` в `core/app.py`.
**Duration**: ~1 час
**Dependencies**: Stage 1 завершён (`create_token`, `verify_token` доступны)

## Detailed Steps

### Step 2.1: Добавить request/response модели

**Action**: Добавить Pydantic-модели `SessionRequest` и `SessionResponse` в `core/app.py`.

**Implementation**:
```python
# core/app.py — новые модели
class SessionRequest(BaseModel):
    pack_id: str
    exercise_id: Optional[str] = None


class SessionResponse(BaseModel):
    session_token: str
    ws_url: str
    expires_at: str  # ISO 8601
```

**Verification**:
- [ ] `SessionRequest(pack_id="rustlings")` создаётся без ошибок
- [ ] `SessionRequest(pack_id="rustlings", exercise_id="intro1")` создаётся без ошибок

**Success Criteria**:
- ✅ Модели валидируются Pydantic корректно

---

### Step 2.2: Реализовать `POST /api/sessions`

**Action**: Добавить endpoint в `core/app.py`.

**Логика**:
1. Найти пак в `registry` — 404 если не найден
2. Вызвать `pool_manager.allocate(pack_id)` — 503 если `None`
3. Получить `ttl_sec` из `pack.pool.session_timeout_sec`
4. Вызвать `create_token(container_id, pack_id, ttl_sec, exercise_id)`
5. Вернуть `SessionResponse`

**Implementation**:
```python
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import HTTPException
from .session import create_token

@app.post("/api/sessions", response_model=SessionResponse, status_code=200)
async def create_session(body: SessionRequest):
    pack = registry.get(body.pack_id)
    if pack is None:
        raise HTTPException(status_code=404, detail="Pack not found")

    container_id = await pool_manager.allocate(body.pack_id)
    if container_id is None:
        raise HTTPException(
            status_code=503,
            detail={"error": "no_capacity"},
        )

    ttl_sec = pack.pool.session_timeout_sec
    token = create_token(container_id, body.pack_id, ttl_sec, body.exercise_id)
    expires_at = (
        datetime.now(timezone.utc) + timedelta(seconds=ttl_sec)
    ).isoformat()

    return SessionResponse(
        session_token=token,
        ws_url=f"/ws/{token}",
        expires_at=expires_at,
    )
```

**Проверить наличие `session_timeout_sec` в `PackConfig`**: если его нет в `pack_registry.py`, добавить в модель `PoolConfig` со значением по умолчанию `3600`.

**Verification**:
- [ ] `POST /api/sessions {"pack_id": "rustlings"}` → 200 с `session_token`, `ws_url`, `expires_at`
- [ ] `POST /api/sessions {"pack_id": "nonexistent"}` → 404
- [ ] При пустом пуле (pool.size=0 или все контейнеры busy) → 503 `{"error": "no_capacity"}`

**Success Criteria**:
- ✅ Возвращает валидный JWT в `session_token`
- ✅ `ws_url` содержит токен
- ✅ 503 при отсутствии свободных контейнеров

---

### Step 2.3: Реализовать `DELETE /api/sessions/{token}`

**Action**: Добавить endpoint для явного завершения сессии.

**Логика**:
1. Вызвать `verify_token(token)` — 400 если `None`
2. Вызвать `pool_manager.release(pack_id, container_id)`
3. Вернуть 204

**Implementation**:
```python
from .session import verify_token

@app.delete("/api/sessions/{token}", status_code=204)
async def delete_session(token: str):
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    await pool_manager.release(payload.pack_id, payload.container_id)
```

**Verification**:
- [ ] `DELETE /api/sessions/{valid_token}` → 204
- [ ] `DELETE /api/sessions/garbage` → 400
- [ ] После `DELETE` контейнер уничтожен, пул пополняется

**Success Criteria**:
- ✅ 204 при валидном токене
- ✅ 400 при невалидном токене
- ✅ Контейнер освобождается через `pool_manager.release`

---

### Step 2.4: Проверить `session_timeout_sec` в `pack_registry.py`

**Action**: Убедиться, что модель `PoolConfig` содержит `session_timeout_sec`.

**Implementation**: Проверить `core/pack_registry.py`. Если поле отсутствует — добавить:
```python
class PoolConfig(BaseModel):
    size: int = 3
    session_timeout_sec: int = 3600
```

**Verification**:
- [ ] `pack.pool.session_timeout_sec` доступно для паков с и без явного поля в `pack.json`

---

## Testing Plan

### Manual Tests (curl / httpie)
```bash
# Запустить TPS
uvicorn core.app:app --reload

# Создать сессию
curl -X POST http://localhost:8080/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"pack_id": "rustlings", "exercise_id": "intro1"}'
# Ожидаем: 200 {"session_token": "...", "ws_url": "/ws/...", "expires_at": "..."}

# Завершить сессию
curl -X DELETE http://localhost:8080/api/sessions/{token}
# Ожидаем: 204

# Несуществующий пак
curl -X POST http://localhost:8080/api/sessions \
  -d '{"pack_id": "unknown"}'
# Ожидаем: 404
```

### OpenAPI Docs
- [ ] Endpoints отображаются на `/docs` с корректными схемами

## Rollback Plan

Новые endpoints добавляются к существующему `app.py`, старый `/ws` endpoint не затрагивается. При проблемах — удалить новые роуты, сервис продолжит работу.

## Definition of Done

- [ ] `POST /api/sessions` → 200 с JWT при наличии warm-контейнера
- [ ] `POST /api/sessions` → 503 при пустом пуле
- [ ] `POST /api/sessions` → 404 при неизвестном `pack_id`
- [ ] `DELETE /api/sessions/{token}` → 204 и освобождение контейнера
- [ ] `DELETE /api/sessions/{token}` → 400 при невалидном токене
- [ ] `session_timeout_sec` доступен в `PoolConfig`
- [ ] Endpoints видны в `/docs`
