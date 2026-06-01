# Tasks: n8n Processes Management

**Input**: Design documents from `specs/002-n8n-processes/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Required. The user explicitly requested endpoint tests for this backend feature.

**Organization**: Tasks are grouped by user story so each story can be implemented and tested independently after the foundational phase.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Every task includes exact file paths

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add dependencies and create the Django app skeleton needed by all stories.

- [X] T001 Add runtime dependencies `httpx` and `pydantic` to `pyproject.toml`
- [X] T002 Run dependency lock/update for `uv.lock`
- [X] T003 Create Django app package skeleton in `seopartnerhub/n8n/`
- [X] T004 Add `N8nConfig` in `seopartnerhub/n8n/apps.py`
- [X] T005 Register `seopartnerhub.n8n` in `LOCAL_APPS` in `config/settings/base.py`
- [X] T006 Add n8n runtime settings in `config/settings/base.py` (`N8N_BASE_URL`, `N8N_WEBHOOK_BASE_URL`, `N8N_CALLBACK_HMAC_SECRET`, `N8N_REQUEST_TIMEOUT_SECONDS`, `N8N_PROCESS_RUN_TIMEOUT_SECONDS`)
- [X] T007 [P] Create package initializers for `seopartnerhub/n8n/api/`, `seopartnerhub/n8n/api/serializers/`, `seopartnerhub/n8n/api/views/`, `seopartnerhub/n8n/models/`, `seopartnerhub/n8n/schemas/`, `seopartnerhub/n8n/selectors/`, `seopartnerhub/n8n/services/`, `seopartnerhub/n8n/integrations/`, `seopartnerhub/n8n/tasks/`, and `seopartnerhub/n8n/tests/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Build core data, schemas, integration abstractions, routing, and test fixtures used by every user story.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T008 Create `ProcessKind` enum in `seopartnerhub/n8n/schemas/process_kind.py`
- [X] T009 Create strict JSON type aliases without `typing.Any` in `seopartnerhub/n8n/schemas/json_value.py`
- [X] T010 Create `TelegramPostSettings` Pydantic schema in `seopartnerhub/n8n/schemas/telegram_post_settings.py`
- [X] T011 Create schema registry in `seopartnerhub/n8n/schemas/schema_registry.py`
- [X] T012 Create `Process` model in `seopartnerhub/n8n/models/process.py`
- [X] T013 Create `ProcessRun` model in `seopartnerhub/n8n/models/process_run.py`
- [X] T014 Export models in `seopartnerhub/n8n/models/__init__.py`
- [X] T015 Create initial migration for `Process` and `ProcessRun` in `seopartnerhub/n8n/migrations/0001_initial.py`
- [X] T016 Create n8n webhook trigger protocol in `seopartnerhub/n8n/integrations/webhook_trigger.py`
- [X] T017 Create HTTPX webhook client in `seopartnerhub/n8n/integrations/n8n_webhook_client.py`
- [X] T018 Create process selector in `seopartnerhub/n8n/selectors/process_selector.py`
- [X] T019 Create process run selector in `seopartnerhub/n8n/selectors/process_run_selector.py`
- [X] T020 Create test factories for users, processes, and runs in `seopartnerhub/n8n/tests/factories.py`
- [X] T021 Register `ProcessViewSet` and `ProcessRunViewSet` routes in `config/api_router.py`
- [X] T022 Add callback URL include/path for `/api/n8n/callbacks/runs/` in `config/urls.py`
- [X] T023 Register models in Django admin in `seopartnerhub/n8n/admin.py`

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Browse automation processes (Priority: P1) MVP

**Goal**: Authenticated users can list processes and retrieve one process with latest-run summary.

**Independent Test**: A seeded workspace returns a non-empty process list and process detail to an authenticated user; unauthenticated access is rejected.

### Tests for User Story 1

- [X] T024 [P] [US1] Add endpoint tests for unauthenticated process list/retrieve rejection in `seopartnerhub/n8n/tests/api/test_process_endpoints.py`
- [X] T025 [P] [US1] Add endpoint tests for authenticated process list with latest run summary in `seopartnerhub/n8n/tests/api/test_process_endpoints.py`
- [X] T026 [P] [US1] Add endpoint tests for authenticated process retrieve with settings and latest run summary in `seopartnerhub/n8n/tests/api/test_process_endpoints.py`

### Implementation for User Story 1

- [X] T027 [US1] Create `ProcessListSerializer` in `seopartnerhub/n8n/api/serializers/process_list_serializer.py`
- [X] T028 [US1] Create `ProcessDetailSerializer` in `seopartnerhub/n8n/api/serializers/process_detail_serializer.py`
- [X] T029 [US1] Create `ProcessViewSet` with `list` and `retrieve` actions in `seopartnerhub/n8n/api/views/process_view_set.py`
- [X] T030 [US1] Add latest-run summary query support to `seopartnerhub/n8n/selectors/process_selector.py`
- [X] T031 [US1] Export serializers/views from `seopartnerhub/n8n/api/serializers/__init__.py` and `seopartnerhub/n8n/api/views/__init__.py`

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - View and edit process configuration (Priority: P1)

