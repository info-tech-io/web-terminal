# Stage 1: FastAPI Migration + Config

**Objective**: Заменить Flask + gevent на FastAPI + uvicorn, вынести конфиг в `.env`
**Issue**: [#2](https://github.com/info-tech-io/web-terminal/issues/2)

## Detailed Steps

### Step 1.1: Обновить зависимости

**Action**: Заменить Flask-зависимости на FastAPI-стек в `requirements.txt`

**Implementation**:
```
# Убрать:
Flask
flask-sock
gevent

# Добавить:
fastapi
uvicorn[standard]
websockets
pydantic-settings
python-dotenv
```

**Verification**:
- [ ] `pip install -r requirements.txt` проходит без ошибок

### Step 1.2: Создать `core/config.py`

**Action**: Pydantic Settings для всех конфигурируемых параметров

**Implementation**:
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

settings = Settings()
```

**Verification**:
- [ ] `python -c "from core.config import settings; print(settings)"` работает

### Step 1.3: Создать `core/ws_proxy.py`

**Action**: Перенести логику WebSocket ↔ PTY из `app.py` в отдельный модуль

**Implementation**: WS-handler принимает `websocket: WebSocket` из FastAPI,
запускает Docker exec, запускает две asyncio-задачи (container→ws и ws→container).

**Verification**:
- [ ] Модуль импортируется без ошибок

### Step 1.4: Создать `core/app.py`

**Action**: FastAPI-приложение с HTTP-роутом `/` и WS-роутом `/ws`

**Implementation**:
```python
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Terminal Pool Service")
```

**Verification**:
- [ ] `uvicorn core.app:app --reload` запускается
- [ ] Открыть браузер → терминал работает

### Step 1.5: Создать `.env.example` и обновить `Dockerfile`

**Action**: Задокументировать переменные окружения, обновить `CMD` в Dockerfile

**Verification**:
- [ ] `cp .env.example .env && uvicorn core.app:app` работает

## Testing Plan

### Manual Test
1. `uvicorn core.app:app --reload`
2. Открыть `http://localhost:8080`
3. Набрать `echo hello` в терминале → увидеть `hello`
4. Набрать `whoami` → увидеть пользователя контейнера

## Rollback Plan

Старый `app.py` остаётся в корне. При необходимости: `python app.py`.

## Definition of Done

- [ ] `uvicorn core.app:app` запускает сервис
- [ ] Терминал работает в браузере
- [ ] Имена берутся из `.env` / переменных окружения
- [ ] `requirements.txt` обновлён, `gevent` удалён
