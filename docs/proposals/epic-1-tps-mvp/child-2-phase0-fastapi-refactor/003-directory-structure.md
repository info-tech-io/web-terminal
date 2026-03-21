# Stage 3: Directory Structure `core/` + `packs/`

**Objective**: Создать скелет целевой архитектуры TPS
**Issue**: [#2](https://github.com/info-tech-io/web-terminal/issues/2)
**Depends on**: Stage 1

## Detailed Steps

### Step 3.1: Создать структуру `core/`

**Action**: Выделить модули согласно целевой структуре roadmap

**Target structure**:
```
core/
├── __init__.py
├── app.py           # FastAPI app, routes (из Stage 1)
├── config.py        # Settings (из Stage 1)
├── ws_proxy.py      # WS ↔ PTY bridge (из Stage 1)
├── pool_manager.py  # placeholder (Phase 1-A)
├── session.py       # placeholder (Phase 1-B)
└── pack_registry.py # placeholder (Phase 1-A)
```

**Verification**:
- [ ] `python -c "import core.app"` работает

### Step 3.2: Создать структуру `packs/`

**Action**: Создать директорию пака rustlings с заглушками

**Target structure**:
```
packs/
└── rustlings/
    ├── pack.json
    ├── Dockerfile
    └── scripts/
        ├── init.sh
        └── exercise.sh
```

Полное содержимое — в Child #5 (Phase 1-C). Здесь создаём структуру.

**Verification**:
- [ ] Директория `packs/rustlings/scripts/` создана

### Step 3.3: Обновить `Dockerfile` TPS-сервиса

**Action**: CMD изменить с `python app.py` на `uvicorn core.app:app`

**Implementation**:
```dockerfile
CMD ["uvicorn", "core.app:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Verification**:
- [ ] `docker build -t tps-service .` проходит
- [ ] Контейнер TPS стартует и отвечает на `GET /`

### Step 3.4: Удалить старый `app.py`

**Action**: После успешной проверки Stage 1 и Stage 3 — удалить монолит

**Verification**:
- [ ] `app.py` удалён из корня репозитория
- [ ] `git status` не показывает `app.py`

## Definition of Done

- [ ] Структура `core/` и `packs/` соответствует целевой из roadmap
- [ ] TPS-сервис собирается и запускается из Docker
- [ ] Старый `app.py` удалён
