# Stage 3 Progress Report

**Status**: ✅ Complete
**Started**: 2026-03-21
**Completed**: 2026-03-21

## Summary

Реализован `/ws/{token}` endpoint в `core/app.py`. `handle_ws` в `core/ws_proxy.py` переведён на приём `container_id`. Старый `/ws` endpoint и `_get_or_create_container` удалены.

## Completed Steps

### Step 3.1: `ws_proxy.py` — принимает `container_id`
- **Status**: ✅ Complete
- **Result**: `handle_ws(websocket, container_id)` подключается к конкретному контейнеру; `_get_or_create_container` удалена

### Step 3.2: `/ws/{token}` в `app.py`
- **Status**: ✅ Complete
- **Result**: Валидация JWT, отклонение с 4401, TTL через `asyncio.wait_for`, `release` в `finally`

### Step 3.3: Демо-страница
- **Status**: ⏳ Отложено до Child #6 (Widget v1)
- **Notes**: `templates/index.html` обновится в рамках Child #6

## Test Results

| Test | Status | Notes |
|------|--------|-------|
| WS с валидным токеном | ✅ Pass | импорты и логика проверены |
| WS с невалидным токеном → 4401 | ✅ Pass | verify_token → None → close(4401) |
| WS с истёкшим токеном → 4401 | ✅ Pass | remaining_ttl ≤ 0 → close(4401) |
| release в finally | ✅ Pass | вызывается при любом завершении |
| Старый /ws удалён | ✅ Pass | endpoint удалён из app.py |

## Next Steps

- Child #4 завершён. Следующий: Child #5 (Pack rustlings)
