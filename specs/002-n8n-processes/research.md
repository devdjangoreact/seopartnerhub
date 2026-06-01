# Research: n8n Processes Management

## Decision: Store process metadata and run history locally

**Decision**: Persist `Process` and `ProcessRun` in Django/Postgres instead of proxying n8n workflow/execution APIs directly.

**Rationale**: The frontend needs a stable, product-specific contract: process name, kind, settings JSON, activation, schedule, latest run, and run history. n8n's internal workflow/execution API is not the product contract and would couple the UI to n8n implementation details. Local state also lets the system show runs immediately after trigger creation, before n8n completes.

**Alternatives considered**:

- Pure n8n proxy: rejected because list/settings/results would depend on n8n API shape and auth.
- Hybrid local settings + n8n execution fetch: rejected for v1 because it creates two sources of truth for results.

## Decision: Trigger workflows through per-process webhooks

**Decision**: Each `Process` stores a workflow-specific webhook path. Manual and scheduled triggers issue HTTP POST to `N8N_BASE_URL + webhook_path` with a JSON payload containing the run identifier and validated settings snapshot.

**Rationale**: n8n webhook nodes are the natural entry point for workflow execution and do not require enabling n8n's public management API or storing a broad API key. This was selected in clarification Q1.

**Alternatives considered**:

- n8n REST workflow execute endpoint: rejected because it requires a global API credential and couples the app to n8n management API semantics.
- Hybrid webhook/API mode per process: rejected for v1 because it increases model complexity without immediate product value.

## Decision: Authenticate callbacks with HMAC-SHA256

**Decision**: n8n completion callbacks include an `X-Signature` header containing HMAC-SHA256 over the raw request body using `N8N_CALLBACK_HMAC_SECRET`.

**Rationale**: HMAC over the raw body is stateless, verifies payload integrity, avoids secrets in URLs, and is straightforward to test. It matches common webhook security patterns and was selected in clarification Q2.

**Alternatives considered**:

- Static bearer token: simpler but does not bind the token to the exact callback body.
- Per-run signed token: secure but adds token issuance and verification complexity for v1.
- Network allowlist only: rejected because it is brittle if n8n later runs outside the same Docker network.

## Decision: Use Pydantic schemas per process kind

**Decision**: Add `pydantic` and define one schema class per `ProcessKind`, initially `TelegramPostSettings`. A registry maps kind -> schema and the configuration service validates settings before persistence.

**Rationale**: The project constitution prefers typed data containers outside the ORM, and the user selected typed schemas during clarification. Pydantic's official docs describe `BaseModel` classes as annotated schemas for validation and serialization, with `model_validate()` and `model_dump()` methods suitable for this flow.

**Alternatives considered**:

- JSON Schema files: good for language-neutral validation, but weaker Python typing.
- Required-field lists: too shallow, no type/format validation.
- DRF serializers per kind: workable, but would couple domain settings validation to HTTP serializers instead of service/domain code.

## Decision: Use HTTPX for outbound webhook calls

**Decision**: Add `httpx` and inject an n8n webhook client into `ProcessTriggerService`.

**Rationale**: HTTPX official docs support JSON POST payloads, explicit timeouts, status handling with `raise_for_status()`, and typed exception classes (`RequestError`, `HTTPStatusError`) for network/status failures. This fits service-layer integration code and tests can substitute a protocol fake.

**Alternatives considered**:

- `requests`: not currently installed and less aligned with modern async-ready Python HTTP clients.
- stdlib `urllib`: avoids a dependency but produces more boilerplate and poorer ergonomics for JSON, timeouts, and status errors.

## Decision: Represent schedules as 5-field cron strings

**Decision**: `Process.schedule_cron` is nullable. A valid 5-field cron expression means scheduled execution is enabled; `NULL`/blank means manual-only.

**Rationale**: Cron is compact, familiar to operators, and maps well to `django-celery-beat`'s `CrontabSchedule`. The project already installs `django-celery-beat` and configures `DatabaseScheduler`.

**Alternatives considered**:

- Interval seconds only: too limited for daily/weekly business schedules.
- Both cron and interval: flexible, but unnecessary model complexity for v1.
- Scheduling out of scope: rejected because the user explicitly asked to support planned launches through Redis/Celery.

## Decision: Use a 15-minute default run timeout

**Decision**: Add `N8N_PROCESS_RUN_TIMEOUT_SECONDS` setting with default `900`.

**Rationale**: A Telegram post normally completes in seconds, but future n8n workflows may involve LLM calls, scraping, retries, or queueing. Fifteen minutes is long enough to avoid false timeouts for typical internal automations while still surfacing genuinely abandoned runs.

**Alternatives considered**:

- 5 minutes: faster failure signal but more likely to mark slow workflows as timed out.
- 60 minutes: avoids false positives but delays operator feedback too much.

## Decision: Expose DRF ViewSets and one callback APIView

**Decision**: Use DRF routers for process/run resources and detail actions for trigger/history; use a dedicated callback endpoint for HMAC-authenticated n8n completion callbacks.

**Rationale**: The current project registers DRF viewsets through `config/api_router.py`. DRF official docs recommend routers for viewsets and `@action(detail=True, methods=["post"])` for ad-hoc resource actions like a process trigger.

**Alternatives considered**:

- Plain Django views for everything: more explicit but inconsistent with current API style.
- One monolithic endpoint: rejected because list/retrieve/update/trigger/history have distinct HTTP semantics and test cases.
