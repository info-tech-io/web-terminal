# Child 3: Pack — Python

**Type**: Issue
**Status**: Planned
**Epic**: Epic #2
**Blocked by**: Child 1 (Exercise Infrastructure)

## Problem Statement

Пака Python не существует. Нужно создать Docker-образ на базе `python:3.12-alpine`,
написать скрипты и три упражнения.

## Dockerfile

```dockerfile
FROM python:3.12-alpine

RUN pip install --no-cache-dir pytest

WORKDIR /workspace
CMD ["/bin/bash"]
```

Базовый образ `python:3.12-alpine` ~55 МБ. `pytest` — единственная дополнительная
зависимость (нужна для упражнений типа `function` и `multi-file`).

## Exercises

### py-expr-01 — Single Expression
**Тип**: `single-expression`
**Курс**: `python-basics`
**Задание**: Используя list comprehension, создай список квадратов нечётных чисел
от 1 до 20 и выведи его на экран.

**Ожидаемый вывод**: `[1, 9, 25, 49, 81, 121, 169, 225, 289, 361]`

**check.sh**: запускает `solution.py`, сравнивает stdout с `expected_output.txt`

**Workspace**:
```
solution.py         # print(...)  ← TODO
expected_output.txt
```

---

### py-func-01 — Function
**Тип**: `function`
**Курс**: `python-basics`
**Задание**: Реализуй функцию `is_palindrome(s: str) -> bool`, которая возвращает
`True` если строка является палиндромом (регистр игнорируется, пробелы учитываются).

**check.sh**: запускает pytest, выводит результат

**Workspace**:
```
solution.py         # def is_palindrome(s): ...  ← TODO
tests/
  test_solution.py  # 6 тест-кейсов (racecar, hello, Madam, пустая строка и др.)
```

---

### py-multi-01 — Multi-File
**Тип**: `multi-file`
**Курс**: `python-basics`
**Задание**: Создай модуль `calculator.py` с четырьмя функциями: `add`, `subtract`,
`multiply`, `divide`. Функция `divide` должна выбрасывать `ValueError` при делении
на ноль.

**check.sh**: запускает pytest, выводит результат

**Workspace**:
```
calculator.py       # TODO: реализуй функции
main.py             # пример использования (для ручного запуска)
tests/
  test_calculator.py  # тесты для всех 4 функций + edge cases
```

---

## Scripts

### init.sh
```bash
#!/bin/bash
# Python pack: verify pytest is available
python3 -c "import pytest" && echo "[init] Python pack ready."
```

### session.sh
Стандартный session.sh из Child 1.

## pack.json

```json
{
  "id": "python",
  "display_name": "Python",
  "description": "Практика на Python",
  "image_tag": "tps-python",
  "pool": { "size": 3, "session_timeout_sec": 3600 },
  "courses": [
    { "id": "python-basics", "label": "Python: основы" }
  ],
  "exercises": [
    { "id": "py-expr-01", "title": "List Comprehension", "course": "python-basics", "type": "single-expression", "difficulty": "easy" },
    { "id": "py-func-01", "title": "Палиндром", "course": "python-basics", "type": "function", "difficulty": "easy" },
    { "id": "py-multi-01", "title": "Калькулятор", "course": "python-basics", "type": "multi-file", "difficulty": "medium" }
  ]
}
```

## Implementation Stages

### Stage 1: Dockerfile + сборка образа
- [ ] Написать `Dockerfile`
- [ ] Собрать образ `tps-python`

### Stage 2: Scripts
- [ ] Написать `init.sh`
- [ ] Написать `session.sh`

### Stage 3: Exercises
- [ ] `py-expr-01`: task.md, workspace/, check.sh
- [ ] `py-func-01`: task.md, workspace/ (с тестами), check.sh
- [ ] `py-multi-01`: task.md, workspace/ (с тестами), check.sh

### Stage 4: pack.json
- [ ] Создать `pack.json`

### Stage 5: Проверка
- [ ] Запустить сессию с каждым упражнением вручную
- [ ] `check` проходит при верном решении
- [ ] `check` падает при неверном

## Definition of Done

- [ ] Образ `tps-python` собран и доступен локально
- [ ] `init.sh` и `session.sh` работают
- [ ] Все три упражнения открываются корректно
- [ ] `check` работает корректно для каждого типа
- [ ] `pack.json` добавлен в `packs/python/`
