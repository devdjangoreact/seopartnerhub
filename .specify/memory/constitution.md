# SEOPartnerHub Constitution

## Core Principles

### I. Class-Based & Clean Architecture
- Application code is organized by **Django apps** under `seopartnerhub/<app>/`.
- Business logic lives in service classes, not in views, serializers, signals, or model methods.
- One public class per file. Filename = class name in `snake_case`.
- Prefer composition over inheritance. Inject collaborators through constructors.

### II. Strict Typing (NON-NEGOTIABLE)
- `mypy` MUST pass against `seopartnerhub` and `config`.
- `typing.Any` is forbidden in application code.
- Every public function / method / class attribute MUST be fully typed.
- TypeScript code MUST NOT use `any`; use `unknown`, generics, or proper unions.

### III. Configuration as Single Source of Truth
- Backend runtime settings live only in `config/settings/{base,local,production,test}.py`.
- No hardcoded env-dependent values outside `config/`.
- Frontend runtime configuration is read from environment variables and documented in quickstart files.

### IV. Logging Discipline (NON-NEGOTIABLE)
- Logging is configured through Django `LOGGING` in `config/settings/base.py`.
- Python modules use `logging.getLogger(__name__)`.
- `print()` is forbidden in app code.
- Every broad exception handler logs full exception context with `logger.exception(...)`.

### V. Error Handling
- Prefer explicit result states for expected business outcomes.
- Raise only for exceptional cases.
- API errors MUST be mapped consistently to structured client-facing errors.
- Celery tasks MUST be idempotent and declare retry policy.

### VI. External Library & API Lookup
- If unsure about third-party APIs, use Context7 MCP where available.
- If Context7 is unavailable, use official docs via web search/fetch and cite them in research artifacts.
- Never fabricate library behavior.

### VII. Documentation & Spec Sync
- After changes to files, endpoints, settings, env variables, tasks, commands, or frontend startup, update relevant docs before reporting done.
- Keep `README.md`, `readme_start.md`, `readme_spec.md`, `.specify/memory/constitution.md`, and active `specs/<feature>/` artifacts consistent.

### VIII. Security & Permissions
- Never read or echo `.env`, `.env.*`, or `./.envs/**`.
- DRF endpoints default to authenticated access.
- All external input MUST be validated before reaching a service.

### IX. Quality Gates (NON-NEGOTIABLE)
Backend:

```bash
uv run ruff check . --fix
uv run ruff format .
uv run djlint seopartnerhub/templates --reformat
uv run mypy seopartnerhub config
uv run pytest
```

Frontend (inside `frontend/starter-kit/` or `frontend/full-version/`):

```bash
pnpm lint
pnpm typecheck
pnpm test --run
pnpm build
```

### X. Frontend Integration (NON-NEGOTIABLE)
- Frontend stack: Next.js 16 App Router, React 19, TypeScript, MUI, pnpm.
- `frontend/starter-kit/` is the MVP and backend-connected target.
- `frontend/full-version/` is a browsable component donor and MUST NOT call backend APIs.
- Docker local dev MUST expose starter-kit on port 3000 and full-version on port 3001.
- Authentication uses django-allauth headless browser endpoints under `/_allauth/browser/v1/...`.
- Auth state uses HttpOnly session cookies; bearer tokens are forbidden for v1.
- Frontend forms use typed validation and no TypeScript `any`.

## Technology Constraints

- Backend stack: Python 3.14, Django 6, DRF, django-allauth headless, Celery 5, Redis, Postgres 18, Cookiecutter-Django, uv.
- Frontend stack: Next.js 16, React 19, TypeScript 5.9, MUI 7, pnpm.
- API contract source of truth: drf-spectacular `/api/schema/`; frontend types are generated from it.
- Container-first local development via `docker-compose.local.yml`.

## Development Workflow

1. `/speckit-specify <feature>`
2. `/speckit-clarify`
3. `/speckit-plan`
4. `/speckit-checklist`
5. `/speckit-tasks`
6. `/speckit-analyze`
7. `/speckit-implement`
8. Code review before merge.

## Governance

- This Constitution supersedes ad-hoc decisions and TODOs that contradict it.
- Amendments require updating both `readme_spec.md` and `.specify/memory/constitution.md`.
- Spec Kit workflow steps reject artifacts that violate NON-NEGOTIABLE Articles II, IV, IX, or X.

**Version**: 0.1.0 | **Ratified**: 2026-06-01 | **Last Amended**: 2026-06-01
