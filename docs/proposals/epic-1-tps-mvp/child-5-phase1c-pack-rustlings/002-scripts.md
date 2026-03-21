# Stage 2: init.sh + exercise.sh

**Issue**: [#5](https://github.com/info-tech-io/web-terminal/issues/5)
**Stage**: 2 of 3

## Goal

Скрипты жизненного цикла контейнера: инициализация при старте и переход к упражнению при открытии сессии.

## Context

Оба скрипта созданы в Phase 0 (commit `a5909dd`). Требуется верификация логики.

## Scripts

### init.sh (`packs/rustlings/scripts/init.sh`)

Выполняется один раз при старте «горячего» контейнера:
1. Клонирует `https://github.com/rust-lang/rustlings` в `/workspace/rustlings` (если не существует)
2. Запускает `rustlings init` для инициализации упражнений

### exercise.sh (`packs/rustlings/scripts/exercise.sh`)

Выполняется при открытии сессии пользователем:
- Если `$EXERCISE_ID` установлен → `rustlings run $EXERCISE_ID`
- Если нет → `exec bash` (просто shell в директории /workspace/rustlings)

## Acceptance Criteria

- [ ] `init.sh` идемпотентен (повторный запуск не вызывает ошибок)
- [ ] `exercise.sh` без `$EXERCISE_ID` открывает bash в правильной директории
- [ ] `exercise.sh` с корректным `$EXERCISE_ID` запускает упражнение
