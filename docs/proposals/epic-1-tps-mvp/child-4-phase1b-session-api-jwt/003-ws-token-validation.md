# Stage 3: WS Token Validation

**Objective**: Заменить старый `/ws` endpoint на `/ws/{token}`, добавить JWT-валидацию, привязать WS к конкретному контейнеру из пула, обеспечить автоматическое завершение сессии по TTL.
**Duration**: ~1-2 часа
**Dependencies**: Stage 1 и Stage 2 завершены

## Detailed Steps

### Step 3.1: Обновить `ws_proxy.py` — принимать `container_id`

**Action**: Рефакторинг `handle_ws` — убрать логику `_get_or_create_container`, принимать `container_id` снаружи.

**Текущее состояние**: `handle_ws(websocket)` сам находит или создаёт контейнер через `settings.tps_container_name`.

**Целевое состояние**: `handle_ws(websocket, container_id)` подключается к уже существующему контейнеру из пула.

**Implementation**:
```python
# core/ws_proxy.py

async def handle_ws(websocket: WebSocket, container_id: str) -> None:
    """Handle a WebSocket connection: bridge browser ↔ Docker PTY.

    Args:
        websocket: FastAPI WebSocket connection.
        container_id: ID of the pre-allocated warm container from the pool.
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

        # ... остальная логика container_to_ws / ws_to_container без изменений ...
```

Удалить функцию `_get_or_create_container` — она больше не нужна.

**Verification**:
- [ ] `handle_ws(websocket, container_id)` подключается к конкретному контейнеру
- [ ] Резайз терминала работает (логика `ws_to_container` не изменилась)

**Success Criteria**:
- ✅ WS подключается к контейнеру по его ID
- ✅ Функция `_get_or_create_container` удалена

---

### Step 3.2: Заменить `/ws` на `/ws/{token}` в `app.py`

**Action**: Удалить старый endpoint `/ws`, добавить новый `/ws/{token}` с JWT-валидацией.

**Логика нового endpoint**:
1. Вызвать `verify_token(token)` — закрыть WS с кодом 4401 если `None`
2. Проверить, что `payload.container_id` присутствует
3. Вычислить оставшийся TTL = `payload.exp - now`
4. Передать `container_id` в `handle_ws`
5. Установить таймаут: по истечении TTL закрыть WS и вызвать `release`

**Implementation**:
```python
# core/app.py
import time
from fastapi import WebSocket
from .session import verify_token

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
        logger.info(
            "Session TTL expired for container %s.", payload.container_id[:12]
        )
        try:
            await websocket.close(code=4401)
        except Exception:
            pass
    finally:
        await pool_manager.release(payload.pack_id, payload.container_id)
```

**Важно**: Старый `@app.websocket("/ws")` — удалить.

**Verification**:
- [ ] WS по `ws://localhost:8080/ws/{valid_token}` — подключение успешно
- [ ] WS по `ws://localhost:8080/ws/garbage` — соединение закрывается с кодом 4401
- [ ] WS по истёкшему токену — закрывается с кодом 4401
- [ ] После закрытия WS контейнер уничтожается, пул пополняется

**Success Criteria**:
- ✅ Только валидный токен открывает WS
- ✅ Код закрытия 4401 при отказе
- ✅ `release` вызывается в `finally` при любом завершении

---

### Step 3.3: Обновить `templates/index.html` (демо-страница)

**Action**: Обновить демо-страницу — теперь для открытия WS нужно сначала получить токен через `POST /api/sessions`.

**Логика JS на демо-странице**:
```javascript
// 1. Получить токен
const resp = await fetch('/api/sessions', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ pack_id: 'rustlings' }),
});
if (resp.status === 503) { alert('Нет свободных ресурсов'); return; }
const { session_token, ws_url } = await resp.json();

// 2. Открыть WS
const ws = new WebSocket(`ws://localhost:8080${ws_url}`);
```

**Verification**:
- [ ] Демо-страница открывает терминал через токен
- [ ] При 503 — показывает сообщение пользователю

**Success Criteria**:
- ✅ Демо работает end-to-end: кнопка → токен → WS → терминал

---

## Testing Plan

### End-to-end Test (manual)
```bash
# 1. Запустить TPS
uvicorn core.app:app --reload --port 8080

# 2. Получить токен
TOKEN=$(curl -s -X POST http://localhost:8080/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"pack_id": "rustlings"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['session_token'])")

echo "Token: $TOKEN"

# 3. Подключиться к WS (websocat)
websocat ws://localhost:8080/ws/$TOKEN

# Ожидаем: интерактивный bash внутри контейнера

# 4. Проверить отклонение невалидного токена
websocat ws://localhost:8080/ws/invalid-token
# Ожидаем: соединение закрыто с кодом 4401
```

### Проверка TTL (опционально)
```bash
# Создать токен с TTL=5 сек (изменить временно session_timeout_sec в pack.json)
# Подключиться → через 5 сек WS должен закрыться автоматически
```

## Rollback Plan

Если потребуется откат — восстановить старый `@app.websocket("/ws")` без токена и старый `handle_ws(websocket)` без `container_id`. Это возможно через `git revert` коммита Stage 3.

## Definition of Done

- [ ] `handle_ws` принимает `container_id`, `_get_or_create_container` удалена
- [ ] `GET /ws/{valid_token}` открывает WS к нужному контейнеру
- [ ] `GET /ws/{invalid_token}` → закрытие с кодом 4401
- [ ] `GET /ws/{expired_token}` → закрытие с кодом 4401
- [ ] После завершения WS-сессии (нормально или по TTL) → `release` вызван
- [ ] Старый `/ws` endpoint удалён
- [ ] Демо-страница работает с новым flow (токен → WS)
