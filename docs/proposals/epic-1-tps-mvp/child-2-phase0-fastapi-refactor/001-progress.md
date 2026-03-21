# Stage 1 Progress Report: FastAPI Migration + Config

**Status**: ✅ Complete
**Started**: 2026-03-21
**Completed**: 2026-03-21

## Summary

Flask + gevent заменён на FastAPI + uvicorn. Конфиг вынесен в Pydantic Settings (.env).
Создана структура `core/` и `packs/`. Старый `app.py` удалён. Добавлен resize-протокол.

## Completed Steps

### Step 1.1: Dependencies
- **Status**: ✅ Complete
- **Result**: `requirements.txt` обновлён — flask/gevent/flask-sock удалены, fastapi/uvicorn/pydantic-settings добавлены

### Step 1.2: `core/config.py`
- **Status**: ✅ Complete
- **Result**: Pydantic Settings с `TPS_IMAGE_NAME`, `TPS_CONTAINER_NAME`, `TPS_HOST`, `TPS_PORT`

### Step 1.3: `core/ws_proxy.py`
- **Status**: ✅ Complete
- **Result**: Async WS↔PTY bridge с поддержкой resize JSON-сообщений

### Step 1.4: `core/app.py`
- **Status**: ✅ Complete
- **Result**: FastAPI app, `GET /`, `WS /ws`, startup hook для сборки образа

### Step 1.5: `.env.example` + `Dockerfile.tps`
- **Status**: ✅ Complete
- **Result**: Задокументированы переменные окружения; TPS-сервис собирается через `Dockerfile.tps`

### Stage 2 (resize) + Stage 3 (structure): Combined
- **Status**: ✅ Complete
- **Result**: `templates/index.html` отправляет resize по WS; `core/`, `packs/rustlings/` созданы; `app.py` удалён

## Test Results

| Test | Status |
|------|--------|
| `python3 -c "from core.app import app"` | ✅ OK |

## Next Steps

- Child #3 (Phase 1-A): Pack Registry + Pool Manager + Redis
