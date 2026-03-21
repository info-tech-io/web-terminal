# Child #4 (Phase 1-B): Session API with JWT

**Type**: Large Issue
**Status**: Planned
**Issue**: [#4](https://github.com/info-tech-io/web-terminal/issues/4)
**Epic**: [#1](https://github.com/info-tech-io/web-terminal/issues/1)
**Blocked by**: Child #3 (Phase 1-A)

## Problem Statement

Нужен безопасный способ привязать WS-соединение к конкретному выделенному контейнеру.
Без токена любой может открыть WS и получить произвольный контейнер.

## Solution Overview

`POST /api/sessions` аллоцирует контейнер и возвращает короткоживущий JWT.
WS-эндпоинт `/ws/{token}` принимает только валидный токен — это обеспечивает привязку.

## JWT Payload

```json
{
  "sub": "session",
  "container_id": "abc123",
  "pack_id": "rustlings",
  "exercise_id": "intro1",
  "exp": 1234567890
}
```

TTL = `session_timeout_sec` из `pack.json` (по умолчанию 3600 сек).

## API

```
POST /api/sessions
  body:  { "pack_id": "rustlings", "exercise_id": "intro1" }
  200:   { "session_token": "...", "ws_url": "/ws/...", "expires_at": "..." }
  503:   { "error": "no_capacity" }

DELETE /api/sessions/{token}
  204:   session terminated

WS /ws/{session_token}
  4401:  invalid or expired token
  PTY stream after handshake
```

## Implementation Stages

### Stage 1: Session model + JWT utils
- `core/session.py` — Pydantic-модель, `create_token`, `verify_token`
- Secret key из Settings

### Stage 2: API endpoints
- `POST /api/sessions` → аллоцировать через Pool Manager, выдать JWT
- `DELETE /api/sessions/{token}` → release контейнера

### Stage 3: WS token validation
- `GET /ws/{token}` → проверить JWT, подключить к PTY контейнера
- При истечении TTL — закрыть WS, вызвать release

## Definition of Done

- [ ] `POST /api/sessions` возвращает валидный JWT
- [ ] `503` при `allocate()` == None
- [ ] WS с невалидным/истёкшим токеном отклоняется с кодом 4401
- [ ] `DELETE /api/sessions/{token}` освобождает контейнер
