# Прогресс Stage 3: Build + Smoke Test

**Статус**: ✅ Завершён
**Дата**: 2026-03-21

## Что было сделано

### Исправления в процессе

**Проблема 1**: Dockerfile не содержал `build-essential` → `cargo install rustlings` падал с ошибкой `linker cc not found`.
**Решение**: добавлен `build-essential` в apt-установку.

**Проблема 2**: `init.sh` клонировал исходный код rustlings (не нужно в v6). В rustlings v6 команда `rustlings init` сама создаёт директорию с упражнениями.
**Решение**: `init.sh` переписан — просто запускает `rustlings init` в `/workspace/`.

### Результаты smoke tests

| Тест | Команда | Результат |
|------|---------|-----------|
| Build | `docker build -t tps-rustlings packs/rustlings/` | ✅ Успешно (2.36 GB) |
| Test 1: init.sh | `docker run --rm tps-rustlings /scripts/init.sh` | ✅ `rustlings ready at /workspace/rustlings` |
| Test 2: структура | `ls /workspace/rustlings/exercises/` | ✅ 26 категорий упражнений |
| Test 3: exercise.sh | `EXERCISE_ID=intro1 /scripts/exercise.sh` | ✅ `✓ Successfully ran intro1` |

### Версия rustlings

Установлена **rustlings v6.5.0** (актуальная). В v6 упражнения организованы по директориям:
```
exercises/
  00_intro/
  01_variables/
  02_functions/
  ...
  25_conversions/
```

Упражнения адресуются по имени файла без префикса: `intro1`, `variables1`, и т.д. — совместимо с нашими ID в `pack.json`.

## Итоговые артефакты

- `packs/rustlings/Dockerfile` — Ubuntu 22.04 + build-essential + rustup + rustlings 6.5.0
- `packs/rustlings/pack.json` — 95 упражнений по 27 категориям
- `packs/rustlings/scripts/init.sh` — `rustlings init` в `/workspace/`
- `packs/rustlings/scripts/exercise.sh` — `rustlings run $EXERCISE_ID` или `bash`
- Образ `tps-rustlings:latest` — собран и проверен
