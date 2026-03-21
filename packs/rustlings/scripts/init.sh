#!/bin/bash
# Runs once when the warm container starts.
# Initializes rustlings exercises in /workspace.
set -e

DEST="/workspace/rustlings"

if [ ! -d "$DEST" ]; then
    cd /workspace
    rustlings init
fi

echo "[init.sh] rustlings ready at $DEST"
