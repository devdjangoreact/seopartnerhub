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
2. Navigate through the full-version showcase.
3. Confirm no sign-in is required.
4. Confirm network requests do not call `/api/` or `/_allauth/`.

## Quality checks

Backend:

```powershell
uv run ruff check . --fix
uv run ruff format .
uv run mypy seopartnerhub config
uv run pytest
```

Starter frontend:

```powershell
cd frontend/starter-kit
pnpm lint
pnpm typecheck
pnpm build
```

Full-version frontend:

```powershell
cd frontend/full-version
pnpm lint
pnpm typecheck
pnpm build
```

## Implementation notes

- Do not add custom auth endpoints.
- Do not introduce bearer tokens.
- Do not connect `frontend/full-version` to Django.
- Keep MFA and RBAC out of v1.
- Keep lockout threshold and duration configurable.
