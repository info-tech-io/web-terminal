# Child 7: CORS — Вынести в конфиг

**Type**: Issue
**Status**: Planned
**Epic**: Epic #2
**Blocked by**: —

## Problem Statement

CORS origins захардкожены в `core/app.py`:
```python
allow_origins=["https://info-tech-io.github.io"]
```
При добавлении новой площадки (Django-платформа, другой GitHub Pages, Hugo-сайт)
нужно менять код. Должно быть достаточно изменить переменную окружения.

## Solution

### core/config.py
Добавить поле `cors_origins`:

```python
class Settings(BaseSettings):
    ...
    cors_origins: list[str] = ["https://info-tech-io.github.io"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="TPS_",
    )
```

Pydantic v2 умеет парсить `TPS_CORS_ORIGINS='["https://a.com","https://b.com"]'`
как список напрямую.

### core/app.py
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)
```

### .env / systemd
В `tps.service` (Environment= или EnvironmentFile=):
```
TPS_CORS_ORIGINS=["https://info-tech-io.github.io"]
```

## Implementation Stages

- [ ] Добавить `cors_origins: list[str]` в `Settings` в `core/config.py`
- [ ] Обновить `core/app.py`: заменить хардкод на `settings.cors_origins`
- [ ] Добавить `TPS_CORS_ORIGINS` в документацию конфига (или `config.example.yaml`)

## Definition of Done

- [ ] `TPS_CORS_ORIGINS` в окружении управляет списком разрешённых origins
- [ ] При изменении списка — только перезапуск сервиса, не изменение кода
- [ ] Дефолтное значение сохраняет текущее поведение
