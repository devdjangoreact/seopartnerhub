# AGENTS.md

> Project rules for AI agents. Keep this file **under 200 lines**.
> Full engineering principles live in `readme_spec.md` (Spec Kit
> Constitution).

## Project

- **Name**: SEOPartnerHub
- **Purpose**: Internal tool for SEO and BizDev teams. Outreach,
  link-building, partnership management, dashboards.
- **Language**: Python 3.14
- **Stack**: Django 6 + DRF + Celery 5 + Postgres 18 + Redis + uvicorn
- **Layout**: Cookiecutter-Django
- **Package manager**: `uv`
- **Spec workflow**: Spec Kit (`.specify/` + `/speckit-*` skills)

## Golden rules

1. Read this file and `readme_spec.md` before doing anything.
2. Never edit `*.local.*` files — personal overrides.
3. Never read `.env`, `.env.*`, or `./.envs/**`.
4. Ask before creating new files.
5. English in code, comments, and commit messages.
6. **All business logic is class-based** in `services/`. No logic in
   views, serializers, signals, or model methods.
7. After every code/structure change, update docs and rules — see
   `.cursor/rules/documentation-sync.mdc`.
8. Every new feature MUST go through Spec Kit:
   `/speckit-specify` → `/speckit-plan` → `/speckit-tasks` →
   `/speckit-implement`.

## Architecture

Strict layering inside each Django app — see
`.cursor/rules/architecture.mdc`:

```
api/  →  services/  →  selectors/ + models + integrations(protocol)
                                  ↑
                          tasks/  (Celery wrappers around services)
```

| Path                                          | Responsibility                                   |
| --------------------------------------------- | ------------------------------------------------ |
| `config/`                                     | Django project: settings, urls, asgi, celery_app |
| `config/settings/{base,local,production,test}.py` | All runtime configuration                    |
| `seopartnerhub/<app>/api/`                    | DRF views, serializers, urls                     |
| `seopartnerhub/<app>/services/`               | Use cases, orchestration, transactions           |
| `seopartnerhub/<app>/selectors/`              | Read-only queries                                |
| `seopartnerhub/<app>/tasks/`                  | Celery tasks (idempotent, with retries)          |
| `seopartnerhub/<app>/integrations/`           | Adapters for external APIs / webhooks / n8n     |
| `seopartnerhub/<app>/models.py`               | Django ORM models + invariants                   |
| `seopartnerhub/n8n/`                          | n8n processes app: models, services, HMAC callbacks, scheduled triggers |
| `seopartnerhub/fake_db/`                      | STUB fixtures served at `/api/fake-db/` (see `.cursor/rules/fake-db-endpoint.mdc`) |
| `tests/`                                      | Cross-app tests                                  |
| `specs/`                                      | Spec Kit feature specs                           |
| `.specify/`                                   | Spec Kit infrastructure                          |

## Commands

All run from project root.

| Task             | Command                                                             |
| ---------------- | ------------------------------------------------------------------- |
| Install          | `uv sync`                                                           |
| Run (Docker)     | `docker compose -f docker-compose.local.yml up --build`             |
| Stop (Docker)    | `docker compose -f docker-compose.local.yml down`                   |
| Superuser        | `docker compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser` |
| Migrate (host)   | `uv run python manage.py migrate`                                   |
| Lint             | `uv run ruff check .`                                               |
| Format           | `uv run ruff format .`                                              |
| Type check       | `uv run mypy seopartnerhub config`                                  |
| Test             | `uv run pytest`                                                     |
| Coverage         | `uv run coverage run -m pytest && uv run coverage html`             |
| Celery worker    | `uv run celery -A config.celery_app worker -l info`                 |
| Celery beat      | `uv run celery -A config.celery_app beat`                           |
| Ship (full QA)   | see `.cursor/commands/ship.md`                                      |

Local URLs after `docker compose ... up`:

- App: `http://127.0.0.1:8000`
- Mailpit (mail): `http://127.0.0.1:8025`
- Flower (Celery): `http://127.0.0.1:5555`

## Code style (Python)

- `mypy` must pass against `seopartnerhub` and `config`.
  **No `typing.Any`.** Use `object` + `isinstance`, generics,
  `TypedDict`, or `Protocol`.
- `from __future__ import annotations` at the top of every module.
- One public class per file. Filename = class name in `snake_case`.
- Prefer composition over inheritance.
- Dependency Inversion: services depend on `Protocol`s, concrete
  adapters are injected in `apps.py` / DI factory.
- Use `pydantic.BaseModel` for non-ORM DTOs; mark them `frozen=True`
  where possible.
- Logging: `logger = logging.getLogger(__name__)`, log full exceptions
  via `logger.exception("static_msg", extra={...})`.
  **No `print()`** in app code.

## Where things live

| Concern             | Path                                |
| ------------------- | ----------------------------------- |
| Spec Kit memory     | `.specify/memory/constitution.md`   |
| Spec templates      | `.specify/templates/`               |
| Feature specs       | `specs/<feature>/{spec,plan,tasks}.md` |
| MCP servers         | `.cursor/mcp.json`                  |
| Hooks               | `.cursor/hooks.json` + `.cursor/hooks/` |
| Slash commands      | `.cursor/commands/`                 |
| Subagents           | `.cursor/agents/`                   |
| Custom modes        | `.cursor/modes/`                    |
| Path-scoped rules   | `.cursor/rules/*.mdc`               |
| Settings            | `.cursor/settings.json`             |
| Constitution (docs) | `readme_spec.md`                    |
