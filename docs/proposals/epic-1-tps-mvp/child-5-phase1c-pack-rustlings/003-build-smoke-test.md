# Stage 3: Build + Smoke Test

**Issue**: [#5](https://github.com/info-tech-io/web-terminal/issues/5)
**Stage**: 3 of 3

## Goal

Убедиться, что образ собирается и rustlings работает внутри контейнера.

## Build

```bash
docker build -t tps-rustlings packs/rustlings/
```

Ожидаемый результат: образ `tps-rustlings` создан без ошибок.

## Smoke Tests

### Test 1: init.sh

```bash
docker run --rm tps-rustlings /bin/bash /scripts/init.sh
```

Ожидаемый вывод: `[init.sh] rustlings ready at /workspace/rustlings`

### Test 2: exercise.sh без ID (shell mode)

```bash
docker run --rm -it tps-rustlings /bin/bash -c \
  "/bin/bash /scripts/init.sh && exec /bin/bash /scripts/exercise.sh"
```

Ожидаемый результат: открывается bash в `/workspace/rustlings`

### Test 3: exercise.sh с ID

```bash
docker run --rm -it tps-rustlings /bin/bash -c \
  "/bin/bash /scripts/init.sh && EXERCISE_ID=intro1 /bin/bash /scripts/exercise.sh"
```

Ожидаемый результат: rustlings открывает упражнение intro1

## Acceptance Criteria

- [ ] `docker build` проходит без ошибок
- [ ] `init.sh` клонирует репозиторий и выводит финальное сообщение
- [ ] `exercise.sh intro1` открывает упражнение (rustlings run intro1)
- [ ] Размер образа не превышает 3 GB
