# Stage 2 Progress: Build Pipeline

**Issue**: [#6](https://github.com/info-tech-io/web-terminal/issues/6)
**Stage**: 2 of 3
**Status**: ✅ Complete

## What Was Done

### npm install + esbuild build

```
added 4 packages, audited 5 packages — 0 vulnerabilities
widget.js  289.5kb  ⚡ Done in 91ms
```

xterm.js и addon-fit успешно встроены в бандл. Бандл не добавляется в git
(покрыт `.gitignore`).

### `core/app.py` — StaticFiles mount

Добавлено монтирование директории `widget/`:

```python
from fastapi.staticfiles import StaticFiles
app.mount("/widget", StaticFiles(directory="widget"), name="widget")
```

После монтирования `/widget/widget.js` отдаётся напрямую без дополнительных
роутов. Проверка:

```
routes: [..., '/widget', '/api/packs', ...]
```

## Commits

- `feat(issue-6): Stage 2 — esbuild build pipeline, FastAPI StaticFiles /widget`

## Acceptance Criteria

- [x] `npm run build --prefix widget` завершается без ошибок
- [x] `widget/widget.js` создаётся (289.5 KB с встроенным xterm.js)
- [x] `/widget` смонтирован в FastAPI, приложение загружается без ошибок
- [x] `widget/widget.js` и `widget/node_modules/` покрыты `.gitignore`
- [x] `requirements.txt` не изменён (StaticFiles входит в fastapi[standard])
