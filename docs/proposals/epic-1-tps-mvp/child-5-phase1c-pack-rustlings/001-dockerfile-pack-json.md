# Stage 1: Dockerfile + pack.json

**Issue**: [#5](https://github.com/info-tech-io/web-terminal/issues/5)
**Stage**: 1 of 3

## Goal

Dockerfile среды выполнения + `pack.json` с полным списком упражнений rustlings.

## Context

Скелет файлов создан в Phase 0 (commit `a5909dd`). Dockerfile содержит Ubuntu 22.04
+ rustup + `cargo install rustlings`. `pack.json` имеет пустой массив `exercises`.

## Tasks

### 1.1 Проверить Dockerfile

Файл уже существует (`packs/rustlings/Dockerfile`). Проверить, что:
- `cargo install rustlings` устанавливает последнюю стабильную версию
- `ENV PATH` включает `~/.cargo/bin`
- Скрипты копируются и получают `chmod +x`

### 1.2 Заполнить pack.json

Добавить полный список всех упражнений rustlings в массив `exercises`.
Каждое упражнение: `{ "id", "label", "description" }`.

Упражнения (по категориям):
- intro: intro1, intro2
- variables: variables1–6
- functions: functions1–5
- if: if1, if2
- quiz1
- primitive_types: primitive_types1–6
- vecs: vecs1–2
- move_semantics: move_semantics1–6
- structs: structs1–3
- enums: enums1–3
- strings: strings1–4
- modules: modules1–3
- hashmaps: hashmaps1–3
- quiz2
- options: options1–3
- errors: errors1–6
- quiz3
- generics: generics1–2
- traits: traits1–5
- tests: tests1–4
- lifetimes: lifetimes1–3
- iterators: iterators1–5
- smart_pointers: arc1, box1, cow1, rc1
- threads: threads1–3
- macros: macros1–4
- clippy: clippy1–3
- conversions: as_ref_mut, from_into, from_str, try_from_into, using_as

## Acceptance Criteria

- [ ] `pack.json` проходит `python3 -c "import json; json.load(open('packs/rustlings/pack.json'))"`
- [ ] Все упражнения содержат поля `id`, `label`, `description`
- [ ] Dockerfile собирается (проверяется в Stage 3)
