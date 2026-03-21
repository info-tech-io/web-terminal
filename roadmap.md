# Web Terminal — Архитектурный Роадмап

## Концепция

Единый микросервис **Terminal Pool Service (TPS)** — независимое ядро, которое управляет пулом Docker-контейнеров и пробрасывает к ним WebSocket-сессии из браузера. Ядро не знает ничего о конкретных языках или упражнениях — всё специфичное подключается через **Pack** (пакет среды).

TPS встраивается в любой контекст: статическую страницу на GitHub Pages, Django-платформу, Hugo-сайт — через JS-виджет и REST API.

---

## Архитектура

```
┌──────────────────────────────────────────────────────────┐
│                    Клиент (браузер)                       │
│                                                          │
│   Статика (GitHub Pages / Hugo)   Django-платформа       │
│   ┌──────────────────────────┐   ┌──────────────────┐    │
│   │  <script data-pack=      │   │  Встроенный      │    │
│   │   "rustlings"            │   │  виджет          │    │
│   │   data-exercise="15">    │   │  (авторизован)   │    │
│   └────────────┬─────────────┘   └────────┬─────────┘    │
└────────────────┼────────────────────────--┼──────────────┘
                 │ REST + WebSocket          │
┌────────────────▼───────────────────────---▼──────────────┐
│              Terminal Pool Service (TPS)                  │
│                                                          │
│  ┌─────────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │   Pool Manager  │  │  WS Proxy    │  │  Session &  │ │
│  │                 │  │  (PTY bridge)│  │  Auth       │ │
│  │ - warm pool     │  │              │  │             │ │
│  │ - allocate      │  │ - token      │  │ - JWT       │ │
│  │ - release       │  │   validation │  │ - anon/user │ │
│  │ - replenish     │  │ - stdin/out  │  │ - timeout   │ │
│  └────────┬────────┘  └──────────────┘  └─────────────┘ │
│           │                                              │
│  ┌────────▼────────────────────────────────────────────┐ │
│  │                  Pack Registry                       │ │
│  │  rustlings | go-tour | haskell-ex | bash-basics | …  │ │
│  └─────────────────────────────────────────────────────┘ │
│                          │                               │
│                    Redis (состояние пула)                 │
└──────────────────────────┼───────────────────────────────┘
                           │ Docker API
┌──────────────────────────▼───────────────────────────────┐
│                      Docker Host                          │
│                                                          │
│  Pool: rustlings   Pool: go-tour    Pool: bash-basics     │
│  [ 🟢 ][ 🟢 ][ 🔴 ]  [ 🟢 ][ 🟢 ]    [ 🟢 ][ 🟢 ][ 🟢 ]  │
│  waiting waiting busy  waiting waiting  waiting ...       │
└──────────────────────────────────────────────────────────┘

🟢 = warm (ожидает сессии)   🔴 = busy (идёт сессия)
```

---

## Pack — единица конфигурации среды

Pack — это директория с тремя обязательными компонентами. TPS читает Pack и знает, как собрать образ, прогреть контейнеры и инициализировать сессию.

### Структура

```
packs/
├── rustlings/
│   ├── pack.json          # метаданные и конфигурация пула
│   ├── Dockerfile         # среда выполнения
│   └── scripts/
│       ├── init.sh        # запускается при старте контейнера
│       └── exercise.sh    # запускается при открытии сессии (получает $EXERCISE_ID)
│
├── go-tour/
│   ├── pack.json
│   ├── Dockerfile
│   └── scripts/
│       ├── init.sh
│       └── exercise.sh
│
├── bash-basics/
│   ├── pack.json
│   ├── Dockerfile
│   └── scripts/
│       ├── init.sh
│       └── exercise.sh
│
└── haskell-ex/
    ├── pack.json
    ├── Dockerfile
    └── scripts/
        ├── init.sh
        └── exercise.sh
```

