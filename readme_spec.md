# Spec-Driven Development Rules

Universal engineering rules adapted from the `arbitrator` project and
re-shaped for **SEOPartnerHub** (Django 6 + DRF + Celery + Postgres +
Redis + Cookiecutter-Django, Python 3.14).

The rules below are written as a **Spec Kit Constitution**: each section
is an Article that becomes a hard input for `/speckit-specify`,
`/speckit-plan`, `/speckit-tasks`, and `/speckit-implement`.

---

## How to plug into Spec Kit

1. Copy the **Constitution** section (everything between
   `<!-- CONSTITUTION:BEGIN -->` and `<!-- CONSTITUTION:END -->`) into
   `.specify/memory/constitution.md`, replacing the template
   placeholders.
2. Fill the version / date footer at the bottom.
3. In Cursor Agent run:

   ```text
   /speckit-constitution
   ```

   The skill will validate the file, normalize headings, and make the
   principles available to every later workflow step
   (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`,
   `/speckit-implement`, `/speckit-analyze`, `/speckit-checklist`).
4. From now on every new feature must be created via:

   ```text
   /speckit-specify   <feature description>
   /speckit-clarify   (optional, de-risk ambiguity)
   /speckit-plan
   /speckit-checklist (optional, quality gate)
   /speckit-tasks
   /speckit-analyze   (optional, consistency check)
   /speckit-implement
   ```

   Every artifact MUST cite the relevant Article(s) below.

---

<!-- CONSTITUTION:BEGIN -->

# SEOPartnerHub Constitution

## Core Principles

### I. Class-Based & Clean Architecture
- Application code is organized by **Django apps** under
  `seopartnerhub/<app>/` (e.g. `users/`, `outreach/`, `partners/`,
  `dashboards/`).
- Inside every app the layering MUST be:
  ```
  api/  (DRF views, serializers, urls)
    ↓
  services/  (use cases, orchestration, transactions)
    ↓
  models/   selectors/   tasks/   (domain + read queries + Celery tasks)
  ```
  Outer layers MAY import inner layers, never the opposite.
- Business logic lives in **service classes**, NOT in views, serializers,
  signals, or model methods. Views translate HTTP ↔ services. Models hold
  data + invariants only.
- One public class per file. Filename = class name in `snake_case`
  (`class OutreachSender` lives in `outreach_sender.py`).
- Prefer **composition** over inheritance. Inject collaborators through
  `__init__`, not via module-level singletons.

### II. Strict Typing (NON-NEGOTIABLE)
- `mypy` MUST pass against `seopartnerhub` (config already enables
  `mypy_django_plugin` and `mypy_drf_plugin`).
- **`typing.Any` is forbidden** in application code. Use `object` +
  `isinstance`, `TypedDict`, `Protocol`, generics, or proper unions.
- `# type: ignore` is only allowed with a comment explaining why and a
  `TODO` for removal.
- Every public function / method / class attribute MUST be fully typed.
- Pydantic models (where used outside Django ORM, e.g. DTOs for external
  APIs / webhooks / n8n payloads) are the source of truth for runtime
  shapes; mark them `model_config = ConfigDict(frozen=True)` whenever
  possible.

### III. Configuration as Single Source of Truth
- Runtime settings live ONLY in `config/settings/{base,local,production,test}.py`,
  fed by `django-environ` from `./.envs/.local/*` and `./.envs/.production/*`.
- **No hardcoded env-dependent values** anywhere outside `config/`.
- Adding a new parameter:
  1. Add a typed read in the appropriate `settings/*.py`.
  2. Add the matching `KEY=value` line to `.envs/.local/.django` (and
     `.production/.django` if used in prod).
  3. Inject the value through Django `settings` import or via a service
     constructor; never `os.environ` outside `config/`.

### IV. Logging Discipline (NON-NEGOTIABLE)
- All logging is configured via Django `LOGGING` in
  `config/settings/base.py`. No ad-hoc logging configuration.
- Inside modules use:
  ```python
  import logging
  logger = logging.getLogger(__name__)
  ```
- **`print()` is forbidden** in `config/`, `seopartnerhub/`, `tasks/`,
  and `management/commands/`. It is allowed only for genuine CLI output
  in admin scripts.
- Every `except Exception:` block MUST call `logger.exception("static
  message", extra={...})`. **Never** log only `str(error)` or
  `error.message` — the full traceback is mandatory.
- Log messages MUST be **static strings**; dynamic data goes into
  `extra=` so it is queryable in log aggregation.
- Required logging points: Celery task start/finish/failure, external
  API call (request id + status), webhook receipt, auth events,
  permission denials, retry/backoff iterations (debug level).

### V. Error Handling
- Prefer returning `Result | None` over raising for **expected** business
  outcomes (e.g. "lead not found", "quota exceeded").
- Raise only for truly exceptional situations. Use a **static** message
  and pass dynamic context via the `Error` second argument /
  `logging.extra`.
- API errors MUST go through a single DRF exception handler that maps
  domain exceptions to JSON `{ "error": { "code": ..., "message": ... } }`.
- Celery tasks MUST be **idempotent** and use explicit retry policy
  (`autoretry_for`, `retry_backoff`, `max_retries`).
- Never swallow exceptions silently. Bare `except:` and `except
  Exception: pass` are forbidden.

### VI. External Library & API Lookup via Context7
- Before writing, reviewing, or explaining code that uses any
  third-party library (Django, DRF, Celery, allauth, django-environ,
  whitenoise, anymail, drf-spectacular, ...), if you are uncertain
  about the current API surface, **do not guess**.
- Call the **Context7 MCP** server:
  1. `resolve-library-id` with the library name.
  2. `get-library-docs` with the returned id, focused on the topic.
- Cite the library + section in the answer / PR description.
- Fallback chain: confident knowledge → Context7 → official docs via
  WebSearch/WebFetch → state "no authoritative source" (never
  fabricate).

### VII. Documentation & Spec Sync
- After every change that adds / removes / renames files, models, API
  endpoints, settings keys, Celery tasks, env variables, or commands,
  the agent MUST update before reporting done:
  - `README.md` (user-facing run / install instructions).
  - `readme_start.md` (quick start cheatsheet).
  - `readme_spec.md` (this file — if a rule itself changed).
  - `.specify/memory/constitution.md` (mirror of the constitution
    section).
  - The relevant spec under `specs/<feature>/spec.md` and `plan.md`.
  - Any `.cursor/rules/*.mdc` whose scope overlaps the change.
- Reporting "done" while `Grep` still finds the old name in any of the
  files above is forbidden.

### VIII. Security & Permissions
- **Never read or echo** `.env`, `.env.*`, `./.envs/**`, or any file
  containing secrets. These are denied in `.cursor/settings.json` and
  `.cursorignore`.
- Never commit secrets. Use Django `SECRET_KEY` from env, not literals.
- DRF endpoints default to `IsAuthenticated`; opening an endpoint
  requires an explicit permission class and a note in the spec.
- All external input (REST bodies, webhooks, n8n payloads) MUST be
  validated through a serializer or a Pydantic DTO before reaching a
  service.

### IX. Quality Gates (NON-NEGOTIABLE)
The following pipeline MUST pass locally and in CI before a feature is
considered shipped. It is wrapped by `/ship` in
`.cursor/commands/ship.md`:

Backend:

```bash
uv run ruff check . --fix
uv run ruff format .
uv run djlint seopartnerhub/templates --reformat
uv run mypy seopartnerhub config
uv run pytest
```

Frontend (run inside `frontend/starter-kit/` or `frontend/full-version/`):

```bash
pnpm lint
pnpm typecheck
pnpm test --run
pnpm build
```

- Coverage thresholds are configured in `pyproject.toml` (`coverage`
  section). Lowering them requires an Article amendment.
- Migrations: any model change MUST include a migration in the same PR.
- Pre-commit hooks (`.pre-commit-config.yaml`) MUST stay green.

### X. Frontend Integration (NON-NEGOTIABLE)

The frontend is a **Next.js 16 App Router** application written in
**TypeScript** with **React 19**, **MUI**, and managed via **pnpm**. Two variants live
in the repository:

| Path                       | Purpose                                                                                  |
| -------------------------- | ---------------------------------------------------------------------------------------- |
| `frontend/starter-kit/`    | **MVP & CI target.** Wired to Django REST. All new features and auth flows live here.    |
| `frontend/full-version/`   | **Component donor.** Browsable showcase; components are migrated into `starter-kit` one-by-one. **Not wired to backend.** |

- All **new** feature work happens in `frontend/starter-kit/`.
- `frontend/full-version/` MUST remain runnable in the browser as a
  reference; do not modify it except to fix build breaks. Copy
  components out of it into `starter-kit/` and adapt them to the
  starter-kit theme / auth context.
- **Only `starter-kit` calls the Django REST API.** `full-version` MUST
  NOT depend on `/api/` or `/_allauth/` endpoints. If a `full-version`
  component contains backend calls, they MUST be stripped or stubbed
  during migration to `starter-kit`.

#### X.1 Docker

`docker-compose.local.yml` MUST run **two** frontend services from a
shared Dockerfile, parameterised by `WORKDIR`:

| Service              | Source folder              | Host port | Backend wired |
| -------------------- | -------------------------- | --------- | ------------- |
| `frontend_starter`   | `frontend/starter-kit/`    | `3000`    | yes           |
| `frontend_full`      | `frontend/full-version/`   | `3001`    | no            |

- Both services build from `compose/local/frontend/Dockerfile`
  (base: `node:20-alpine`, package manager: `pnpm` via `corepack`,
  multi-stage `deps` → `dev`).
- Both mount their respective source as a volume and run `pnpm dev`.
- `frontend_starter.depends_on: [django]`. `frontend_full` is
  standalone.
- `node_modules` is kept in a named volume per service, not shared, to
  avoid lock conflicts.
- `package.json` scripts in both variants MUST expose the canonical
  entry points: `dev`, `build`, `start`, `lint`, `typecheck`, `test`.
  `starter-kit/package.json` additionally exposes `generate:api`.

#### X.2 Auth — django-allauth headless

- All registration / login / logout / email-verification / password-reset
  / MFA flows MUST go through **`django-allauth` headless REST** at
  `/_allauth/browser/v1/...`. **No custom auth endpoints.**
- Required Django settings (in `config/settings/base.py` unless noted):
  - `INSTALLED_APPS += ["allauth.headless"]`
  - `HEADLESS_ONLY = False`  (keep server templates for admin recovery)
  - `HEADLESS_FRONTEND_URLS = { "account_confirm_email": ".../verify-email/{key}", "account_reset_password_from_key": ".../reset-password/{key}", "account_signup": ".../register" }`
  - `urlpatterns += [path("_allauth/", include("allauth.headless.urls"))]`
- Auth state on the frontend is a **HttpOnly session cookie** set by
  allauth (browser flow). Bearer tokens are forbidden unless the spec
  explicitly justifies them.
- CORS / CSRF (in `config/settings/local.py`):
  - `CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]`
  - `CORS_ALLOW_CREDENTIALS = True`
  - `CSRF_TRUSTED_ORIGINS = ["http://localhost:3000"]`
  - `SESSION_COOKIE_SAMESITE = "Lax"` for local;
    production behind same parent domain uses `"Lax"`,
    cross-site requires `"None"` + `Secure=True` (HTTPS only).
- In local dev the Next.js app MUST proxy `/_allauth/*` and `/api/*` to
  the Django service via `next.config.ts` `rewrites`, so the browser
  sees a single origin and CORS does not apply.

#### X.3 Frontend code rules

- **One typed API client** under `src/lib/api/` (e.g. `apiClient.ts`)
  wrapping `fetch` with `credentials: "include"`, error mapping, and
  retry policy. No `fetch()` calls in React components.
- **One auth client** under `src/lib/auth/` exposing methods that map
  1-to-1 to allauth headless endpoints
  (`signup`, `login`, `logout`, `getSession`, `requestPasswordReset`,
  `confirmPasswordReset`, `verifyEmail`, MFA helpers).
- **Types generated from OpenAPI**: the script `pnpm generate:api`
  fetches `/api/schema/` from Django and runs `openapi-typescript` into
  `src/lib/api/schema.ts`. CI fails if the committed file drifts.
- All forms MUST use **react-hook-form + zod** for validation; no
  manual `useState` for form fields.
- Auth state lives in a single React Context provider
  (`src/lib/auth/AuthProvider.tsx`) that calls
  `auth.getSession()` on mount and exposes `{ user, status, login,
  logout, ... }`. Components consume it via `useAuth()`.
- Mandatory pages in `frontend/starter-kit/src/app/`:
  - `(auth)/login`
  - `(auth)/register`
  - `(auth)/verify-email/[key]`
  - `(auth)/reset-password`
  - `(auth)/reset-password/[key]`
  - `(dashboard)/...` — protected by a server-side session check.
- **No `any` in TypeScript.** Use `unknown`, generics, or proper unions
  (mirrors backend Article II).
- ESLint + Prettier MUST be green. `pnpm typecheck` (`tsc --noEmit`)
  MUST pass.

#### X.4 Documentation & spec sync

- `README.md` and `readme_start.md` MUST list the frontend port (3000),
  the `pnpm dev` flow, and the Docker variant.
- Any change to allauth headless config or to `next.config.ts` rewrites
  MUST update this Article and the relevant `specs/<feature>/plan.md`.

## Technology Constraints

- **Backend stack**: Python 3.14, Django 6, DRF, django-allauth
  (headless mode), Celery 5 + Redis, Postgres 18, Cookiecutter-Django
  layout, `uv` package manager.
- **Frontend stack**: Next.js 16 App Router, React 19, TypeScript,
  MUI, pnpm. Lives under `frontend/starter-kit/` (MVP target) and
  `frontend/full-version/` (reference).
- **Auth**: only `django-allauth` headless REST under
  `/_allauth/browser/v1/...`. Session cookies (HttpOnly).
- **API contract**: source of truth is `drf-spectacular`
  (`/api/schema/`). Frontend TypeScript types are generated from it.
- **Async I/O**: use Django async views or Celery tasks; do not block
  request threads on external I/O.
- **Background work**: every job longer than ~200 ms or touching a
  third-party API MUST be a Celery task with idempotency and retries.
- **External integrations** (n8n, webhooks, partner APIs) MUST go
  through an adapter class under `seopartnerhub/<app>/integrations/`
  that implements a `domain` protocol; the service depends on the
  protocol, not on `requests` directly.
- **Container-first**: local dev runs through
  `docker-compose.local.yml` (Django + Postgres + Redis + Mailpit +
  Celery + Flower + **frontend**). Rules and commands MUST work both
  inside and outside the container.

## Development Workflow

1. `/speckit-specify <feature>` — write `spec.md`.
2. `/speckit-clarify` (optional) — resolve open questions.
3. `/speckit-plan` — produce `plan.md` referencing the Articles above.
4. `/speckit-checklist` (optional) — generate quality checklist.
5. `/speckit-tasks` — break `plan.md` into `tasks.md`.
6. `/speckit-analyze` (optional) — cross-artifact consistency.
7. `/speckit-implement` — execute tasks; each PR MUST run `/ship`.
8. Code review by the `code-reviewer` subagent before merge.

## Governance

- This Constitution supersedes ad-hoc decisions and any inline
  comments / TODOs that contradict it.
- Amendments require: a PR editing both `readme_spec.md` and
  `.specify/memory/constitution.md`, plus a bumped version below and a
  one-line entry in the PR description.
- Spec Kit workflow steps will reject artifacts that violate
  NON-NEGOTIABLE Articles (II, IV, IX).

**Version**: 0.1.0 | **Ratified**: 2026-06-01 | **Last Amended**: 2026-06-01

<!-- CONSTITUTION:END -->

---

## Source attribution

Adapted from the reference project `C:\shere-folder\arbitrator`:

| Source file                                    | Used for Article(s)        |
| ---------------------------------------------- | -------------------------- |
| `AGENTS.md`                                    | I, III, IX                 |
| `.cursor/rules/architecture.mdc`               | I, II, III, V              |
| `.cursor/rules/logging.mdc`                    | IV                         |
| `.cursor/rules/context7-lookup.mdc`            | VI                         |
| `.cursor/rules/documentation-sync.mdc`         | VII                        |
| `.cursor/settings.json` + `.cursorignore`      | VIII                       |
| `.cursor/commands/ship.md`                     | IX                         |

Article **X (Frontend Integration)** is project-specific to
SEOPartnerHub and has no counterpart in `arbitrator` (CLI/Streamlit
project).

Project-specific items from `arbitrator` (ccxt.pro `watch_*`,
USDT-margined perpetual futures, Streamlit composition root, exchange
`Factory._registry`) are **intentionally excluded** as non-universal.
