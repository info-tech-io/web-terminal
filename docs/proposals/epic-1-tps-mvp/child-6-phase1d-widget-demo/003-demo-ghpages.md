# Stage 3: Demo Page + Public Deployment

**Issue**: [#6](https://github.com/info-tech-io/web-terminal/issues/6)
**Stage**: 3 of 3

## Goal

Поднять TPS на `practiciraptor.com` как публичный API-эндпоинт и опубликовать
статическую демо-страницу на GitHub Pages, которая встраивает виджет,
указывающий на этот эндпоинт.

## Architecture

```
GitHub Pages (статика)                practiciraptor.com (TPS)
┌──────────────────────────┐          ┌──────────────────────────┐
│  docs/demo/index.html    │          │  nginx → uvicorn :8080   │
│                          │  HTTPS   │                          │
│  <script                 │ ───────► │  POST /api/sessions      │
│    data-pack="rustlings" │          │  WS   /ws/{token}        │
│    data-tps-url=         │  WSS     │  GET  /widget/widget.js  │
│    "https://             │ ───────► │                          │
│    practiciraptor.com">  │          │  Docker: tps-rustlings   │
└──────────────────────────┘          └──────────────────────────┘
```

Это точная реализация Режима 2 из roadmap: TPS — независимый микросервис,
виджет встраивается на статическую страницу.

## Context

- `widget/widget.js` собран (Stage 2), отдаётся по `/widget/widget.js`
- На сервере уже работает nginx с SSL (necodate.fun через certbot)
- Домен `practiciraptor.com` делегирован на текущий сервер
- TPS слушает порт `8080` (из `.env.example`)

## Tasks

### 3.1 Собрать Docker-образ rustlings

```bash
docker build -t tps-rustlings packs/rustlings/
```

Образ нужен Pool Manager для запуска «горячих» контейнеров.
Проверка: `docker images | grep tps-rustlings`

### 3.2 Настроить nginx для practiciraptor.com

Создать `/etc/nginx/sites-enabled/practiciraptor.com`:

```nginx
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name practiciraptor.com;

    ssl_certificate /etc/letsencrypt/live/practiciraptor.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/practiciraptor.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # WebSocket upgrade headers
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_read_timeout 3600s;

    location / {
        proxy_pass http://127.0.0.1:8080;
    }
}

server {
    listen 80;
    listen [::]:80;
    server_name practiciraptor.com;
    return 301 https://$host$request_uri;
}
```

Получить SSL-сертификат:
```bash
certbot --nginx -d practiciraptor.com
```

### 3.3 Настроить CORS в TPS

Виджет на GitHub Pages будет делать запросы с другого origin —
нужно добавить CORS в `core/app.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://<github-username>.github.io"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)
```

### 3.4 Запустить TPS как systemd-сервис

Создать `/etc/systemd/system/tps.service`:

```ini
[Unit]
Description=Terminal Pool Service
After=network.target docker.service
Requires=docker.service

[Service]
User=sky
WorkingDirectory=/home/sky/info-tech-io/web-terminal
EnvironmentFile=/home/sky/info-tech-io/web-terminal/.env
ExecStart=/home/sky/info-tech-io/web-terminal/.venv/bin/uvicorn core.app:app --host 0.0.0.0 --port 8080
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
systemctl enable tps && systemctl start tps
```

### 3.5 Обновить `templates/index.html`

Минимальная страница TPS (отдаётся при `GET /` на practiciraptor.com):

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TPS — Terminal Pool Service</title>
</head>
<body>
  <h1>Terminal Pool Service</h1>
  <p>API is running. See <a href="/docs">API docs</a>.</p>
</body>
</html>
```

### 3.6 Создать демо-страницу на GitHub Pages

Файл `docs/demo/index.html` (публикуется через GitHub Pages из ветки `main`, папка `docs/`):

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rustlings Demo — Web Terminal</title>
</head>
<body>
  <h1>Rustlings in your browser</h1>
  <p>Interactive Rust exercises, no install needed.</p>

  <script src="https://practiciraptor.com/widget/widget.js"
          data-pack="rustlings"
          data-tps-url="https://practiciraptor.com">
  </script>
</body>
</html>
```

### 3.7 Smoke-test полного флоу

1. `curl https://practiciraptor.com/api/packs` → список паков с `pool_warm > 0`
2. Открыть GitHub Pages демо в браузере
3. Нажать «Launch Terminal» → терминал открывается ≤ 3 сек
4. Ввести команду в терминале, убедиться в ответе
5. Закрыть страницу → `pool_busy` уменьшился (`GET /api/packs/rustlings`)

### 3.8 Обновить README

Добавить раздел **Deploy** с инструкцией:
- Сборка образа, запуск TPS, конфиг nginx
- Как встроить виджет на любую страницу

## Acceptance Criteria

- [ ] `docker images | grep tps-rustlings` — образ существует
- [ ] `GET https://practiciraptor.com/api/packs` возвращает rustlings с `pool_warm > 0`
- [ ] `GET https://practiciraptor.com/widget/widget.js` — `200 OK`
- [ ] Демо-страница на GitHub Pages открывает терминал через виджет
- [ ] WebSocket соединение устанавливается (wss://)
- [ ] `beforeunload` освобождает контейнер
- [ ] CORS настроен: запросы с GitHub Pages проходят без ошибок
