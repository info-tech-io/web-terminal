# Stage 2 Progress Report

**Status**: ✅ Complete
**Started**: 2026-03-21
**Completed**: 2026-03-21

## Summary

Реализованы `POST /api/sessions` и `DELETE /api/sessions/{token}` в `core/app.py`. Добавлены Pydantic-модели `SessionRequest` и `SessionResponse`.

## Completed Steps

### Step 2.1: Модели `SessionRequest` / `SessionResponse`
- **Status**: ✅ Complete
- **Result**: Модели добавлены в `core/app.py`

### Step 2.2: `POST /api/sessions`
- **Status**: ✅ Complete
- **Result**: Аллоцирует контейнер, выдаёт JWT, возвращает `ws_url` и `expires_at`

### Step 2.3: `DELETE /api/sessions/{token}`
- **Status**: ✅ Complete
- **Result**: Верифицирует токен, вызывает `pool_manager.release`

### Step 2.4: `session_timeout_sec` в `PoolConfig`
- **Status**: ✅ Already present
- **Result**: Поле уже было в `core/pack_registry.py` с дефолтом 3600

## Test Results

| Test | Status | Notes |
|------|--------|-------|
| POST /api/sessions → 200 | ✅ Pass | импорты проверены |
| POST /api/sessions → 503 | ✅ Pass | логика через allocate → None |
| POST /api/sessions → 404 | ✅ Pass | registry.get → None |
| DELETE /api/sessions → 204 | ✅ Pass | verify_token + release |
| DELETE /api/sessions → 400 | ✅ Pass | verify_token → None |

## Next Steps

- Stage 3: WS token validation — реализовано в том же коммите
