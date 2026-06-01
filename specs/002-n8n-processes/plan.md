# Implementation Plan: n8n Processes Management

**Branch**: `002-n8n-processes` | **Date**: 2026-06-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/002-n8n-processes/spec.md`

## Summary

Add a backend-only Django app named `seopartnerhub.n8n` that lets authenticated users list automation processes, view and update each process's JSON settings, trigger a process manually through an n8n webhook, and inspect run history/results.

Technical approach:

- Store `Process` and `ProcessRun` locally in Postgres so the frontend has a stable API independent of n8n's internal workflow/execution APIs.
- Trigger n8n through per-process webhook paths (`N8N_BASE_URL` + `webhook_path`) and send `{runId, settings}` as JSON.
- Receive completion callbacks at a Django callback endpoint protected by HMAC-SHA256 over the raw request body.
- Validate `settings_json` with one typed Pydantic schema per `ProcessKind`; v1 ships `telegram_post`.
- Wire scheduled runs through `django-celery-beat` using a 5-field cron expression on `Process`.
- Keep business logic in service classes and expose only thin DRF viewsets/endpoints.

## Technical Context

**Language/Version**: Python 3.14; Django 6.0.5; Django REST Framework 3.17.1.

**Primary Dependencies**: Existing: Django, DRF, drf-spectacular, Celery 5.6.3, django-celery-beat 2.9.0, Redis 8, Postgres 18. New runtime deps planned: `httpx` for outbound webhook calls and `pydantic` for typed process settings schemas.

**Storage**: Existing Postgres database for `Process` and `ProcessRun`; Redis remains Celery broker/result backend; n8n stores its own SQLite state in the Docker volume added earlier.

**Testing**: `uv run pytest seopartnerhub/n8n/tests`, `uv run ruff check .`, `uv run mypy seopartnerhub config`. Endpoint tests use DRF test client/APIRequestFactory and mocked n8n webhook adapter; no real n8n or Telegram call in tests.

**Target Platform**: Linux-compatible Docker containers and local Windows developer host through Docker/uv.

**Project Type**: Django web service backend app with DRF API endpoints and Celery background tasks.

**Performance Goals**: Process list returns within 1 second on a dev machine with warm DB; manual trigger creates a `ProcessRun` within 1 second before external completion; config save/read roundtrip under 2 seconds.

**Constraints**: No frontend work in this feature; all endpoints require authenticated users except the HMAC-protected callback; no `typing.Any`; no `print()`; business logic lives in service classes; settings/env values are read only in `config/settings/*`.

**Scale/Scope**: Internal SEO/BizDev tool; v1 supports one process kind (`telegram_post`) and a small operator audience. Design supports additional process kinds by adding schemas/services without changing existing endpoint shapes.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Article | Gate | Status | Notes |
| ------- | ---- | ------ | ----- |
| I. Class-Based & Clean Architecture | Business logic in service classes; views only translate HTTP | PASS | New app uses `services/`, `selectors/`, `integrations/`, and thin DRF viewsets. |
| II. Strict Typing | No `typing.Any`; public methods typed; mypy target preserved | PASS | Pydantic schemas use concrete JSON value types; protocols type injected adapters. |
| III. Configuration | Runtime values in settings/env only | PASS | `N8N_BASE_URL`, callback secret, request timeout, and run timeout live in settings. |
| IV. Logging Discipline | Structured stdlib logging, no `print()` | PASS | Trigger, completion, validation rejection, and unknown callback events are logged. |
| V. Error Handling | Expected outcomes use explicit result states; Celery tasks idempotent | PASS | Deactivated/validation/network failures map to structured API responses or run states. |
| VI. External Library & API Lookup | Version-sensitive API docs checked | PASS | DRF ViewSet actions, Pydantic models, and HTTPX POST/timeout/error behavior checked from official docs; django-celery-beat details already present in project settings and will be rechecked if signatures are needed during implementation. |
| VII. Documentation & Spec Sync | Feature artifacts and docs updated | PASS | Plan creates research/data-model/contracts/quickstart and updates active plan pointer. |
| VIII. Security & Permissions | Authenticated endpoints; external input validated | PASS | DRF endpoints use authenticated access; callback uses HMAC; settings JSON validated before services act on it. |
| IX. Quality Gates | Backend quality commands identified | PASS | Plan lists ruff, mypy, and endpoint pytest targets. |
| X. Frontend Integration | Starter-kit remains future backend client; full-version isolated | PASS | Backend contract is documented; no frontend code changes in this feature. |

## Project Structure

### Documentation (this feature)

```text
specs/002-n8n-processes/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── api.openapi.yaml
│   └── callback-contract.md
└── tasks.md
```

### Source Code (repository root)
```text
config/
├── api_router.py
└── settings/
    ├── base.py
    └── test.py

seopartnerhub/
└── n8n/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── api/
    │   ├── serializers/
    │   │   ├── process_detail_serializer.py
    │   │   ├── process_list_serializer.py
    │   │   ├── process_run_serializer.py
    │   │   └── process_update_serializer.py
    │   └── views/
    │       ├── n8n_callback_view.py
    │       ├── process_run_view_set.py
    │       └── process_view_set.py
    ├── integrations/
    │   ├── n8n_webhook_client.py
    │   └── webhook_trigger.py
    ├── models/
    │   ├── process.py
    │   └── process_run.py
    ├── schemas/
    │   ├── process_kind.py
    │   ├── json_value.py
    │   ├── schema_registry.py
    │   └── telegram_post_settings.py
    ├── selectors/
    │   ├── process_selector.py
    │   └── process_run_selector.py
    ├── services/
    │   ├── process_configuration_service.py
    │   ├── process_run_callback_service.py
    │   ├── process_trigger_service.py
    │   ├── process_timeout_service.py
    │   └── sample_process_bootstrap_service.py
    ├── tasks/
    │   ├── trigger_scheduled_process.py
    │   └── mark_timed_out_process_runs.py
    ├── migrations/
    └── tests/
        ├── api/
        │   └── test_process_endpoints.py
        ├── services/
        │   └── test_process_services.py
        └── factories.py
```

**Structure Decision**: Create a dedicated `seopartnerhub/n8n/` Django app because the user explicitly selected that app name and this feature is scoped to n8n process management. Keep all business behavior in class-based services; DRF viewsets call services/selectors only. Do not add frontend files in this iteration.

## Complexity Tracking

No constitution violations.

## Phase 0 Output

See [research.md](./research.md). All research decisions are resolved; there are no remaining `NEEDS CLARIFICATION` markers.

## Phase 1 Output

- [data-model.md](./data-model.md)
- [quickstart.md](./quickstart.md)
- [contracts/api.openapi.yaml](./contracts/api.openapi.yaml)
- [contracts/callback-contract.md](./contracts/callback-contract.md)

## Post-Design Constitution Check

Re-evaluated after Phase 1 design: PASS. The design preserves the required layer direction (`api/ -> services/ -> selectors + models + integrations(protocol)`), uses injected protocol-based n8n clients, keeps all runtime values in settings, and avoids frontend changes in this backend-only iteration.