**Goal**: Authenticated users can update a process's JSON settings and mutable metadata with field-level validation.

**Independent Test**: A user patches valid Telegram settings and re-fetches the process; invalid settings return field-level errors and preserve the previous value.

### Tests for User Story 2

- [X] T032 [P] [US2] Add endpoint test for valid settings update in `seopartnerhub/n8n/tests/api/test_process_endpoints.py`
- [X] T033 [P] [US2] Add endpoint test for invalid Telegram settings rejection in `seopartnerhub/n8n/tests/api/test_process_endpoints.py`
- [X] T034 [P] [US2] Add service tests for schema validation and previous-settings preservation in `seopartnerhub/n8n/tests/services/test_process_services.py`

### Implementation for User Story 2

- [X] T035 [US2] Create `ProcessUpdateSerializer` in `seopartnerhub/n8n/api/serializers/process_update_serializer.py`
- [X] T036 [US2] Create `ProcessConfigurationService` in `seopartnerhub/n8n/services/process_configuration_service.py`
- [X] T037 [US2] Add `partial_update` support to `ProcessViewSet` in `seopartnerhub/n8n/api/views/process_view_set.py`
- [X] T038 [US2] Add structured validation rejection logging in `seopartnerhub/n8n/services/process_configuration_service.py`

**Checkpoint**: User Stories 1 and 2 are independently functional.

---

## Phase 5: User Story 3 - Manually trigger a process and watch result (Priority: P2)

**Goal**: Authenticated users can trigger active processes, inspect runs, and n8n can complete runs via HMAC callback.

**Independent Test**: A trigger creates a `running` run and calls the injected webhook client; a signed callback transitions the run to `succeeded`/`failed`; run history returns newest first.

### Tests for User Story 3

- [X] T039 [P] [US3] Add endpoint test for manual trigger creating a running run in `seopartnerhub/n8n/tests/api/test_process_endpoints.py`
- [X] T040 [P] [US3] Add endpoint test for deactivated process trigger rejection in `seopartnerhub/n8n/tests/api/test_process_endpoints.py`
- [X] T041 [P] [US3] Add endpoint tests for process run retrieve and process run history in `seopartnerhub/n8n/tests/api/test_process_endpoints.py`
- [X] T042 [P] [US3] Add callback endpoint tests for valid HMAC success/failure payloads in `seopartnerhub/n8n/tests/api/test_process_endpoints.py`
- [X] T043 [P] [US3] Add callback endpoint tests for invalid signature and unknown run rejection in `seopartnerhub/n8n/tests/api/test_process_endpoints.py`
- [X] T044 [P] [US3] Add service tests for trigger network failure and timeout handling in `seopartnerhub/n8n/tests/services/test_process_services.py`

### Implementation for User Story 3

- [X] T045 [US3] Create `ProcessRunSerializer` in `seopartnerhub/n8n/api/serializers/process_run_serializer.py`
- [X] T046 [US3] Create `ProcessTriggerService` in `seopartnerhub/n8n/services/process_trigger_service.py`
- [X] T047 [US3] Add `trigger` detail action to `ProcessViewSet` in `seopartnerhub/n8n/api/views/process_view_set.py`
- [X] T048 [US3] Create `ProcessRunViewSet` in `seopartnerhub/n8n/api/views/process_run_view_set.py`
- [X] T049 [US3] Add process-specific `runs` action to `ProcessViewSet` in `seopartnerhub/n8n/api/views/process_view_set.py`
- [X] T050 [US3] Create HMAC verification and run completion logic in `seopartnerhub/n8n/services/process_run_callback_service.py`
- [X] T051 [US3] Create `N8nCallbackView` in `seopartnerhub/n8n/api/views/n8n_callback_view.py`
- [X] T052 [US3] Create timeout service in `seopartnerhub/n8n/services/process_timeout_service.py`
- [X] T053 [US3] Create timeout Celery task in `seopartnerhub/n8n/tasks/mark_timed_out_process_runs.py`
- [X] T054 [US3] Add structured trigger, completion, network failure, unknown callback, and timeout logging in `seopartnerhub/n8n/services/`

**Checkpoint**: User Stories 1, 2, and 3 are independently functional.

---

## Phase 6: User Story 4 - Sample Telegram-post process available out of the box (Priority: P3)

**Goal**: Fresh workspaces include the canonical `Telegram post via BotFather` sample process.

**Independent Test**: After migrations/bootstrap, the process list includes the Telegram sample and its settings match the Telegram schema.

### Tests for User Story 4

- [X] T055 [P] [US4] Add service test for idempotent Telegram sample bootstrap in `seopartnerhub/n8n/tests/services/test_process_services.py`
- [X] T056 [P] [US4] Add endpoint test proving sample process appears in list after bootstrap in `seopartnerhub/n8n/tests/api/test_process_endpoints.py`

### Implementation for User Story 4

