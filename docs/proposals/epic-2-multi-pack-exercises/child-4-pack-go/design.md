# Child 4: Pack — Go

**Type**: Issue
**Status**: Planned
**Epic**: Epic #2
**Blocked by**: Child 1 (Exercise Infrastructure)

## Problem Statement

Пака Go не существует. Нужно создать Docker-образ на базе `golang:1.23-alpine`,
написать скрипты и три упражнения.

## Dockerfile

```dockerfile
FROM golang:1.23-alpine

RUN apk add --no-cache bash

WORKDIR /workspace
CMD ["/bin/bash"]
```

Образ `golang:1.23-alpine` ~260 МБ. Включает полный тулчейн: `go build`, `go test`,
`go run`. Bash добавляется отдельно (alpine по умолчанию использует sh).

## Exercises

### go-expr-01 — Single Expression
**Тип**: `single-expression`
**Курс**: `go-basics`
**Задание**: Выведи таблицу умножения от 1 до 5 в виде:
```
1 x 1 = 1
1 x 2 = 2
...
5 x 5 = 25
```

**check.sh**: `go run main.go`, сравнивает stdout с `expected_output.txt`

**Workspace**:
```
main.go             # package main + func main() { TODO }
expected_output.txt
```

---

### go-func-01 — Function
**Тип**: `function`
**Курс**: `go-basics`
**Задание**: Реализуй функцию `Reverse(s string) string`, которая возвращает
строку в обратном порядке. Функция должна корректно работать с ASCII-строками.

**check.sh**: `go test`, выводит результат

**Workspace**:
```
solution.go         # package main + func Reverse(s string) string { TODO }
solution_test.go    # тесты: "hello"→"olleh", ""→"", "a"→"a" и др.
```

---

### go-multi-01 — Multi-File
**Тип**: `multi-file`
**Курс**: `go-basics`
**Задание**: Создай пакет `mathutils` с тремя функциями для работы со слайсами
целых чисел: `Max(nums []int) int`, `Min(nums []int) int`, `Sum(nums []int) int`.
Каждая функция должна возвращать `0` для пустого слайса.

**check.sh**: `go test ./...`, выводит результат

**Workspace**:
```
mathutils/
  mathutils.go       # package mathutils + TODO функции
  mathutils_test.go  # тесты для каждой функции + edge cases
main.go              # пример использования
```

---

## Scripts

### init.sh
```bash
#!/bin/bash
# Go pack: warm up module cache
go version && echo "[init] Go pack ready."
```

### session.sh
Стандартный session.sh из Child 1.

Особенность для Go: если упражнение содержит `go.mod` — он уже лежит в workspace.
Если нет — session.sh инициализирует модуль:
```bash
cd ~/exercise
[ -f go.mod ] || go mod init exercise
```

## pack.json

```json
{
  "id": "go",
  "display_name": "Go",
  "description": "Практика на Go",
  "image_tag": "tps-go",
  "pool": { "size": 3, "session_timeout_sec": 3600 },
  "courses": [
    { "id": "go-basics", "label": "Go: основы" }
  ],
  "exercises": [
    { "id": "go-expr-01", "title": "Таблица умножения", "course": "go-basics", "type": "single-expression", "difficulty": "easy" },
    { "id": "go-func-01", "title": "Реверс строки", "course": "go-basics", "type": "function", "difficulty": "easy" },
    { "id": "go-multi-01", "title": "Пакет mathutils", "course": "go-basics", "type": "multi-file", "difficulty": "medium" }
  ]
}
```

## Implementation Stages

### Stage 1: Dockerfile + сборка образа
- [ ] Написать `Dockerfile`
- [ ] Собрать образ `tps-go`

### Stage 2: Scripts
- [ ] Написать `init.sh`
- [ ] Написать `session.sh` (с логикой `go mod init` при необходимости)

### Stage 3: Exercises
- [ ] `go-expr-01`: task.md, workspace/ (main.go + expected_output.txt), check.sh
- [ ] `go-func-01`: task.md, workspace/ (solution.go + solution_test.go), check.sh
- [ ] `go-multi-01`: task.md, workspace/ (mathutils/ + main.go + go.mod), check.sh

### Stage 4: pack.json
- [ ] Создать `pack.json`

### Stage 5: Проверка
- [ ] Запустить сессию с каждым упражнением вручную
- [ ] `check` проходит при верном решении
- [ ] `check` падает при неверном

## Definition of Done

- [ ] Образ `tps-go` собран и доступен локально
- [ ] `init.sh` и `session.sh` работают
- [ ] Все три упражнения открываются корректно
- [ ] `check` работает корректно для каждого типа
- [ ] `pack.json` добавлен в `packs/go/`
