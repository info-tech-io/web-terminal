#!/bin/bash
set -e

SESSION="main"

# Load env vars from volume (API key, web token)
if [ -f "$HOME/.env" ]; then
    export $(grep -v '^#' "$HOME/.env" | xargs)
fi

# Create detached tmux session with Claude Code if not already running
if ! tmux has-session -t "$SESSION" 2>/dev/null; then
    tmux new-session -d -s "$SESSION" -x 220 -y 60 "cd /root/ai/projects && claude"
fi

# Start FastAPI
exec /app/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8080
