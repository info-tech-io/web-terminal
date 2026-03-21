# Stage 3: Demo Page + GitHub Pages

**Issue**: [#6](https://github.com/info-tech-io/web-terminal/issues/6)
**Stage**: 3 of 3

## Goal

Обновить `templates/index.html` для работы с виджетом и настроить
публичную демо-страницу, встраивающую виджет с TPS через `<script>`.

## Context

После Stage 2 `widget/widget.js` собирается и отдаётся по `/widget/widget.js`.
Текущий `templates/index.html` — устаревший прототип без виджета.
GitHub Actions workflow (`notify-hub.yml`) уже существует.

## Tasks

### 3.1 Обновить `templates/index.html`

Заменить содержимое на минималистичную демо-страницу с виджетом:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TPS Demo — Rustlings</title>
</head>
<body>
  <h1>Web Terminal Demo</h1>
  <p>Rustlings — интерактивные упражнения по Rust прямо в браузере.</p>

  <script src="/widget/widget.js"
          data-pack="rustlings"
          data-tps-url="">
  </script>
</body>
</html>
```

`data-tps-url=""` — пустая строка означает `location.origin`,
то есть виджет обращается к тому же серверу, где открыта страница.

### 3.2 Добавить GitHub Pages деплой в README

В `README.md` добавить раздел **Deploy**:
- Как запустить TPS локально (`uvicorn core.app:app`)
- Переменные окружения (`.env.example`)
- Как собрать виджет (`npm run build --prefix widget`)
- Как встроить виджет на статическую страницу (пример `<script>` тега)

### 3.3 Smoke-test полного флоу

Последовательность проверки:
1. Запустить TPS: `uvicorn core.app:app --reload`
2. Открыть `http://localhost:8000/` в браузере
3. Нажать «Запустить терминал»
4. Убедиться, что терминал открылся и отвечает на ввод
5. Проверить все состояния:
   - `idle` → кнопка видна
   - `loading` → кнопка неактивна, индикатор загрузки
   - `connected` → терминал виден, кнопка «Завершить»
   - `terminated` → терминал скрыт, кнопка «Запустить» снова
6. Закрыть вкладку и убедиться через `GET /api/packs/rustlings`,
   что `pool_busy` уменьшился (контейнер освобождён)

### 3.4 Опционально: GitHub Pages

Если TPS развёрнут на публичном сервере:
- Создать `docs/demo/index.html` со `<script src="https://terminal.infotecha.ru/widget.js" ...>`
- Настроить GitHub Pages на публикацию из `docs/` ветки `main`
- Ссылку на демо добавить в `README.md`

Это выполняется только после публичного деплоя TPS (вне scope данного Child).

## Acceptance Criteria

- [ ] `GET /` возвращает страницу с тегом `<script data-pack="rustlings">`
- [ ] Полный флоу работает: кнопка → терминал → ввод команд → завершение
- [ ] `beforeunload` освобождает контейнер (проверить через `/api/packs/rustlings`)
- [ ] Состояния `no_capacity` и `error` отображаются корректно
- [ ] README содержит инструкцию по запуску и встраиванию виджета
