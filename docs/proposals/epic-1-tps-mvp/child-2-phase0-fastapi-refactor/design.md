# Child #2 (Phase 0): FastAPI Migration + Refactor Prototype

**Type**: Large Issue
**Status**: In Progress
**Issue**: [#2](https://github.com/info-tech-io/web-terminal/issues/2)
**Epic**: [#1](https://github.com/info-tech-io/web-terminal/issues/1)

## Problem Statement

Прототип (`app.py`) — монолит 137 строк на Flask + gevent с хардкодом имён `gemini-*`,
без конфига, без ресайза терминала и без структуры директорий для будущих компонентов TPS.

Конкретные проблемы:
1. Flask + gevent monkey-patching — хрупкий способ получить async; FastAPI + uvicorn решает это нативно
2. `DOCKER_IMAGE_NAME = "gemini-terminal-box"` — хардкод, мешает конфигурации и тестированию
3. Нет обработки resize-сообщений от клиента — терминал не реагирует на изменение размера окна
4. Всё в одном файле — невозможно добавить Pool Manager, Session, Pack Registry без хаоса

## Solution Overview

### Stage 1: FastAPI migration + config

Заменить Flask + flask-sock + gevent на FastAPI + uvicorn. Вынести конфиг в `.env`.
Результат: сервис поднимается командой `uvicorn core.app:app`, WebSocket работает.

### Stage 2: Terminal resize (SIGWINCH)

Добавить протокол resize-сообщений между клиентом и PTY.
Клиент отправляет JSON `{"type":"resize","cols":N,"rows":M}` перед данными.
Сервер вызывает `docker_client.api.exec_resize(exec_id, cols=N, rows=M)`.

### Stage 3: Directory structure `core/` + `packs/`

Разбить монолит на модули согласно целевой структуре roadmap:
- `core/app.py` — FastAPI app, роуты
- `core/ws_proxy.py` — WebSocket ↔ PTY мост (текущий код `app.py`)
- `core/config.py` — загрузка настроек из `.env`
- `packs/rustlings/` — placeholder для Phase 1-C

## Technical Decisions

### Почему FastAPI + uvicorn вместо Flask + gevent

| Аспект | Flask + gevent | FastAPI + uvicorn |
|--------|---------------|-------------------|
| WebSocket | flask-sock поверх gevent | Нативный, встроен в Starlette |
| Async | monkey-patching (хрупко) | Нативный asyncio |
| Config | нет стандарта | Pydantic Settings |
| OpenAPI | нет | Встроен (`/docs`) |
| Performance WS | ограничен gevent | Лучше при N > 10 соединений |

### Протокол resize

Клиент (xterm.js) при событии `onResize` отправляет по WS:
```json
{"type": "resize", "cols": 220, "rows": 50}
```
Все остальные сообщения — бинарные или строки с данными PTY.

### Config через Pydantic Settings

```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    tps_image_name: str = "tps-base"
    tps_container_name: str = "tps-instance"
    tps_host: str = "0.0.0.0"
    tps_port: int = 8080

    class Config:
        env_file = ".env"
```

## Implementation Stages

### Stage 1: FastAPI migration + config
- **Objective**: Заменить Flask на FastAPI, вынести конфиг
- **Deliverables**: `core/app.py`, `core/config.py`, `core/ws_proxy.py`, `.env.example`, `requirements.txt`
- **Success Criteria**: `uvicorn core.app:app` запускает сервис, терминал работает

### Stage 2: Terminal resize
- **Objective**: Поддержка ресайза PTY
- **Deliverables**: Обновлённый `core/ws_proxy.py`, обновлённый `templates/index.html`
- **Success Criteria**: Изменение размера окна браузера меняет размер PTY

### Stage 3: Directory structure
- **Objective**: Создать скелет будущей архитектуры
- **Deliverables**: `packs/rustlings/.gitkeep`, `core/__init__.py`, обновлённый `Dockerfile`
- **Success Criteria**: Структура соответствует целевой из roadmap

## Dependencies

- Нет внешних зависимостей (это первый Child в Epic)

## Testing Strategy

- Ручной тест: `uvicorn core.app:app --reload`, открыть браузер, набрать команды в терминале
- Ручной тест resize: изменить размер окна браузера, убедиться что `tput cols` отдаёт правильное значение
