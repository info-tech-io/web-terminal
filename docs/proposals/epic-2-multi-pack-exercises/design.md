# Epic #2: Мульти-пак и упражнения

**Type**: Epic
**Status**: Planned
**Epic**: [#2](https://github.com/info-tech-io/web-terminal/issues/)

## Problem Statement

TPS поддерживает один пак (bash) без упражнений. Нужно:
- добавить полноценную систему упражнений с несколькими типами заданий
- поддержать несколько языковых паков (Bash, Python, Go)
- показывать список упражнений на главной странице
- виджет должен автоматически стартовать сессию при открытии задания

## Solution Overview

Единая структура `exercises/` внутри каждого пака. Упражнение — директория с `meta.json`,
`task.md`, `workspace/` (шаблон для пользователя) и `check.sh` (логика проверки).
При старте сессии `ws_proxy` запускает `session.sh` вместо голого bash: скрипт копирует
`workspace/`, выводит задание в терминал и открывает bash. Пользователь проверяет
работу командой `check`.

## Architecture

```
Browser
  └── Exercise List Page (index.html)
        └── click exercise → Widget (auto-connect)
                                  └── POST /api/sessions { pack_id, exercise_id }
                                        └── WS /ws/{token}
                                              └── ws_proxy → exec session.sh $EXERCISE_ID
                                                              └── workspace/ + check + bash

Pack structure:
packs/{lang}/
  ├── Dockerfile
  ├── pack.json            # pool config + courses + exercises metadata
  ├── scripts/
  │   ├── init.sh          # runs at container warm-up
  │   └── session.sh       # runs at session open, receives $EXERCISE_ID
  └── exercises/
      └── {exercise_id}/
          ├── meta.json    # id, title, course, type, difficulty, entry_file
          ├── task.md      # task description (printed in terminal)
          ├── workspace/   # copied to ~/exercise/ at session start
          └── check.sh     # verification logic (becomes `check` command)
```

## Exercise Types

| Type | Description | Verification |
|------|-------------|-------------|
| `single-expression` | Написать выражение/команду, сравнить stdout | `check` сравнивает вывод с `expected_output.txt` |
| `function` | Реализовать функцию, есть тесты | `check` запускает тест-раннер (pytest / go test) |
| `multi-file` | Несколько связанных файлов | `check` запускает тесты рекурсивно |

## Child Issues

| # | Child | Blocks |
|---|-------|--------|
| Child 1 | Exercise Infrastructure | Child 2, 3, 4 |
| Child 2 | Pack: Bash (3 упражнения) | Child 6 |
| Child 3 | Pack: Python (3 упражнения) | Child 6 |
| Child 4 | Pack: Go (3 упражнения) | Child 6 |
| Child 5 | Виджет: автоподключение | Child 6 |
| Child 6 | Главная страница: список упражнений | — |
| Child 7 | CORS: вынести в конфиг | — |

## Execution Order

```
Child 1 (Infrastructure)    Child 7 (CORS)
     │
     ├──► Child 2 (Bash) ────────┐
     ├──► Child 3 (Python) ──────┤──► Child 6 (List Page)
     ├──► Child 4 (Go) ──────────┤
     └──►                        │
                                  │
Child 5 (Widget) ────────────────┘
```

## Definition of Done

- [ ] TPS запускается с тремя паками: bash, python, go
- [ ] Каждый пак имеет 3 упражнения (single-expression, function, multi-file)
- [ ] `check` работает корректно для каждого типа упражнения во всех паках
- [ ] Задание выводится в терминал при старте сессии
- [ ] Главная страница показывает список упражнений по пакам
- [ ] Клик на упражнение → виджет открывается и сессия стартует автоматически
- [ ] CORS origins читаются из переменной окружения
