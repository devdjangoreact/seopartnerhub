# Contract: Local Frontend Docker

## Services

`docker-compose.local.yml` exposes two frontend services.

| Service | Source | Port | Backend access |
| ------- | ------ | ---- | -------------- |
| `frontend_starter` | `frontend/starter-kit/` | `3000:3000` | Yes |
| `frontend_full` | `frontend/full-version/` | `3001:3000` | No |

## Shared Dockerfile

Path:

```text
compose/local/frontend/Dockerfile
```

Required behavior:

- Base image: `node:20-alpine`.
- Enable pnpm through Corepack.
- Accept build argument `FRONTEND_DIR`.
- Install dependencies from the selected frontend directory's lockfile.
- Run `pnpm dev --hostname 0.0.0.0 --port 3000` in dev mode.

## Volumes

Use separate dependency volumes:

```text
seopartnerhub_frontend_starter_node_modules
seopartnerhub_frontend_full_node_modules
```

Do not share `node_modules` between starter-kit and full-version.

## Environment

`frontend_starter`:

```text
NEXT_PUBLIC_SITE_URL=http://localhost:3000
NEXT_PUBLIC_DJANGO_URL=http://localhost:8000
DJANGO_INTERNAL_URL=http://django:8000
```

`frontend_full`:

```text
NEXT_PUBLIC_SITE_URL=http://localhost:3001
```

`frontend_full` must not receive backend URLs.

## Health / Manual Verification

After `docker compose -f docker-compose.local.yml up --build`:

- `http://localhost:3000` renders the starter-kit product UI.
- `http://localhost:3001` renders the full-version showcase.
- `http://localhost:8000` renders Django.
- `http://localhost:8025` renders Mailpit.
- `http://localhost:5555` renders Flower.

## Failure Contract

- If Django is down, `frontend_starter` shows a user-friendly unavailable state for auth/API calls.
- `frontend_full` remains browsable even if Django is down.
