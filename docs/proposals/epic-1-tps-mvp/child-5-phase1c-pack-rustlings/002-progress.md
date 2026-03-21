# Stage 2 Progress: init.sh + exercise.sh

**Status**: ✅ Complete
**Date**: 2026-03-21

## What Was Done

Оба скрипта созданы в Phase 0 (commit `a5909dd`) — логика полностью соответствует дизайну.

### init.sh

- Клонирует `https://github.com/rust-lang/rustlings` в `/workspace/rustlings` (если не существует — идемпотентен)
- Запускает `rustlings init` для инициализации
- Выводит: `[init.sh] rustlings ready at /workspace/rustlings`

### exercise.sh

- `$EXERCISE_ID` установлен → `exec rustlings run "$EXERCISE_ID"`
- `$EXERCISE_ID` не установлен → `exec bash` (shell в `/workspace/rustlings`)

## Commits

- `a5909dd feat(phase-0): migrate to FastAPI, add core/ structure and packs/rustlings skeleton`
