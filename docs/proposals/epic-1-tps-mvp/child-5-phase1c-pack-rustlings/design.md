# Child #5 (Phase 1-C): Pack `rustlings`

**Type**: Large Issue
**Status**: Planned
**Issue**: [#5](https://github.com/info-tech-io/web-terminal/issues/5)
**Epic**: [#1](https://github.com/info-tech-io/web-terminal/issues/1)
**Blocked by**: Child #2 (Phase 0) — только структура директорий

## Problem Statement

Нужна первая рабочая среда выполнения для TPS. rustlings — 92 упражнения по Rust,
идеальный кандидат для MVP: понятная установка, чёткий список упражнений, популярный инструмент.

## Solution Overview

Pack = Dockerfile (среда) + `pack.json` (метаданные) + `init.sh` + `exercise.sh`.
Исходный код rustlings клонируется в `init.sh` — это позволяет обновлять упражнения
без пересборки образа.

## Files

```
packs/rustlings/
├── pack.json          # метаданные, pool config, список упражнений
├── Dockerfile         # Ubuntu 22.04 + Rust toolchain + rustlings
└── scripts/
    ├── init.sh        # клонирует rustlings в /workspace при старте контейнера
    └── exercise.sh    # переходит к упражнению по $EXERCISE_ID
```

## pack.json Structure

```json
{
  "id": "rustlings",
  "display_name": "Rustlings",
  "description": "92 упражнения для изучения Rust",
  "image_tag": "tps-rustlings",
  "pool": {
    "size": 3,
    "session_timeout_sec": 3600
  },
  "source": {
    "repo": "https://github.com/rust-lang/rustlings",
    "branch": "main",
    "clone_depth": 1
  },
  "exercises": [ ... ]
}
```

## Implementation Stages

### Stage 1: Dockerfile + pack.json
- Dockerfile: Ubuntu 22.04, rustup, cargo install rustlings
- pack.json: полный список всех 92 упражнений

### Stage 2: init.sh + exercise.sh
- `init.sh`: git clone rustlings в `/workspace`, `rustlings init`
- `exercise.sh`: `cd /workspace/rustlings && rustlings run $EXERCISE_ID || exec bash`

### Stage 3: Build + smoke test
- `docker build -t tps-rustlings packs/rustlings/`
- Запустить контейнер вручную, проверить `rustlings run intro1`

## Definition of Done

- [ ] `docker build -t tps-rustlings packs/rustlings/` проходит без ошибок
- [ ] `init.sh` клонирует репозиторий и инициализирует rustlings
- [ ] `exercise.sh intro1` открывает первое упражнение
- [ ] `pack.json` содержит все 92 упражнения с корректными ID
