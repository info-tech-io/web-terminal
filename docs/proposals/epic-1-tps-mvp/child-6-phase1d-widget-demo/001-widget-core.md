# Stage 1: Widget Core

**Issue**: [#6](https://github.com/info-tech-io/web-terminal/issues/6)
**Stage**: 1 of 3

## Goal

Написать `widget/src/widget.js` — самодостаточный JS-модуль с state machine,
управлением сессией через REST API и терминалом через xterm.js + WebSocket.

## Context

TPS API уже реализован (Child #4):
- `POST /api/sessions` → `{ session_token, ws_url, expires_at }` или `503`
- `DELETE /api/sessions/{token}` → завершить сессию
- `WS /ws/{token}` → PTY-поток

Виджет встраивается через `data-*` атрибуты тега `<script>`:
- `data-pack` — обязательный, id пака (например `rustlings`)
- `data-exercise` — опциональный, id упражнения
- `data-tps-url` — base URL сервиса (по умолчанию: `location.origin`)

## State Machine

```
idle
  → (кнопка нажата) → loading
      → (сессия получена, WS открыт) → connected
      → (503 no_capacity) → no_capacity
      → (сетевая ошибка) → error
connected
  → (WS закрыт / TTL истёк) → terminated
  → (пользователь нажал "Завершить") → terminated
```

Каждое состояние меняет UI: текст кнопки, видимость терминала, сообщение об ошибке.

## Tasks

### 1.1 Создать структуру директории

```
widget/
├── src/
│   └── widget.js
└── package.json
```

`package.json` — только зависимости для сборки:
```json
{
  "name": "tps-widget",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "@xterm/xterm": "^5.5.0",
    "@xterm/addon-fit": "^0.10.0"
  },
  "devDependencies": {
    "esbuild": "^0.25.0"
  }
}
```

### 1.2 Реализовать `widget/src/widget.js`

**Инициализация** — при загрузке скрипта:
1. Найти тег `<script>` с `data-pack`
2. Прочитать `data-pack`, `data-exercise`, `data-tps-url`
3. Создать DOM-placeholder рядом со скриптом
4. Рендерить начальное состояние `idle` (кнопка «Запустить терминал»)

**`requestSession()`**:
```
POST {tpsUrl}/api/sessions
Body: { pack_id, exercise_id? }
```
- При успехе → сохранить `session_token`, `ws_url` → перейти в `loading → connected`
- При `503` → перейти в `no_capacity`
- При другой ошибке → перейти в `error`

**`connect(token, ws_url)`**:
- Создать контейнер `<div>` для терминала
- Инициализировать `Terminal` из xterm.js + `FitAddon`
- Открыть `WebSocket` к `{tpsUrl}{ws_url}`
- WS `message` → `term.write(data)`
- `term.onData` → `ws.send(data)`
- Отправить resize-сообщение при открытии и при изменении размера окна:
  ```json
  { "type": "resize", "cols": N, "rows": N }
  ```
- WS `close` / `error` → перейти в `terminated`

**`terminate()`**:
```
DELETE {tpsUrl}/api/sessions/{session_token}
```
- Закрыть WS
- Перейти в `terminated`
- Очистить DOM терминала

**`beforeunload`** → вызвать `terminate()` (через `navigator.sendBeacon` или синхронный `fetch`).

### 1.3 DOM и стили

Минимальный inline CSS внутри виджета (без внешних файлов):
- Контейнер терминала: `width: 100%; height: 400px; background: #1e1e1e`
- Кнопка: стандартная, без зависимостей от фреймворков
- Состояния `no_capacity` и `error`: текстовое сообщение над кнопкой

## File Structure After Stage

```
widget/
├── src/
│   └── widget.js     ← новый файл
└── package.json      ← новый файл
```

## Acceptance Criteria

- [ ] `widget/src/widget.js` существует
- [ ] `widget/package.json` содержит зависимости xterm.js и esbuild
- [ ] State machine покрывает все 5 состояний: `idle`, `loading`, `connected`, `no_capacity`, `error`, `terminated`
- [ ] `requestSession()` делает `POST /api/sessions` с правильным телом
- [ ] `connect()` открывает xterm.js в DOM и пробрасывает WS ↔ PTY
- [ ] `terminate()` вызывает `DELETE /api/sessions/{token}` и закрывает WS
- [ ] `beforeunload` вызывает `terminate()`
- [ ] Resize отправляется как JSON `{ "type": "resize", "cols", "rows" }`
