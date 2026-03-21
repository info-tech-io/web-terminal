# Child #3 (Phase 1-A): Pack Registry + Pool Manager + Redis

**Type**: Large Issue
**Status**: Planned
**Issue**: [#3](https://github.com/info-tech-io/web-terminal/issues/3)
**Epic**: [#1](https://github.com/info-tech-io/web-terminal/issues/1)
**Blocked by**: Child #2 (Phase 0)

## Problem Statement

TPS должен управлять пулом «горячих» Docker-контейнеров для каждого пака.
Контейнеры должны быть готовы к сессии до её запроса — это исключает задержку старта.

## Solution Overview

### Pack Registry (`core/pack_registry.py`)
Читает `packs/*/pack.json`, валидирует через Pydantic, предоставляет список паков.

### Pool Manager (`core/pool_manager.py`)
Управляет пулом через Redis:
- `warm` — контейнер запущен, ожидает сессии
- `busy` — контейнер занят активной сессией
- Фоновая задача replenish: поддерживает `pool.size` warm-контейнеров

## Architecture

```
Pool Manager
  ├── Redis Hash: tps:pool:{pack_id}
  │     container_id → state (warm|busy)
  │
  ├── allocate(pack_id) → container_id | None
  ├── release(container_id) → удалить + replenish
  └── replenish(pack_id) → запустить новый warm-контейнер
```

## Redis Schema

```
tps:pool:{pack_id}        Hash  { container_id: "warm"|"busy" }
tps:pool:{pack_id}:lock   String  (distributed lock для replenish)
```

## Technical Decisions

- Docker SDK вызовы — через `asyncio.to_thread` (блокирующие)
- Replenish запускается как `asyncio.create_task` при старте TPS
- При старте TPS: если warm < pool.size → запустить недостающие контейнеры

## Implementation Stages

### Stage 1: Pack Registry
- Pydantic-модели для `pack.json`
- `PackRegistry.load_all()` — сканирует `packs/*/pack.json`
- Endpoints `GET /api/packs` и `GET /api/packs/{pack_id}`

### Stage 2: Pool Manager (Redis + Docker)
- `PoolManager.allocate(pack_id)` — атомарно переводит warm → busy
- `PoolManager.release(container_id)` — удаляет контейнер, запускает replenish
- Startup: инициализация пула при старте TPS

### Stage 3: Replenish background task
- `asyncio.create_task(pool_manager.replenish_loop())` при старте
- Период: каждые 5 сек проверять и дополнять пул

## Definition of Done

- [ ] `GET /api/packs` возвращает список паков с `pool_warm` и `pool_busy` счётчиками
- [ ] Pool Manager держит N warm-контейнеров согласно `pack.json`
- [ ] `allocate` возвращает `None` при пустом пуле (→ 503 в Session API)
- [ ] После `release` новый контейнер поднимается автоматически
