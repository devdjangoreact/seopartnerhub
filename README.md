# SEOPartnerHub

Internal tool for SEO and BizDev teams. Automates outreach, link-building and partnership management. Dashboards provide analytics on deals and team performance.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

License: MIT

## Settings

Moved to [settings](https://cookiecutter-django.readthedocs.io/en/latest/1-getting-started/settings.html).

## Quick start

One-command local stack (Django + Postgres + Redis + Celery + Mailpit + two Next.js frontends):

```bash
docker compose -f docker-compose.local.yml up --build
```

Local URLs:

- Django backend: http://127.0.0.1:8000
- Starter frontend (wired to Django, MVP target): http://127.0.0.1:3000
- Full-version showcase (component donor, backend-free): http://127.0.0.1:3001
- Mailpit (email viewer): http://127.0.0.1:8025
- Flower (Celery): http://127.0.0.1:5555
- n8n editor: http://127.0.0.1:5678

See `readme_start.md` for the developer quick start and `readme_spec.md` for the project constitution.

## n8n process management

The `seopartnerhub.n8n` Django app exposes authenticated DRF endpoints to manage
n8n-driven automation processes (currently the canonical Telegram-post sample):

- `GET /api/n8n/processes/` and `GET /api/n8n/processes/{id}/`
- `PATCH /api/n8n/processes/{id}/` (typed validation per `ProcessKind` via Pydantic)
- `POST /api/n8n/processes/{id}/trigger/` (manual run, also available via Django admin action)
- `GET /api/n8n/processes/{id}/runs/` and `GET /api/n8n/runs/{run_id}/` for run history
- `POST /api/n8n/callbacks/runs/` for HMAC-SHA256 signed completion callbacks from n8n

Required Django settings (envs read in `config/settings/base.py`):

| Key | Default | Purpose |
| --- | --- | --- |
| `N8N_BASE_URL` | `http://n8n:5678` | n8n service base URL |
| `N8N_WEBHOOK_BASE_URL` | `http://n8n:5678/webhook` | Joined with `Process.webhook_path` to trigger workflows |
| `N8N_CALLBACK_HMAC_SECRET` | dev-only | Shared secret for inbound `X-Signature` callbacks |
| `N8N_REQUEST_TIMEOUT_SECONDS` | `10` | HTTPX timeout for outbound triggers |
| `N8N_PROCESS_RUN_TIMEOUT_SECONDS` | `900` | Sweep threshold for stale `running` runs |

## Frontend integration

- `frontend/starter-kit/` is the product UI. It uses django-allauth headless browser endpoints
  under `/_allauth/browser/v1/...` via Next.js rewrites for same-origin auth.
- `frontend/full-version/` is a Vuexy component **donor / showcase**. It is fully browsable
  without an account and does not call the Django backend. Components are copied from here into
  `frontend/starter-kit/` as features land.
- Auth is session-cookie based. No bearer tokens. For DRF endpoints, the starter-kit uses the same
  Django session via `SessionAuthentication`; raw DRF token auth is reserved for admin / scripts
  and not used by the product UI.

## Basic Commands

### Setting Up Your Users

- To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you'll see a "Verify Your E-mail Address" page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user's email should be verified and ready to go.

- To create a **superuser account**, use this command:

      uv run python manage.py createsuperuser

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Type checks

Running type checks with mypy:

    uv run mypy seopartnerhub

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    uv run coverage run -m pytest
    uv run coverage html
    uv run open htmlcov/index.html

#### Running tests with pytest

    uv run pytest

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/2-local-development/developing-locally.html#using-webpack-or-gulp).

### Celery

This app comes with Celery.

To run a celery worker:

```bash
cd seopartnerhub
uv run celery -A config.celery_app worker -l info
```

Please note: For Celery's import magic to work, it is important _where_ the celery commands are run. If you are in the same folder with _manage.py_, you should be right.

To run [periodic tasks](https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html), you'll need to start the celery beat scheduler service. You can start it as a standalone process:

```bash
cd seopartnerhub
uv run celery -A config.celery_app beat
```

or you can embed the beat service inside a worker with the `-B` option (not recommended for production use):

```bash
cd seopartnerhub
uv run celery -A config.celery_app worker -B -l info
```

### Email Server

In development, it is often nice to be able to see emails that are being sent from your application. For that reason local SMTP server [Mailpit](https://github.com/axllent/mailpit) with a web interface is available as docker container.

Container mailpit will start automatically when you will run all docker containers.
Please check [cookiecutter-django Docker documentation](https://cookiecutter-django.readthedocs.io/en/latest/2-local-development/developing-locally-docker.html) for more details how to start all containers.

With Mailpit running, to view messages that are sent by your application, open your browser and go to `http://127.0.0.1:8025`

## Deployment

The following details how to deploy this application.

### Docker

See detailed [cookiecutter-django Docker documentation](https://cookiecutter-django.readthedocs.io/en/latest/3-deployment/deployment-with-docker.html).
