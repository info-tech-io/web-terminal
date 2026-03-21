# Child #6 (Phase 1-D): JS Widget v1 + Demo Page

**Type**: Large Issue
**Status**: Planned
**Issue**: [#6](https://github.com/info-tech-io/web-terminal/issues/6)
**Epic**: [#1](https://github.com/info-tech-io/web-terminal/issues/1)
**Blocked by**: Child #3 (Pool Manager), Child #4 (Session API), Child #5 (Pack rustlings)

## Problem Statement

TPS должен быть встраиваемым — одним тегом `<script>` на любую страницу.
Нужен виджет, который самостоятельно управляет UX: кнопка запуска, состояния, xterm.js,
WebSocket-соединение, завершение сессии.

## Solution Overview

Самодостаточный JS-бандл (`widget.js`) без внешних зависимостей в рантайме.
xterm.js подключается как npm-зависимость и бандлится внутрь.

### Embed API

```html
<script src="https://terminal.infotecha.ru/widget.js"
        data-pack="rustlings"
        data-exercise="intro1"
        data-tps-url="https://terminal.infotecha.ru">
</script>
```

## Widget States

```
idle → loading → connected → terminated
            ↘ error
            ↘ no_capacity
```

## Architecture

```
widget.js
  ├── mount()           — найти placeholder, создать DOM
  ├── requestSession()  — POST /api/sessions
  ├── connect(token)    — открыть WS + xterm.js
  ├── resize()          — отправить resize по WS
  └── terminate()       — DELETE /api/sessions/{token}
```

## Implementation Stages

### Stage 1: Widget core (`widget/src/widget.js`)
- State machine: idle → loading → connected/error/no_capacity
- `requestSession()` → `POST /api/sessions`
- xterm.js + WebSocket
- `beforeunload` → `terminate()`

### Stage 2: Build pipeline
- esbuild: `widget/src/widget.js` → `widget/widget.js`
- Поддержка `data-*` атрибутов
- Serve через FastAPI `StaticFiles`

### Stage 3: Demo page + GitHub Pages
- Обновить `templates/index.html` с виджетом
- Настроить GitHub Pages (папка `docs/` или отдельная ветка)
- Задокументировать деплой в README

## Definition of Done

- [ ] Виджет встраивается одним `<script>` тегом
- [ ] Кнопка → терминал открывается ≤ 3 сек (warm container)
- [ ] Все состояния (загрузка, нет ресурсов, ошибка) отображаются
- [ ] Демо-страница работает на GitHub Pages
- [ ] `beforeunload` корректно завершает сессию
