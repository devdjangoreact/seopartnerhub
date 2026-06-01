---
description: Format, lint, type-check, test. Full quality pipeline.
---

# /ship

Run the full quality pipeline against the project. Stop on the first
failing step and surface the exact log.

## Local (uv on host)

Windows (PowerShell):

```powershell
uv run ruff check . --fix
uv run ruff format .
uv run djlint seopartnerhub/templates --reformat
uv run mypy seopartnerhub config
uv run pytest
```

Linux / macOS:

```bash
uv run ruff check . --fix
uv run ruff format .
uv run djlint seopartnerhub/templates --reformat
uv run mypy seopartnerhub config
uv run pytest
```

## Inside Docker

```bash
docker compose -f docker-compose.local.yml run --rm django ruff check . --fix
docker compose -f docker-compose.local.yml run --rm django ruff format .
docker compose -f docker-compose.local.yml run --rm django djlint seopartnerhub/templates --reformat
docker compose -f docker-compose.local.yml run --rm django mypy seopartnerhub config
docker compose -f docker-compose.local.yml run --rm django pytest
```

## Pre-merge checklist

- [ ] All steps above are green.
- [ ] Migrations included for every model change.
- [ ] `README.md` / `readme_start.md` / `readme_spec.md` updated if
      install / run / settings changed.
- [ ] `specs/<feature>/spec.md` and `plan.md` updated if the feature
      changed.
- [ ] `code-reviewer` subagent approved the diff.
