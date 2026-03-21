# Stage 2: Build Pipeline

**Issue**: [#6](https://github.com/info-tech-io/web-terminal/issues/6)
**Stage**: 2 of 3

## Goal

Настроить сборку `widget/src/widget.js` → `widget/widget.js` через esbuild
и отдавать бандл через FastAPI `StaticFiles`.

## Context

После Stage 1 существует `widget/src/widget.js` с импортами xterm.js.
Бандл нужен единственным файлом без внешних зависимостей в рантайме —
xterm.js должен быть встроен внутрь `widget.js`.

## Tasks

### 2.1 Добавить build-скрипт в `package.json`

```json
{
  "scripts": {
    "build": "esbuild widget/src/widget.js --bundle --minify --outfile=widget/widget.js --platform=browser --target=es2017"
  }
}
```

Флаги:
- `--bundle` — встроить xterm.js и addon-fit
- `--minify` — минификация для продакшна
- `--platform=browser` — не добавлять Node.js полифилы
- `--target=es2017` — поддержка современных браузеров

### 2.2 Добавить `StaticFiles` в FastAPI

В `core/app.py` добавить монтирование директории `widget/`:

```python
from fastapi.staticfiles import StaticFiles

app.mount("/widget", StaticFiles(directory="widget"), name="widget")
```

После этого `widget.js` будет доступен по пути `/widget/widget.js`.

### 2.3 Добавить `widget/` в `.gitignore` (только бандл)

Исходники коммитятся, бандл генерируется при деплое:

```gitignore
# widget build output
widget/widget.js
widget/node_modules/
```

### 2.4 Верификация сборки

```bash
cd /home/sky/info-tech-io/web-terminal
npm install --prefix widget
npm run build --prefix widget
# → widget/widget.js должен появиться (~500KB с xterm.js)
```

Проверка, что FastAPI отдаёт файл:
```bash
curl -I http://localhost:8000/widget/widget.js
# → HTTP/1.1 200 OK, Content-Type: application/javascript
```

## File Structure After Stage

```
widget/
├── src/
│   └── widget.js       ← исходник (в git)
├── widget.js           ← бандл (НЕ в git, генерируется)
└── package.json        ← в git
```

## Acceptance Criteria

- [ ] `npm run build --prefix widget` завершается без ошибок
- [ ] `widget/widget.js` создаётся и содержит xterm.js (размер > 100KB)
- [ ] `GET /widget/widget.js` возвращает `200 OK`
- [ ] `widget/widget.js` и `widget/node_modules/` добавлены в `.gitignore`
- [ ] `requirements.txt` не изменён (StaticFiles входит в fastapi[standard])
