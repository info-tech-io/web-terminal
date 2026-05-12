# AI Box — веб-терминал с Claude Code

Браузерный терминал, открывающий доступ к сессии [Claude Code](https://claude.ai/code) прямо из браузера. Работает на [practiciraptor.com/claude](https://practiciraptor.com/claude).

## Архитектура

```
Browser (xterm.js)
      │ WebSocket (wss://)
      ▼
nginx  ──  SSL, subpath /claude
      │ proxy_pass
      ▼
FastAPI + uvicorn  (port 8080 inside container)
      │ PTY (pty.openpty)
      ▼
tmux session "main"
      │
      ▼
Claude Code  (working dir: /root/ai/projects)
```

Всё приложение живёт в одном Docker-контейнере. nginx и секреты — на хосте.

## Стек

| Слой | Технология |
|---|---|
| Frontend | xterm.js + FitAddon |
| Backend | FastAPI + uvicorn |
| Terminal | tmux + PTY |
| AI | Claude Code (claude CLI) |
| Proxy | nginx (SSL, subpath) |

## Деплой

### Требования на хосте
- Docker + Docker Compose
- nginx с SSL

### 1. Секреты

Создайте `~/ai/.env`:

```env
WEB_TOKEN=your_secret_token
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 2. Запуск контейнера

```bash
docker compose up -d
```

Контейнер поднимет uvicorn на `127.0.0.1:8000`.

### 3. nginx

```nginx
location /claude {
    proxy_pass http://127.0.0.1:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
}
```

### Обновление

```bash
docker compose build && docker compose up -d
```

## Навигация в терминале

| Действие | Клавиши |
|---|---|
| Войти в режим скролла | `Ctrl+b [` |
| Скроллить | `↑ ↓` / `Page Up/Down` |
| Выйти из режима скролла | `q` |
