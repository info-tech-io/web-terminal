# Child 1: Exercise Infrastructure

**Type**: Large Issue
**Status**: Planned
**Epic**: Epic #2
**Blocked by**: —

## Problem Statement

TPS не знает об упражнениях: `pack.json` не содержит exercises, `ws_proxy` запускает
голый bash без контекста, нет API для получения метаданных задания.
Нужно заложить инфраструктуру, на которую опираются все паки.

## Solution Overview

1. Расширить схему `pack.json` — добавить `courses` и `exercises`
2. Обновить `PackRegistry` и Pydantic-модели
3. Добавить API endpoint для получения задания
4. Изменить `ws_proxy`: запускать `session.sh` с `$EXERCISE_ID` вместо голого bash
5. Зафиксировать конвенцию структуры директории упражнения

## pack.json Schema (extended)

```json
{
  "id": "python",
  "display_name": "Python",
  "description": "Интерактивный Python-терминал",
  "image_tag": "tps-python",

  "pool": {
    "size": 3,
    "session_timeout_sec": 3600
  },

  "courses": [
    { "id": "python-basics", "label": "Python: основы" },
    { "id": "python-algorithms", "label": "Алгоритмы на Python" }
  ],

  "exercises": [
    {
      "id": "py-expr-01",
      "title": "List Comprehension",
      "course": "python-basics",
      "type": "single-expression",
      "difficulty": "easy",
      "entry_file": "solution.py"
    }
  ]
}
```

## Exercise Directory Structure

```
packs/{lang}/exercises/{exercise_id}/
  ├── meta.json       # дублирует поля из pack.json (для автономного чтения)
  ├── task.md         # текст задания, выводится в терминале при старте
  ├── workspace/      # копируется в ~/exercise/ при старте сессии
  │   ├── solution.py / main.go / script.sh   # шаблон с TODO
  │   └── tests/      # тесты (для типов function и multi-file)
  └── check.sh        # логика проверки, становится командой `check`
```

## session.sh Convention

`session.sh` — единая точка входа при старте любой сессии:

```bash
#!/bin/bash
EXERCISE_DIR="/packs/${PACK_ID}/exercises/${EXERCISE_ID}"

# Если упражнения нет — просто открыть bash
if [ -z "$EXERCISE_ID" ] || [ ! -d "$EXERCISE_DIR" ]; then
    exec bash
fi

# Подготовить workspace
mkdir -p ~/exercise
cp -r "$EXERCISE_DIR/workspace/." ~/exercise/

# Зарегистрировать команду check
install -m 755 "$EXERCISE_DIR/check.sh" /usr/local/bin/check

# Показать задание
echo ""
cat "$EXERCISE_DIR/task.md"
echo ""

# Открыть bash в рабочей директории
cd ~/exercise
exec bash
```

## ws_proxy Changes

`handle_ws` получает `pack_id` и `exercise_id` из JWT payload и передаёт их в
`exec_create` через переменные окружения:

```python
exec_instance = client.api.exec_create(
    container_id,
    ["bash", "/packs/{pack_id}/scripts/session.sh"],
    env=[f"PACK_ID={pack_id}", f"EXERCISE_ID={exercise_id or ''}"],
    stdout=True, stderr=True, stdin=True, tty=True,
)
```

`app.py`: передать `payload.pack_id` и `payload.exercise_id` в `handle_ws`.

## New API Endpoint

```
GET /api/packs/{pack_id}/exercises/{exercise_id}
→ {
    "id": "py-expr-01",
    "title": "List Comprehension",
    "course": "python-basics",
    "type": "single-expression",
    "difficulty": "easy",
    "task": "<содержимое task.md>"
  }
```

## Implementation Stages

### Stage 1: Модели и PackRegistry
- [ ] Pydantic-модели: `CourseConfig`, `ExerciseConfig`
- [ ] Расширить `PackConfig`: поля `courses` и `exercises`
- [ ] `PackRegistry`: читать `exercises/` из директории пака

### Stage 2: API endpoint
- [ ] `GET /api/packs/{pack_id}/exercises/{exercise_id}` — возвращает meta + task.md

### Stage 3: ws_proxy + app.py
- [ ] `handle_ws(websocket, container_id, pack_id, exercise_id)`
- [ ] `exec_create` запускает `session.sh` с env vars вместо голого bash
- [ ] `app.py`: передать pack_id + exercise_id из JWT payload в handle_ws

### Stage 4: session.sh конвенция
- [ ] Задокументировать интерфейс session.sh (env vars, поведение при пустом EXERCISE_ID)
- [ ] Убедиться что скрипт корректно работает без упражнения (fallback to plain bash)

## Definition of Done

- [ ] `GET /api/packs/{pack_id}/exercises/{exercise_id}` возвращает метаданные и текст задания
- [ ] При старте сессии с `exercise_id` — workspace скопирован, `check` доступен, задание напечатано
- [ ] При старте сессии без `exercise_id` — открывается чистый bash (без ошибок)
- [ ] `handle_ws` принимает pack_id + exercise_id
