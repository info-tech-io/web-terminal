# Stage 2: Terminal Resize (SIGWINCH)

**Objective**: Передавать изменения размера окна от клиента в PTY контейнера
**Issue**: [#2](https://github.com/info-tech-io/web-terminal/issues/2)
**Depends on**: Stage 1

## Detailed Steps

### Step 2.1: Протокол resize-сообщений на клиенте

**Action**: При событии `onResize` xterm.js отправлять JSON по WebSocket

**Implementation** (в `templates/index.html`):
```javascript
term.onResize(({ cols, rows }) => {
    if (socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'resize', cols, rows }));
    }
});
```

**Verification**:
- [ ] В DevTools Network → WS видны resize-сообщения при изменении размера окна

### Step 2.2: Обработка resize на сервере

**Action**: В `core/ws_proxy.py` разбирать входящие сообщения: если JSON с `type=resize` — вызывать `exec_resize`, иначе — передавать в PTY

**Implementation**:
```python
import json

async def ws_to_container(websocket, socket_stream, exec_id, docker_client):
    while True:
        data = await websocket.receive_bytes()
        try:
            msg = json.loads(data)
            if msg.get("type") == "resize":
                docker_client.api.exec_resize(
                    exec_id, cols=msg["cols"], height=msg["rows"]
                )
                continue
        except (json.JSONDecodeError, KeyError):
            pass
        await asyncio.to_thread(socket_stream.sendall, data)
```

**Verification**:
- [ ] Сервер не падает при получении resize-сообщения
- [ ] `tput cols` в терминале возвращает актуальное значение после ресайза

### Step 2.3: Начальный resize при подключении

**Action**: Клиент отправляет resize-сообщение сразу после открытия WS-соединения

**Implementation**:
```javascript
socket.onopen = () => {
    socket.send(JSON.stringify({
        type: 'resize',
        cols: term.cols,
        rows: term.rows
    }));
};
```

**Verification**:
- [ ] При первом открытии терминала `tput cols` совпадает с шириной xterm.js

## Testing Plan

1. Открыть терминал
2. Выполнить `tput cols` — должно совпадать с шириной xterm
3. Изменить размер окна браузера
4. Выполнить `tput cols` снова — значение обновилось

## Definition of Done

- [ ] Resize-сообщения обрабатываются без ошибок сервера
- [ ] PTY меняет размер при изменении окна браузера
- [ ] Начальный размер выставляется при подключении
