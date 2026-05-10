#!/bin/bash
# Called by ws_proxy for every new session. Env: PACK_ID, EXERCISE_ID.
set -e

EXERCISE_DIR="/packs/${PACK_ID}/exercises/${EXERCISE_ID}"

mkdir -p ~/exercise

if [ -d "${EXERCISE_DIR}/workspace" ]; then
    cp -r "${EXERCISE_DIR}/workspace/." ~/exercise/
fi

if [ -f "${EXERCISE_DIR}/check.sh" ]; then
    cp "${EXERCISE_DIR}/check.sh" /usr/local/bin/check
    chmod +x /usr/local/bin/check
fi

cd ~/exercise

# Инициализируем go.mod если его нет (нужно для go run / go test)
[ -f go.mod ] || go mod init exercise 2>/dev/null

if [ -f "${EXERCISE_DIR}/task.md" ]; then
    echo ""
    cat "${EXERCISE_DIR}/task.md"
    echo ""
fi

exec bash