- [X] T057 [US4] Create `SampleProcessBootstrapService` in `seopartnerhub/n8n/services/sample_process_bootstrap_service.py`
- [X] T058 [US4] Add sample process data migration in `seopartnerhub/n8n/migrations/0002_seed_telegram_post_process.py`
- [X] T059 [US4] Document sample webhook path and required Telegram settings in `specs/002-n8n-processes/quickstart.md`

**Checkpoint**: All user stories are independently functional.

---

## Phase 7: Scheduled Runs & Cross-Story Integration

**Purpose**: Wire cron scheduling promised by the feature into Redis/Celery after core manual flows are working.

- [X] T060 Create scheduled trigger Celery task in `seopartnerhub/n8n/tasks/trigger_scheduled_process.py`
- [X] T061 Create django-celery-beat synchronization logic for `Process.schedule_cron` in `seopartnerhub/n8n/services/process_configuration_service.py`
- [X] T062 Add tests for cron schedule validation and beat synchronization in `seopartnerhub/n8n/tests/services/test_process_services.py`
- [X] T063 Register n8n tasks package exports in `seopartnerhub/n8n/tasks/__init__.py`

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Docs, schema, quality checks, and project-wide sync after implementation.

- [X] T064 Update OpenAPI expectations in `specs/002-n8n-processes/contracts/api.openapi.yaml` if implementation changes response field names
- [X] T065 Update `README.md` with n8n backend API, settings, and local run notes
- [X] T066 Update `readme_start.md` with n8n URL, backend endpoint smoke flow, and required settings
- [X] T067 Update `AGENTS.md` paths table if new `seopartnerhub/n8n/` app paths need to be listed
- [X] T068 Update `.cursor/rules/architecture.mdc` if the new `n8n` app introduces new layer examples
- [X] T069 Run `uv run ruff check seopartnerhub/n8n config`
- [X] T070 Run `uv run mypy seopartnerhub config`
- [X] T071 Run `uv run pytest seopartnerhub/n8n/tests`
- [X] T072 Run `uv run python manage.py spectacular --file schema.yml --validate` if available, or otherwise verify `/api/schema/` includes the n8n endpoints

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup and blocks all user stories.
- **US1 (Phase 3)**: Depends on Foundational; MVP.
- **US2 (Phase 4)**: Depends on Foundational and can run after US1 serializers/selectors exist; independently testable once process detail exists.
- **US3 (Phase 5)**: Depends on Foundational and uses `Process`/`ProcessRun`; benefits from US1/US2 but is independently testable with factories.
- **US4 (Phase 6)**: Depends on Foundational; can be implemented once `Process` and schema registry exist.
- **Scheduled Runs (Phase 7)**: Depends on US2/US3 because it uses config saves and trigger service.
- **Polish (Phase 8)**: Depends on desired implementation phases being complete.

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on other stories after Foundational.
- **User Story 2 (P1)**: Uses the process detail surface from US1 but can be validated independently with a single process fixture.
- **User Story 3 (P2)**: Uses `Process` and `ProcessRun`; can be validated with service fakes and endpoint tests.
- **User Story 4 (P3)**: Uses `Process` and settings schemas; no dependency on trigger/callback completion.

### Within Each User Story

- Tests first; they should fail before implementation.
- Models/schemas before services.
- Services before endpoints.
- Endpoint wiring before OpenAPI/schema validation.
- Logging and error handling complete before story checkpoint.

---

## Parallel Opportunities

- T007 can run in parallel with settings/dependency edits after T003.
- T008-T011 can run in parallel with T016-T019 after package skeleton exists.
- T024-T026 can be written in parallel before US1 implementation.
- T032-T034 can be written in parallel before US2 implementation.
- T039-T044 can be written in parallel before US3 implementation.
- T055-T056 can be written in parallel before US4 implementation.
- Documentation tasks T065-T068 can run in parallel after implementation stabilizes.

---

## Parallel Example: User Story 3

```bash
Task: "Add endpoint test for manual trigger creating a running run in seopartnerhub/n8n/tests/api/test_process_endpoints.py"
Task: "Add endpoint tests for valid HMAC success/failure callbacks in seopartnerhub/n8n/tests/api/test_process_endpoints.py"
Task: "Add service tests for trigger network failure and timeout handling in seopartnerhub/n8n/tests/services/test_process_services.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Stop and validate list/retrieve endpoints with authenticated and unauthenticated tests.
4. Demo MVP: authenticated process visibility with latest-run summary.

### Incremental Delivery

1. Foundation -> US1 list/retrieve.
2. Add US2 settings update/validation.
3. Add US3 trigger, callback, and run history.
4. Add US4 sample process.
5. Add scheduled execution and final docs/quality checks.

### Notes

- Do not introduce frontend files in this feature.
- Do not use `typing.Any`; use the JSON value aliases from `seopartnerhub/n8n/schemas/json_value.py`.
- Keep one public class per file in the new app.
- Use module-level `logger = logging.getLogger(__name__)` and static log event names.
- Use injected protocols/fakes for n8n webhook tests; never call real n8n or Telegram in tests.