### pack.json

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

  "exercises": [
    { "id": "intro1",   "label": "Intro 1",   "description": "Hello, world!" },
    { "id": "intro2",   "label": "Intro 2",   "description": "Комментарии"   },
    { "id": "variables1", "label": "Variables 1", "description": "Переменные" }
  ]
}
```

Секция `exercises` опциональна — если её нет, виджет просто открывает shell без контекста упражнения.

### Dockerfile пака

Dockerfile пака отвечает только за среду. Исходный код упражнений клонируется в `init.sh` при старте контейнера — это позволяет обновлять упражнения без пересборки образа.

```dockerfile
# packs/rustlings/Dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y curl git && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.cargo/bin:$PATH"
RUN cargo install rustlings

WORKDIR /workspace
CMD ["/bin/bash"]
```

### init.sh и exercise.sh

`init.sh` — выполняется один раз при старте «горячего» контейнера. Клонирует репозиторий, устанавливает зависимости.

`exercise.sh` — выполняется в момент открытия сессии. Получает переменную окружения `$EXERCISE_ID`, переходит к нужному упражнению и запускает интерактивную оболочку.

```bash
# packs/rustlings/scripts/exercise.sh
#!/bin/bash
cd /workspace/rustlings

if [ -n "$EXERCISE_ID" ]; then
    rustlings run "$EXERCISE_ID"
else
    exec bash
fi
```

---

## REST API TPS

```
GET  /api/packs                        → список доступных паков и их состояние
GET  /api/packs/{pack_id}              → детали пака (упражнения, состояние пула)
POST /api/sessions                     → запросить сессию
     body: { pack_id, exercise_id? }
     → { session_token, ws_url, expires_at } | 503 { error: "no_capacity" }
DELETE /api/sessions/{token}           → завершить сессию

WS   /ws/{session_token}              → терминальное соединение
```

Сессионный токен — короткоживущий JWT (TTL = `session_timeout_sec` из pack.json). WS-соединение принимается только при наличии валидного токена. Это закрывает и авторизацию, и защиту от несанкционированного доступа.

---

## JS Виджет

Самодостаточный бандл. Встраивается одним тегом `<script>` на любую страницу — статику, Hugo, Django.

```html
<!-- Минимальный вариант: просто shell -->
<script src="https://terminal.infotecha.ru/widget.js"
        data-pack="rustlings">
</script>

<!-- С конкретным упражнением -->
<script src="https://terminal.infotecha.ru/widget.js"
        data-pack="rustlings"
        data-exercise="intro1">
</script>

<!-- С авторизацией (передаётся JWT от Django) -->
<script src="https://terminal.infotecha.ru/widget.js"
        data-pack="rustlings"
        data-exercise="variables1"
        data-auth-token="{{ user_jwt }}">
