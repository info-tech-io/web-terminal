# Stage 1 Progress: Widget Core

**Issue**: [#6](https://github.com/info-tech-io/web-terminal/issues/6)
**Stage**: 1 of 3
**Status**: ✅ Complete

## What Was Done

### `widget/package.json`

Создан файл с зависимостями:
- `@xterm/xterm ^5.5.0` + `@xterm/addon-fit ^0.10.0` — терминал в браузере
- `esbuild ^0.25.0` — сборщик бандла
- Скрипты `build` (prod) и `build:dev` (с sourcemap)

### `widget/src/widget.js`

Реализован самодостаточный JS-модуль:

**Bootstrap**: при загрузке скрипта находит тег `<script data-pack="...">`,
читает `data-pack`, `data-exercise`, `data-tps-url`, монтирует DOM-контейнер
рядом со скриптом.

**State machine** (6 состояний):
- `idle` — кнопка «Launch Terminal»
- `loading` — кнопка неактивна, текст «Connecting…»
- `connected` — терминал виден, кнопка «Terminate Session»
- `no_capacity` — сообщение об отсутствии ресурсов, кнопка снова активна
- `error` — сообщение об ошибке, кнопка «Retry»
- `terminated` — терминал скрыт, сессия завершена

**`requestSession()`** — `POST /api/sessions` с `{ pack_id, exercise_id? }`.
Обрабатывает 503 → `no_capacity`, другие ошибки → `error`.

**`connect(wsPath)`** — открывает WebSocket, инициализирует `Terminal` + `FitAddon`,
монтирует в DOM.
- `ws.onmessage` → `term.write(data)`
- `term.onData` → `ws.send(new TextEncoder().encode(data))`
- Resize отправляется как байты: `TextEncoder().encode(JSON.stringify({type:'resize',cols,rows}))`
- `ws.onclose` → переход в `terminated`

**`terminate()`** — закрывает WS, переходит в `terminated`,
отправляет `DELETE /api/sessions/{token}`.

**`terminateBeforeUnload()`** — вызывается при `beforeunload`,
использует `navigator.sendBeacon` для надёжной доставки при закрытии вкладки.

### `.gitignore`

Добавлены записи `widget/widget.js` и `widget/node_modules/`.

## Commits

- `feat(issue-6): Stage 1 — widget core (state machine, xterm.js, WS, session lifecycle)`

## Acceptance Criteria

- [x] `widget/src/widget.js` существует
- [x] `widget/package.json` содержит зависимости xterm.js и esbuild
- [x] State machine покрывает все состояния: `idle`, `loading`, `connected`, `no_capacity`, `error`, `terminated`
- [x] `requestSession()` делает `POST /api/sessions` с правильным телом
- [x] `connect()` открывает xterm.js в DOM и пробрасывает WS ↔ PTY
- [x] `terminate()` вызывает `DELETE /api/sessions/{token}` и закрывает WS
- [x] `beforeunload` вызывает `terminate()` через `sendBeacon`
- [x] Resize отправляется как JSON-байты `{ "type": "resize", "cols", "rows" }`
