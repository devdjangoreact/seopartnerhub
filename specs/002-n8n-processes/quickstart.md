# Quickstart: n8n Processes Management

This quickstart describes how to validate the backend feature after `/speckit-implement` completes.

## Prerequisites

- Docker local stack is configured with `n8n` in `docker-compose.local.yml`.
- Django settings expose:
  - `N8N_BASE_URL=http://n8n:5678`
  - `N8N_WEBHOOK_BASE_URL=http://n8n:5678/webhook`
  - `N8N_CALLBACK_HMAC_SECRET=<shared secret>`
  - `N8N_PROCESS_RUN_TIMEOUT_SECONDS=900`
- The database has migrations applied.
- An authenticated user exists.

## Apply Backend Setup

```bash
uv sync
uv run python manage.py migrate
```

The migration/bootstrap step should create the sample process:

```text
Telegram post via BotFather
```

## Start Local Services

```bash
docker compose -f docker-compose.local.yml up --build
```

Relevant URLs:

- Django: `http://localhost:8000`
- n8n: `http://localhost:5678`
- Flower: `http://localhost:5555`

## API Smoke Flow

All `/api/n8n/...` endpoints require the existing authenticated browser session or DRF token auth.

1. List processes:

   ```http
   GET /api/n8n/processes/
   ```

   Expected: `200 OK` and at least one process named `Telegram post via BotFather`.

2. Retrieve the sample process:

   ```http
   GET /api/n8n/processes/{id}/
   ```

   Expected: settings include `chatId`/`chat_id` equivalent represented by the backend contract, message text, and optional parse mode.

3. Update settings:

   ```http
   PATCH /api/n8n/processes/{id}/
   Content-Type: application/json

   {
     "settings_json": {
       "chat_id": "-100111222333",
       "message": "SEOPartnerHub test post",
       "parse_mode": "HTML",
       "disable_web_page_preview": false
     }
   }
   ```

   Expected: `200 OK` and the persisted settings are returned.

4. Trigger manually:

   ```http
   POST /api/n8n/processes/{id}/trigger/
   ```

   Expected: `201 Created` and a `ProcessRun` in `running` state.

5. Simulate n8n callback in tests/dev:

   ```http
   POST /api/n8n/callbacks/runs/
   X-Signature: <hmac-sha256-over-raw-body>
   Content-Type: application/json

   {
     "runId": "<run-id>",
     "status": "succeeded",
     "result": {
       "telegram_message_id": 12345
     }
   }
   ```

   Expected: `200 OK`; retrieving the run returns `succeeded`.

6. List run history:

   ```http
   GET /api/n8n/processes/{id}/runs/
   ```

   Expected: newest run appears first with status and result.

7. Retrieve a single run:

   ```http
   GET /api/n8n/runs/{run_id}/
   ```

## Sample Process Webhook Path

The Telegram-post sample process is seeded with `webhook_path = /seopartnerhub/telegram-post`. Configure the corresponding n8n workflow with a Webhook trigger node listening on the same path, and ensure the workflow:

- accepts a JSON body with `run_id`, `process_id`, `settings.chat_id`, `settings.message`,
  `settings.parse_mode`, `settings.disable_web_page_preview`;
- sends a Telegram message via a BotFather bot using those settings;
- POSTs the completion callback to `${DJANGO_URL}/api/n8n/callbacks/runs/` with header
  `X-Signature: <hex hmac-sha256 over the raw body using N8N_CALLBACK_HMAC_SECRET>`.

## Endpoint Test Targets

Run only after the feature is implemented:

```bash
uv run pytest seopartnerhub/n8n/tests
uv run ruff check seopartnerhub/n8n config
uv run mypy seopartnerhub config
```

Run only after the feature is implemented:

```bash
uv run pytest seopartnerhub/n8n/tests
uv run ruff check seopartnerhub/n8n config
uv run mypy seopartnerhub config
```

## Expected Test Coverage

- Unauthenticated list/retrieve/update/trigger/run-history requests return auth errors.
- Authenticated users can list/retrieve processes.
- Settings update persists valid Telegram settings and rejects invalid settings with field-level errors.
- Manual trigger creates a `running` run and calls the injected webhook client with `{runId, settings}`.
- Deactivated processes cannot be triggered and do not create runs.
- HMAC callback marks known running runs as `succeeded` or `failed`.
- Missing/invalid signatures are rejected.
- Unknown run callbacks are rejected without state changes.
- Timeout task marks stale `running` runs as `timed_out`.