</script>
```

Виджет отвечает за:
- кнопку «Запустить терминал» и UX состояний (loading, connected, error, no_capacity)
- запрос сессии у TPS
- управление xterm.js и WebSocket-соединением
- отображение информации об упражнении
- корректное завершение сессии при закрытии страницы

---

## Три режима работы

### Режим 1 — Личная песочница

- Несколько именованных паков (rustlings, go-tour, haskell-ex)
- Аутентификация через токен в конфиге TPS или Basic Auth
- Контейнеры могут быть постоянными (не удаляются после сессии)
- Деплой: один сервер, TPS запущен локально или за nginx

### Режим 2 — Публичный сервис (эфемерный)

- Пул горячих контейнеров фиксированного размера
- Сессия анонимна, контейнер уничтожается после завершения, новый поднимается взамен
- При исчерпании пула — `503 Temporarily Unavailable`
- Деплой: TPS на отдельном сервере, виджет встроен в статику на GitHub Pages

### Режим 3 — Платная подписка

- Авторизованные пользователи идентифицируются JWT, выданным Django-платформой
- TPS получает токен, проверяет тип пользователя, выдаёт ресурс в обход лимита пула
- Персональный Docker Volume монтируется в контейнер — прогресс сохраняется между сессиями
- TPS не управляет пользователями — он только принимает или отклоняет токен

---

## Стек

| Компонент | Технология | Обоснование |
|---|---|---|
| TPS Backend | Python / Flask + Gevent | уже в проекте, gevent решает конкурентность WS |
| Pool State | Redis | атомарные операции для управления пулом |
| Container Runtime | Docker SDK | уже в проекте |
| Widget | Vanilla JS + xterm.js | уже в проекте, без лишних зависимостей |
| Auth (платная подписка) | JWT + Django | Django — часть стека организации |
| Документация | Hugo | уже есть структура в `docs/` |

**Опциональная альтернатива для бэкенда:** FastAPI вместо Flask. Нативный async, встроенный OpenAPI, лучше масштабируется при большом числе WS-соединений. Стоит рассмотреть при переходе к Режиму 2+.

---

## Фазы реализации

### Фаза 0 — Рефакторинг прототипа *(текущее состояние → чистая база)*

- [ ] Переименовать образ и контейнер (убрать `gemini-*`)
- [ ] Вынести конфигурацию (имена, порты) из хардкода в переменные окружения / конфиг-файл
- [ ] Добавить передачу ресайза терминала в PTY контейнера (SIGWINCH)
- [ ] Базовая структура директорий `packs/` и `core/`

### Фаза 1 — Первый Pack: rustlings *(MVP)*

- [ ] Реализовать Pack Registry (чтение `pack.json`)
- [ ] Реализовать Pool Manager для одного пака + Redis
- [ ] Сессионные токены (JWT) на `/api/sessions`
- [ ] Валидация токена на WS-эндпоинте
- [ ] Pack `rustlings`: Dockerfile, `init.sh`, `exercise.sh`, `pack.json` с полным списком упражнений
- [ ] Виджет v1: кнопка запуска, состояния, xterm.js, завершение сессии
- [ ] Демо-страница на GitHub Pages с виджетом

### Фаза 2 — Мульти-пак и публичный сервис

- [ ] Pool Manager для нескольких паков одновременно
- [ ] Pack `bash-basics`
- [ ] Pack `go-tour`
- [ ] Pack `haskell-ex`
- [ ] Виджет: отображение информации об упражнении, список упражнений
- [ ] Обработка `503` и UX «нет свободных ресурсов»
- [ ] CORS и политика встраивания

### Фаза 3 — Авторизация и платная подписка

- [ ] Принятие и верификация JWT от внешней системы (Django)
- [ ] Логика приоритетного доступа (авторизованный пользователь получает контейнер вне очереди)
- [ ] Docker Volumes для сохранения прогресса
- [ ] API для управления volume пользователя (backup, reset)

---

## Структура репозитория (целевая)

```
web-terminal/
├── core/                    # ядро TPS
│   ├── app.py               # Flask-приложение, роуты
│   ├── pool_manager.py      # управление пулом контейнеров
│   ├── session.py           # JWT, жизненный цикл сессии
│   ├── pack_registry.py     # загрузка и валидация паков
│   └── ws_proxy.py          # WebSocket ↔ PTY мост
│
├── packs/                   # среды выполнения
│   ├── rustlings/
│   │   ├── pack.json
│   │   ├── Dockerfile
│   │   └── scripts/
│   │       ├── init.sh
│   │       └── exercise.sh
│   ├── bash-basics/
│   ├── go-tour/
│   └── haskell-ex/
│
├── widget/                  # JS виджет
│   ├── widget.js            # бандл для встраивания
│   └── src/                 # исходники
│
├── docs/                    # документация (Hugo)
│   ├── module.json
│   └── content/
│
├── templates/               # HTML для демо-режима
│   └── index.html
│
├── config.example.yaml      # пример конфигурации TPS
├── requirements.txt
├── Dockerfile               # образ самого TPS-сервиса
├── README.md
└── roadmap.md
```
