# Stage 3: Replenish Loop + App Integration

**Issue**: [#3](https://github.com/info-tech-io/web-terminal/issues/3)

## What

Интегрировать `PackRegistry` и `PoolManager` в `app.py`:
- Startup: загрузить паки, прогреть пулы, запустить фоновую задачу
- Replenish loop: каждые 5 сек проверять и дополнять пулы

## Startup Sequence

```
1. registry.load_all()
2. pool_manager.set_packs({p.id: p for p in registry.all()})
3. await pool_manager.initialize()        — запустить warm контейнеры
4. asyncio.create_task(pool_manager.replenish_loop())
```

## Config Addition

`packs_dir: Path = Path("packs")` добавляется в `Settings`.

## Decisions

- Период replenish loop: 5 секунд (hardcoded константа)
- `initialize()` не блокирует старт сервера — контейнеры стартуют асинхронно
- Старый `/ws` эндпоинт без токена сохраняется до Child #4 (Session API)
