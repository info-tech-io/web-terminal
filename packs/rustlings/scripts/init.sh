#!/bin/bash
# Runs once when the warm container starts.
# Clones rustlings exercises into /workspace.
set -e

REPO="https://github.com/rust-lang/rustlings"
DEST="/workspace/rustlings"

if [ ! -d "$DEST" ]; then
    git clone --depth 1 "$REPO" "$DEST"
fi

cd "$DEST"
rustlings init 2>/dev/null || true

echo "[init.sh] rustlings ready at $DEST"
