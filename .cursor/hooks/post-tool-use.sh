#!/usr/bin/env bash
# Post-tool-use hook (Linux / macOS)
# Fires after every file edit Cursor performs.
# TODO: auto-run "uv run ruff check --fix <edited>", auto-commit, etc.

mkdir -p .cursor/logs
echo "$(date -Iseconds) post-tool-use" >> .cursor/logs/hooks.log
