#!/usr/bin/env bash
# Before-submit hook (Linux / macOS)
# Runs before the prompt is sent to the model.
# TODO: scrub secrets from prompt, save state before context compaction, etc.

mkdir -p .cursor/logs
echo "$(date -Iseconds) before-submit" >> .cursor/logs/hooks.log
