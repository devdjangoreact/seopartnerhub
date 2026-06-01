# Quickstart: Frontend Auth Bootstrap

## Prerequisites

- Docker Desktop running.
- Node is optional on host; frontend runs in Docker.
- Do not read or edit `.env`, `.env.*`, or `./.envs/**` while implementing.

## Start the full local stack

```powershell
docker compose -f docker-compose.local.yml up --build
```

Expected local URLs:

- Django: `http://localhost:8000`
- Starter frontend: `http://localhost:3000`
- Full-version showcase: `http://localhost:3001`
- Mailpit: `http://localhost:8025`
- Flower: `http://localhost:5555`

## Create a superuser

```powershell
docker compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser
```

## Manual auth flow check

1. Open `http://localhost:3000/register`.
2. Register with a new email and password.
3. Open `http://localhost:8025` and find the verification email.
4. Follow the verification link.
5. Confirm you land in an authenticated frontend state.
6. Sign out.
7. Open `http://localhost:3000/login`.
8. Sign in with the same credentials.
9. Reload the page and confirm the session persists.
10. Open a protected page while signed out and confirm redirect to login.

## Showcase check

1. Open `http://localhost:3001`.
2. Navigate through the full-version showcase (e.g. `/en/dashboards/crm`).
3. Confirm no sign-in is required.
4. Open the browser DevTools network panel and confirm zero requests hit
   `/api/` or `/_allauth/` paths.
5. Stop the Django container (`docker compose -f docker-compose.local.yml stop django`)
   and confirm the showcase keeps rendering and navigating; restart Django when done.

## Quality checks

Backend (host with `uv` and MSVC build tools, or inside Docker):

```powershell
uv run ruff check . --fix
uv run ruff format .
uv run mypy seopartnerhub config
uv run pytest
```

Without MSVC build tools on Windows, run ruff via `uvx` (no project deps):

```powershell
uvx ruff@latest check config seopartnerhub
uvx ruff@latest format --check config seopartnerhub
```

Or run the full pipeline inside Docker:

```powershell
docker compose -f docker-compose.local.yml run --rm django ruff check . --fix
docker compose -f docker-compose.local.yml run --rm django ruff format .
docker compose -f docker-compose.local.yml run --rm django mypy seopartnerhub config
docker compose -f docker-compose.local.yml run --rm django pytest
```

Starter frontend (inside the running container, since pnpm and node_modules live there):

```powershell
docker compose -f docker-compose.local.yml exec frontend_starter pnpm lint
docker compose -f docker-compose.local.yml exec frontend_starter pnpm typecheck
docker compose -f docker-compose.local.yml exec frontend_starter pnpm build
```

Full-version frontend:

```powershell
docker compose -f docker-compose.local.yml exec frontend_full pnpm lint
docker compose -f docker-compose.local.yml exec frontend_full pnpm typecheck
docker compose -f docker-compose.local.yml exec frontend_full pnpm build
```

## Implementation notes

- Do not add custom auth endpoints.
- Do not introduce bearer tokens.
- Do not connect `frontend/full-version` to Django.
- Keep MFA and RBAC out of v1.
- Keep lockout threshold and duration configurable.
