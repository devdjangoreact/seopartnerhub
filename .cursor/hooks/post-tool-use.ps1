# Post-tool-use hook (Windows / PowerShell)
# Fires after every file edit Cursor performs.
# TODO: auto-run "uv run ruff check --fix <edited>", auto-commit, etc.

param(
    [string]$EventJson
)

$logDir = ".cursor/logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Force -Path $logDir | Out-Null }
"$(Get-Date -Format o) post-tool-use" | Add-Content -Path "$logDir/hooks.log"
