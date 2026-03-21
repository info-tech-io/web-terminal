# Stage 3 Progress: Demo Page + Public Deployment

**Issue**: [#6](https://github.com/info-tech-io/web-terminal/issues/6)
**Stage**: 3 of 3
**Status**: ✅ Complete

## What Was Done

### Docker image: tps-rustlings

```
docker build -t tps-rustlings packs/rustlings/
→ sha256:08781fbd... (все слои из кэша)
```

### SSL: practiciraptor.com

```
certbot certonly --nginx -d practiciraptor.com
→ /etc/letsencrypt/live/practiciraptor.com/ (expires 2026-06-19)
```

### nginx: /etc/nginx/sites-enabled/practiciraptor.com

- SSL + proxy_pass → http://127.0.0.1:8080
- WebSocket upgrade headers (`Upgrade`, `Connection`, `proxy_read_timeout 3600s`)
- HTTP → HTTPS redirect

### CORS: core/app.py

```python
app.add_middleware(CORSMiddleware,
    allow_origins=["https://info-tech-io.github.io"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)
```

### systemd: /etc/systemd/system/tps.service

TPS запущен как systemd-сервис (enabled, автозапуск при перезагрузке):
```
User=sky, WorkingDirectory=.../web-terminal
ExecStart=.venv/bin/uvicorn core.app:app --host 0.0.0.0 --port 8080
```

### templates/index.html

Обновлена под API-страницу со ссылками на `/docs` и `/api/packs`.

### docs/demo/index.html

Статическая демо-страница для GitHub Pages:
```html
<script src="https://practiciraptor.com/widget/widget.js"
        data-pack="rustlings"
        data-tps-url="https://practiciraptor.com">
</script>
```

### Smoke test

```
GET https://practiciraptor.com/api/packs
→ [{"id":"rustlings","pool_warm":3,"pool_busy":0,...}]
```

Все 3 контейнера прогрелись сразу после старта сервиса.

## Commits

- `feat(issue-6): Stage 3 — public deployment on practiciraptor.com`

## Acceptance Criteria

- [x] `docker images | grep tps-rustlings` — образ существует
- [x] `GET https://practiciraptor.com/api/packs` → rustlings с `pool_warm: 3`
- [x] `GET https://practiciraptor.com/widget/widget.js` → 200 OK
- [x] CORS настроен для info-tech-io.github.io
- [x] TPS запущен как systemd-сервис (enabled, автозапуск)
- [x] `docs/demo/index.html` создан для GitHub Pages
- [ ] Демо-страница на GitHub Pages открывает терминал (требует настройки Pages)
- [ ] Полный E2E тест через браузер
