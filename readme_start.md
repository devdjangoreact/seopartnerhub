# Quick start

## One-command local stack (Docker)

```powershell
docker compose -f docker-compose.local.yml up --build
docker compose -f docker-compose.local.yml down
docker compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser
```

## Local URLs

- Django backend: http://127.0.0.1:8000
- Starter frontend (MVP): http://127.0.0.1:3000
- Full-version showcase: http://127.0.0.1:3001
- Mailpit (email viewer): http://127.0.0.1:8025
- Flower (Celery): http://127.0.0.1:5555
- n8n editor: http://127.0.0.1:5678

## n8n backend smoke flow

Authenticated DRF endpoints (session or token auth):

```text
GET    /api/n8n/processes/           # list with latest-run summary
GET    /api/n8n/processes/{id}/      # detail with full settings_json
PATCH  /api/n8n/processes/{id}/      # update name / is_active / settings_json / webhook_path / schedule_cron
POST   /api/n8n/processes/{id}/trigger/   # manual trigger -> 201 + ProcessRun running
GET    /api/n8n/processes/{id}/runs/      # run history newest-first
GET    /api/n8n/runs/{run_id}/            # single run detail
POST   /api/n8n/callbacks/runs/           # n8n -> Django, X-Signature: HMAC-SHA256 over raw body
```

Required Django settings (already wired in `config/settings/base.py`,
overridable via env): `N8N_BASE_URL`, `N8N_WEBHOOK_BASE_URL`,
`N8N_CALLBACK_HMAC_SECRET`, `N8N_REQUEST_TIMEOUT_SECONDS`,
`N8N_PROCESS_RUN_TIMEOUT_SECONDS` (default 900).

## Frontend notes

- `frontend/starter-kit/` is the wired product UI. It calls Django via Next.js rewrites
  (`/_allauth/*`, `/api/*`).
- `frontend/full-version/` is the component **donor / showcase**. It is browsable as a standalone
  Next.js app and MUST NOT call Django. Components are copied into `starter-kit/` as features land.
- Both run from one shared image at `compose/local/frontend/Dockerfile` and use separate
  `node_modules` volumes.
- pnpm blocks dependency build scripts by default; the allow-list per app is set in each
  frontend's `pnpm-workspace.yaml` under `allowBuilds` so `pnpm install` in Docker is
  non-interactive (`esbuild`, `sharp` for starter-kit; plus `prisma`, `@prisma/engines`,
  `@prisma/client` for full-version).
- `frontend/full-version/` ships its own NextAuth + Prisma demo. It MUST NOT call Django.
  Required env vars live in `frontend/full-version/.env.example` (committed) and are seeded
  into `.env.local` (gitignored) automatically. On the host, copy them manually once:
  ```powershell
  Copy-Item frontend/full-version/.env.example frontend/full-version/.env.local
  ```
  In Docker, `compose/local/frontend/start` does the copy on the first run.

## Optional: run a frontend on the host (rarely needed)

Run from the project root. Requires Node 20+. If `pnpm` is missing, install it once
without admin via the standalone installer (then reopen the terminal):

```powershell
iwr https://get.pnpm.io/install.ps1 -useb | iex
```

**Starter-kit** (port 3000, talks to Django; backend must run at `http://localhost:8000`).
Seed host env on the first run (file is gitignored and not used in Docker — compose overrides
the same vars via `services.frontend_starter.environment:`):

```powershell
Copy-Item frontend/starter-kit/.env.example frontend/starter-kit/.env.local
```

Then start it:

```powershell
pnpm --dir frontend/starter-kit install; pnpm --dir frontend/starter-kit dev
```

**Full-version showcase** (port 3001, no backend, run in a second terminal):

```powershell
pnpm --dir frontend/full-version install; pnpm --dir frontend/full-version dev --port 3001
```

## End-to-end auth tests (Playwright, Python)

Runs against the live stack (Docker + host frontend on `:3000`). Uses the
system Chrome via `--browser-channel chrome`, no Chromium download. The
isolated `uvx` environment skips the host `psycopg-c` build.

```powershell
uvx --from pytest --with pytest-playwright pytest tests/e2e/ -v
```

Override the targets if needed:

```powershell
$env:E2E_FRONTEND_URL = "http://localhost:3000"; $env:E2E_MAILPIT_URL = "http://localhost:8025"; uvx --from pytest --with pytest-playwright pytest tests/e2e/ -v
```

Covered flows: registration (with confirm-password validation), email
verification via Mailpit, sign-in, password reset.
