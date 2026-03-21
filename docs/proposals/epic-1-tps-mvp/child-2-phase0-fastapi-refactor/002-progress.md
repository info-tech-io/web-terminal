# Stage 2 Progress Report: Terminal Resize (SIGWINCH)

**Status**: ✅ Complete
**Started**: 2026-03-21
**Completed**: 2026-03-21

## Summary

Реализован resize-протокол. Клиент отправляет `{"type":"resize","cols":N,"rows":M}` по WS;
сервер вызывает `exec_resize`. Начальный resize отправляется при открытии соединения.
