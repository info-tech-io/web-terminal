#!/bin/bash
# Runs when a session starts. Navigates to the requested exercise.
# $EXERCISE_ID — exercise identifier from pack.json (e.g. "intro1")
cd /workspace/rustlings

if [ -n "$EXERCISE_ID" ]; then
    exec rustlings run "$EXERCISE_ID"
else
    exec bash
fi
