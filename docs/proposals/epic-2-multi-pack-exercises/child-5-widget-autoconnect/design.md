# Child 5: Виджет — Автоподключение

**Type**: Issue
**Status**: Planned
**Epic**: Epic #2
**Blocked by**: —

## Problem Statement

Текущий виджет требует ручного нажатия кнопки "Launch Terminal". Для учебной платформы
нужно, чтобы сессия стартовала автоматически в момент открытия задания — пользователь
кликает на упражнение и сразу видит терминал с заданием.

## Solution Overview

Убрать состояние `idle` и кнопку "Launch Terminal". При монтировании виджет сразу
вызывает `requestSession()`. Кнопка "Terminate Session" остаётся — пользователь
должен иметь возможность завершить сессию явно.

## State Machine Changes

**Было**: `idle → loading → connected → terminated`

**Стало**: `loading → connected → terminated`

Состояния `no_capacity` и `error` сохраняются — пользователь может повторить попытку.

```
mount()
  └── requestSession()   ← сразу при монтировании
        ├── 503 → no_capacity  (кнопка "Попробовать снова")
        ├── error → error      (кнопка "Повторить")
        └── ok → loading → connected
                                └── terminate button
                                      └── terminated (кнопка "Открыть снова")
```

## UI Changes

| Состояние | Было | Стало |
|-----------|------|-------|
| `idle` | кнопка "Launch Terminal" | **удалено** |
| `loading` | кнопка "Connecting…" (disabled) | без изменений |
| `connected` | кнопка "Terminate Session" | без изменений |
| `no_capacity` | кнопка "Launch Terminal" + сообщение | кнопка "Попробовать снова" + сообщение |
| `error` | кнопка "Retry" + сообщение | без изменений |
| `terminated` | кнопка "Launch Terminal" + сообщение | кнопка "Открыть снова" + сообщение |

## Implementation

В `widget/src/widget.js`:

1. Удалить `case 'idle'` из `render()`
2. В конце `mount()` вместо `render()` вызвать `requestSession()`
3. Переименовать текст кнопок для `no_capacity` и `terminated` (см. таблицу)
4. Убрать проверку `state === 'idle'` из обработчика клика кнопки

После изменений — пересобрать бандл:
```bash
cd widget && npm run build:dev
```

Обновить cache-buster в `templates/index.html`: `?v=N+1`

## Definition of Done

- [ ] Виджет стартует сессию автоматически при монтировании
- [ ] Состояния `no_capacity`, `error`, `terminated` с кнопкой повтора работают корректно
- [ ] Кнопка "Terminate Session" завершает сессию
- [ ] Бандл пересобран, cache-buster обновлён
