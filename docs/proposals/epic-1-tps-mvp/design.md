# Epic #1: TPS MVP — Terminal Pool Service

**Type**: Epic
**Status**: In Progress
**Issue**: [#1](https://github.com/info-tech-io/web-terminal/issues/1)

## Problem Statement

Существующий прототип (`app.py`) — монолит на Flask с хардкодом, без пула контейнеров,
без сессий и без возможности встраивания. Нужно превратить его в самостоятельный микросервис
(Terminal Pool Service), который можно встраивать виджетом на любую страницу.

## Solution Overview

Единый микросервис **TPS** на FastAPI управляет пулом Docker-контейнеров и пробрасывает
к ним WebSocket-сессии. Клиент взаимодействует через REST API и JS-виджет.

## Architecture

```
Browser
  ├── JS Widget (xterm.js)
  │     ├── POST /api/sessions   → session_token + ws_url
  │     └── WS  /ws/{token}      → PTY stream
  │
  └── TPS (FastAPI + uvicorn)
        ├── Pack Registry         packs/*/pack.json
        ├── Pool Manager          Redis ← → Docker API
        └── Session Manager       JWT (short-lived)

Docker Host
  └── Containers: tps-rustlings (warm × N, busy × M)
```

## Tech Stack

| Component | Technology | Reason |
|-----------|-----------|--------|
| Backend | FastAPI + uvicorn | Нативный async, WebSocket, OpenAPI |
| Pool State | Redis | Атомарные операции для управления пулом |
| Container Runtime | Docker SDK | Уже в проекте |
| Widget | Vanilla JS + xterm.js | Уже в проекте, без зависимостей |

## Child Issues

| # | Child | Blocks |
|---|-------|--------|
| [#2](https://github.com/info-tech-io/web-terminal/issues/2) | Phase 0: FastAPI migration + refactor | всё остальное |
| [#3](https://github.com/info-tech-io/web-terminal/issues/3) | Phase 1-A: Pack Registry + Pool Manager + Redis | #4, #6 |
| [#4](https://github.com/info-tech-io/web-terminal/issues/4) | Phase 1-B: Session API (JWT) | #6 |
| [#5](https://github.com/info-tech-io/web-terminal/issues/5) | Phase 1-C: Pack rustlings | #6 |
| [#6](https://github.com/info-tech-io/web-terminal/issues/6) | Phase 1-D: JS Widget v1 + Demo page | — |

## Execution Order

```
#2 (Phase 0)
     │
     ├──► #3 (Pool Manager) ─────┐
     ├──► #4 (Session API)  ─────┤──► #6 (Widget + Demo)
     └──► #5 (Pack rustlings) ───┘
```

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Docker SDK несовместим с async | High | Использовать `asyncio.to_thread` для блокирующих вызовов |
| Redis недоступен при старте | Medium | Health check + graceful degradation в Pool Manager |
| rustlings image большой (>1GB) | Low | Multi-stage build, `.dockerignore` |

## Definition of Done

- [ ] `uvicorn core.app:app` запускает TPS
- [ ] Пул rustlings-контейнеров поддерживается автоматически
- [ ] Браузер открывает терминальную сессию одной кнопкой
- [ ] Контейнер удаляется по завершении сессии, новый поднимается
- [ ] Демо-страница на GitHub Pages работает
