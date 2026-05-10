# Child 2: Pack — Bash

**Type**: Issue
**Status**: Planned
**Epic**: Epic #2
**Blocked by**: Child 1 (Exercise Infrastructure)

## Problem Statement

Пак `bash` существует, но без упражнений: нет `init.sh`, `session.sh`, нет директории
`exercises/`. Нужно добавить три упражнения, покрывающих три базовых типа.

## Exercises

### bash-expr-01 — Single Expression
**Тип**: `single-expression`
**Курс**: `bash-scripting`
**Задание**: Найди все файлы с расширением `.sh` в директории `/usr/bin` и выведи их
количество одной командой.

**Ожидаемый вывод**: одно число (количество `.sh` файлов)

**check.sh**: запускает `solution.sh`, сравнивает stdout с `expected_output.txt`

**Workspace**:
```
solution.sh     # #!/bin/bash + TODO: напиши команду
expected_output.txt  # эталонный ответ
```

---

### bash-func-01 — Function / Script
**Тип**: `function`
**Курс**: `bash-scripting`
**Задание**: Напиши скрипт `count_words.sh`, который принимает имя файла как аргумент
и выводит количество слов в нём. Если файл не существует — выводит ошибку в stderr
и завершается с кодом 1.

**check.sh**: запускает скрипт с тестовыми файлами, проверяет stdout и exit code

**Workspace**:
```
count_words.sh        # шаблон с TODO
tests/
  sample.txt          # тестовый файл со словами
  test_count_words.sh # тест-раннер
```

---

### bash-multi-01 — Multi-File
**Тип**: `multi-file`
**Курс**: `bash-scripting`
**Задание**: Создай систему логирования из двух скриптов:
- `log.sh` — принимает сообщение, записывает его с меткой времени в `app.log`
- `tail_log.sh` — выводит последние N строк из `app.log` (N передаётся аргументом,
  по умолчанию 10)

**check.sh**: вызывает оба скрипта, проверяет формат записи и корректность вывода

**Workspace**:
```
log.sh          # шаблон
tail_log.sh     # шаблон
tests/
  test_logging.sh
```

---

## Scripts

### init.sh
Запускается при прогреве контейнера. Для bash-пака достаточно проверить наличие
нужных утилит (wc, find, date — уже есть в ubuntu).

```bash
#!/bin/bash
# Bash pack: no additional setup needed
echo "[init] Bash pack ready."
```

### session.sh
Стандартный session.sh из Child 1 — копирует workspace, регистрирует `check`,
печатает task.md, открывает bash в ~/exercise.

## pack.json (updated)

```json
{
  "id": "bash",
  "display_name": "Bash",
  "description": "Скриптинг на Bash",
  "image_tag": "tps-bash",
  "pool": { "size": 3, "session_timeout_sec": 3600 },
  "courses": [
    { "id": "bash-scripting", "label": "Bash: скриптинг" }
  ],
  "exercises": [
    { "id": "bash-expr-01", "title": "Поиск файлов", "course": "bash-scripting", "type": "single-expression", "difficulty": "easy" },
    { "id": "bash-func-01", "title": "Подсчёт слов", "course": "bash-scripting", "type": "function", "difficulty": "easy" },
    { "id": "bash-multi-01", "title": "Система логирования", "course": "bash-scripting", "type": "multi-file", "difficulty": "medium" }
  ]
}
```

## Implementation Stages

### Stage 1: Scripts
- [ ] Написать `init.sh`
- [ ] Написать `session.sh`

### Stage 2: Exercises
- [ ] `bash-expr-01`: task.md, workspace/, check.sh
- [ ] `bash-func-01`: task.md, workspace/, tests/, check.sh
- [ ] `bash-multi-01`: task.md, workspace/, tests/, check.sh

### Stage 3: pack.json
- [ ] Обновить `pack.json`: добавить courses + exercises

### Stage 4: Проверка
- [ ] Запустить сессию с каждым упражнением вручную
- [ ] Убедиться что `check` проходит при верном решении
- [ ] Убедиться что `check` падает при неверном

## Definition of Done

- [ ] `init.sh` и `session.sh` присутствуют и работают
- [ ] Все три упражнения открываются корректно (workspace + задание в терминале)
- [ ] `check` возвращает успех при правильном решении для каждого упражнения
- [ ] `pack.json` содержит courses и exercises
