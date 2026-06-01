#!/usr/bin/env bash
# Session-start hook (Linux / macOS)
# TODO: load project context on startup (git branch, last feature spec, etc).

mkdir -p .cursor/logs
echo "$(date -Iseconds) session-start" >> .cursor/logs/hooks.log
