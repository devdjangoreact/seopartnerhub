# Implementation Plan: Frontend Auth Bootstrap

**Branch**: `main` | **Date**: 2026-06-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-frontend-auth-bootstrap/spec.md`

## Summary

Bootstrap the frontend integration by running both existing Next.js variants in Docker, wiring
`frontend/starter-kit/` to Django's existing django-allauth headless browser auth, and keeping
`frontend/full-version/` as a browsable component donor with no backend dependency.

Technical approach:

- Add one shared local frontend Dockerfile and two compose services: `frontend_starter` on port
  3000 and `frontend_full` on port 3001.
- Enable django-allauth headless browser endpoints under `/_allauth/browser/v1/` while preserving
  classic allauth templates for admin / recovery.
- Keep auth session-based with HttpOnly Django session cookies and CSRF headers; do not introduce
  bearer tokens.
- Add a typed auth/API layer in `frontend/starter-kit/` only.
- Generate frontend API types from drf-spectacular `/api/schema/`.
- Defer MFA and RBAC to later features, but keep extension points open.

## Technical Context

**Language/Version**: Python 3.14; TypeScript 5.9.3; Node 20 in Docker.

**Primary Dependencies**: Django 6.0.5, Django REST Framework 3.17.1, django-allauth 65.18.0 with
`mfa` extra installed but disabled for v1, django-cors-headers 4.9.0, drf-spectacular 0.29.0,
Celery 5.6.3, Redis 8, Postgres 18, Next.js 16.1.1, React 19.2.3, MUI 7.3.6, pnpm.

**Storage**: Existing Postgres database for Django users, email addresses, sessions, and allauth
account state. Redis for Celery/cache where already configured. No new domain tables for v1.

**Testing**: Backend: `uv run pytest`, `uv run mypy seopartnerhub config`, `uv run ruff check .`,
`uv run ruff format .`. Frontend: `pnpm lint`, `pnpm typecheck`, `pnpm build`; add
`pnpm test --run` only after the test runner is added to the starter-kit.

**Target Platform**: Local Docker Compose on Linux-compatible containers; developer host may be
Windows. Browser target: modern evergreen browsers.

**Project Type**: Web application with Django backend and two Next.js frontend apps.

**Performance Goals**: Sign-in reaches product UI within 5 seconds on standard broadband;
registration + email verification can be completed within 2 minutes locally; one-command local
startup exposes both frontend URLs within 5 minutes on a clean machine.

**Constraints**: No custom auth surface; all auth flows use django-allauth headless browser
endpoints. Only `starter-kit` calls Django. `full-version` remains a backend-free showcase. No
TypeScript `any`. No MFA or RBAC in v1. Lockout policy is 5 failed attempts per identifier followed
by 60 seconds lockout, configurable.

**Scale/Scope**: Internal SEO/BizDev tool; v1 covers registration, email verification, sign-in,
sign-out, password reset, session identification, protected UI routing, and Docker startup for both
frontend variants.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Article | Gate | Status | Notes |
| ------- | ---- | ------ | ----- |
| I. Class-Based & Clean Architecture | Backend business logic in services, not views | PASS | v1 mostly config + allauth; any custom lockout/logging service goes under `seopartnerhub/users/services/`. |
| II. Strict Typing | No Python `Any`, no TS `any` | PASS | Plan requires typed frontend clients and generated OpenAPI types. |
| III. Configuration | Runtime settings in settings/env | PASS | All ports, frontend URLs, lockout thresholds, CORS/CSRF settings are settings/env-driven. |
| IV. Logging | Structured Django logging | PASS | Auth events logged through stdlib logger; no `print()`. |
| V. Error Handling | Structured errors and no silent swallowing | PASS | Frontend maps allauth error responses to typed UI errors. |
| VI. External Library Lookup | Docs checked | PASS | allauth, Next rewrites, CORS/CSRF researched in `research.md`. |
| VII. Docs & Spec Sync | Update docs/specs | PASS | Plan includes README/readme_start/readme_spec updates. |
| VIII. Security | No env reading; default authenticated access | PASS | Uses session cookies + CSRF; no bearer tokens. |
| IX. Quality Gates | Backend/frontend quality commands defined | PASS | Plan records backend and frontend checks. |
| X. Frontend Integration | Two Docker frontends; starter only calls API | PASS | Design keeps `frontend_full` isolated and browsable on port 3001. |

## Project Structure

### Documentation (this feature)

```text
specs/001-frontend-auth-bootstrap/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── auth-headless-browser.md
│   └── frontend-docker.md
└── tasks.md
```

### Source Code (repository root)

```text
compose/
└── local/
    └── frontend/
        ├── Dockerfile
        └── start

config/
├── settings/
│   ├── base.py
│   └── local.py
└── urls.py

seopartnerhub/
└── users/
    ├── services/
    │   └── sign_in_lockout_service.py
    └── tests/

frontend/
├── starter-kit/
│   ├── next.config.ts
│   ├── package.json
│   └── src/
│       ├── app/
│       │   ├── (auth)/
│       │   │   ├── login/page.tsx
│       │   │   ├── register/page.tsx
│       │   │   ├── reset-password/page.tsx
│       │   │   ├── reset-password/[key]/page.tsx
│       │   │   └── verify-email/[key]/page.tsx
│       │   └── (dashboard)/
│       │       └── layout.tsx
│       └── lib/
│           ├── api/
│           │   ├── apiClient.ts
│           │   └── schema.ts
│           └── auth/
│               ├── AuthProvider.tsx
│               ├── authClient.ts
│               ├── authTypes.ts
│               └── useAuth.ts
└── full-version/
    └── next.config.ts

tests/
└── users/
```

**Structure Decision**: Keep Cookiecutter-Django backend layout and the existing two Next.js
folders. Add only a Docker wrapper and starter-kit auth/API surface; do not merge or rename
frontend variants in this feature.

## Complexity Tracking

No constitution violations.

## Phase 0 Output

See [research.md](./research.md). All research decisions are resolved; there are no remaining
`NEEDS CLARIFICATION` markers.

## Phase 1 Output

- [data-model.md](./data-model.md)
- [quickstart.md](./quickstart.md)
- [contracts/auth-headless-browser.md](./contracts/auth-headless-browser.md)
- [contracts/frontend-docker.md](./contracts/frontend-docker.md)

## Post-Design Constitution Check

Re-evaluated after Phase 1 design: PASS. The design keeps django-allauth as the only auth surface,
keeps full-version isolated, uses typed frontend contracts, and documents required settings and
quality gates.
