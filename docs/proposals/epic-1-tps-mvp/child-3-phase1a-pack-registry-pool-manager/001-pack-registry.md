# Stage 1: Pack Registry

**Issue**: [#3](https://github.com/info-tech-io/web-terminal/issues/3)

## What

Реализовать `PackRegistry` — компонент, который сканирует `packs/*/pack.json`,
валидирует через Pydantic и предоставляет API эндпоинты.

## Pydantic Models

```
ExerciseConfig  — одно упражнение (id, label, description)
PoolConfig      — настройки пула (size, session_timeout_sec)
SourceConfig    — репозиторий упражнений (repo, branch, clone_depth)
PackConfig      — полная конфигурация пака
```

## API

```
GET /api/packs              → список всех паков + pool_warm/pool_busy счётчики
GET /api/packs/{pack_id}    → детали пака включая exercises
```

## Decisions

- `PackRegistry` — синглтон, создаётся при старте приложения
- `load_all()` сканирует `settings.packs_dir / "*/pack.json"`
- Сломанный pack.json — логируется warning, пропускается (не роняет сервис)
- `pool_warm` / `pool_busy` в ответе запрашиваются у `PoolManager`
