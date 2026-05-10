# Прогресс: Epic #2 — Мульти-пак и упражнения

## Дашборд

```mermaid
graph TD
    subgraph "Epic #2: Multi-Pack & Exercises"
        A["Child 1\nExercise Infrastructure"] -->|unlocks| B["Child 2\nPack: Bash"]
        A --> C["Child 3\nPack: Python"]
        A --> D["Child 4\nPack: Go"]
        B --> F["Child 6\nList Page"]
        C --> F
        D --> F
        E["Child 5\nWidget Auto-connect"] --> F
        G["Child 7\nCORS Config"]
    end

    style A fill:#c8e6c9,stroke:#2e7d32
    style B fill:#c8e6c9,stroke:#2e7d32
    style C fill:#c8e6c9,stroke:#2e7d32
    style D fill:#c8e6c9,stroke:#2e7d32
    style E fill:#c8e6c9,stroke:#2e7d32
    style F fill:#c8e6c9,stroke:#2e7d32
    style G fill:#c8e6c9,stroke:#2e7d32
```

## Сводка по child issues

| Child | Название | Статус | Прогресс |
|-------|----------|--------|----------|
| Child 1 | Exercise Infrastructure | ✅ Выполнен | 100% |
| Child 2 | Pack: Bash | ✅ Выполнен | 100% |
| Child 3 | Pack: Python | ✅ Выполнен | 100% |
| Child 4 | Pack: Go | ✅ Выполнен | 100% |
| Child 5 | Виджет: автоподключение | ✅ Выполнен | 100% |
| Child 6 | Главная страница | ✅ Выполнен | 100% |
| Child 7 | CORS конфиг | ✅ Выполнен | 100% |

## Метрики

- **Общий прогресс**: 100% (7/7 child issues завершены)
- **Начат**: 2026-05-10
- **Реализован**: 2026-05-10

## Ручные шаги для деплоя

- [ ] `docker build -t tps-python packs/python/`
- [ ] `docker build -t tps-go packs/go/`
- [ ] Перезапустить сервис: `sudo systemctl restart tps`
- [ ] Проверить `GET /api/packs` — bash/python/go с exercises
- [ ] Открыть `GET /` — список упражнений по курсам
- [ ] Кликнуть упражнение → терминал открывается → `check` работает
