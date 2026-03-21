# Stage 2: Pool Manager (InMemoryStore)

**Issue**: [#3](https://github.com/info-tech-io/web-terminal/issues/3)

## What

Реализовать `PoolManager` с абстракцией хранилища состояния пула.

## Storage Abstraction

```
PoolStore (ABC)
  ├── get_all(pack_id)              → dict[container_id, state]
  ├── set_state(pack_id, cid, state)
  ├── remove(pack_id, cid)
  └── allocate_warm(pack_id)        → container_id | None  (atomic)

InMemoryStore(PoolStore)
  └── asyncio.Lock — гарантирует атомарность allocate_warm
```

Позднее `RedisStore(PoolStore)` подключается без изменений в `PoolManager`.

## PoolManager Interface

```
allocate(pack_id)             → container_id | None
release(pack_id, container_id)
warm_count(pack_id)           → int
busy_count(pack_id)           → int
initialize()                  → прогрев при старте
replenish_loop()              → фоновая задача asyncio
```

## Decisions

- Docker SDK вызовы — через `asyncio.to_thread`
- `_replenish(pack_id)` защищён per-pack asyncio.Lock (не Redis-lock)
- При `allocate` сразу триггерится `_replenish` (не ждать цикла)
- Если образ пака не найден — логируется error, контейнер не создаётся
