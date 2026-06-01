# Feature Specification: n8n Processes Management

**Feature Branch**: `002-n8n-processes`

**Created**: 2026-06-01

**Status**: Draft

**Input**: User description: "Django app for managing n8n processes: list,
view/edit JSON settings, manually trigger, see run history. Telegram post via
BotFather as the canonical sample process. Backend-only at this stage with
endpoint tests."

## Clarifications

### Session 2026-06-01

- Q: Through which channel does the backend invoke the external automation engine when a user manually triggers a process? → A: Per-workflow webhook URL — each Process stores its own webhook path; trigger = HTTP POST on that path with `{run_id, settings}`; n8n public API is not used.
- Q: How does the backend authenticate completion callbacks from the external automation engine? → A: HMAC-SHA256 signature over the raw request body, sent in an `X-Signature` header, verified against a shared secret from configuration; nothing in the URL or unsigned headers is trusted.
- Q: How is a Process's optional schedule expressed? → A: A single optional cron expression field on the Process; presence of a valid cron value means the process runs on that schedule, absence means manual-only.
- Q: How is per-kind validation of a Process's configuration document expressed? → A: A typed schema model is registered for each Process kind (one schema per kind); saving a configuration runs the kind's schema and returns field-level errors when fields are missing, of the wrong type, or fail kind-specific constraints.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Browse automation processes (Priority: P1)

An authenticated team member opens the product and sees a list of all
automation processes available in the workspace. For each process they see a
human-readable name, what kind of work it performs (e.g. "Telegram post"),
its current activation status, and the timestamp + result of its most recent
run. From this list the user can drill into a single process to inspect its
configuration and history.

**Why this priority**: Without a discoverable list of processes, no other
capability (editing settings, manual run, viewing results) is reachable. This
is the entry point and the smallest demonstrable slice of value.

**Independent Test**: With a freshly seeded workspace (one or more sample
processes pre-created), an authenticated user calls the list endpoint and
receives a non-empty collection where each item carries name, kind,
activation flag, and a summary of the latest run (status + finished
timestamp, or "never run"). Delivers value: visibility into what automations
exist.

**Acceptance Scenarios**:

1. **Given** the workspace contains at least one process, **When** an
   authenticated user requests the process list, **Then** the response lists
   every process with name, kind, activation flag, and latest run summary.
2. **Given** an authenticated user knows a process identifier, **When** they
   request that single process, **Then** the response includes its full
   configuration document, activation status, optional schedule, and the
   most recent run summary.
3. **Given** an unauthenticated client, **When** it requests the process
   list, **Then** the request is rejected with an authentication error.

---

### User Story 2 - View and edit process configuration (Priority: P1)

An authenticated user opens a process and sees its full configuration as a
structured document (a JSON object such as Telegram chat id, message
template, parse mode). They can change values inside that document and save
the new version. Subsequent manual or scheduled runs of that process must
use the updated configuration.

**Why this priority**: Configuration is the operator's primary surface for
adapting an automation to a new audience, message, or partner without code
changes. It is independently testable from manual triggering and run
history, and is required before triggering returns useful behavior.

**Independent Test**: An authenticated user fetches a process, modifies its
configuration document, submits the change, and re-fetches the process. The
returned configuration matches the new value, and the process's
"last modified" metadata reflects the update. Delivers value: the operator
controls what each automation does without engineering involvement.

**Acceptance Scenarios**:

1. **Given** a process exists, **When** an authenticated user retrieves it,
   **Then** they see its configuration document as structured data they can
   read field-by-field.
2. **Given** an authenticated user has edited the configuration document,
   **When** they save the change, **Then** subsequent reads return the new
   document and a "last modified" timestamp newer than before.
3. **Given** a configuration document missing a field that the process kind
   requires (e.g. Telegram process without `chat_id`), **When** an
   authenticated user tries to save it, **Then** the save is rejected with a
   field-level validation error and the previous configuration is preserved.

---

### User Story 3 - Manually trigger a process and watch result (Priority: P2)

An authenticated user opens a process and triggers it on demand. The system
acknowledges the trigger immediately with a run identifier and an initial
"running" state. As the external automation engine executes the work and
reports back, the run transitions to "succeeded" or "failed" with a
human-readable result payload (and an error message on failure). The user
can fetch the run by its identifier or browse the process's recent run
history to see this and previous executions.

**Why this priority**: Triggering is the action that converts a configured
process into observable business output (an actually sent Telegram post,
etc.). It depends on US1+US2 (a process must exist and be configured) but
delivers the end-to-end value of the feature.

**Independent Test**: An authenticated user triggers a known sample process
and immediately receives a run identifier in "running" state. After the
external engine acknowledges completion (simulated via a callback in tests),
fetching the same run returns "succeeded" with a result payload, and the
run appears at the top of that process's run history. Delivers value: the
operator has launched real work and confirmed it ran.

**Acceptance Scenarios**:

1. **Given** a process is active and has valid configuration, **When** an
   authenticated user triggers it, **Then** the system records a new run in
   "running" state, returns its identifier, and reports it in the process's
   recent runs list.
2. **Given** a run is in progress, **When** the external automation engine
   reports completion through the system's callback channel, **Then** the
   stored run transitions to "succeeded" or "failed" and exposes a result
   payload (or error message) to authenticated readers.
3. **Given** a process is deactivated, **When** a user tries to trigger it,
   **Then** the trigger is rejected with a clear error and no run record is
   created.

---

### User Story 4 - Sample Telegram-post process available out of the box (Priority: P3)

When the product is installed, a working sample process named
"Telegram post via BotFather" already exists. Its configuration document
contains the fields a Telegram post requires (target chat identifier,
message text, optional formatting mode). Operators can use this sample to
verify the end-to-end flow (list → view configuration → edit → trigger →
see result) without first having to author a process from scratch.

**Why this priority**: A canonical, ready-to-use example is a documentation
and onboarding accelerator. It is independently testable: it must simply
exist and be operable through US1-US3.

**Independent Test**: On a freshly initialized workspace, the process list
contains the "Telegram post via BotFather" sample with a Telegram-shaped
configuration document; flows from US1-US3 work against it without any
prior setup.

**Acceptance Scenarios**:

1. **Given** a freshly initialized workspace, **When** an authenticated user
   lists processes, **Then** the "Telegram post via BotFather" sample is
   present.
2. **Given** the sample process, **When** an authenticated user retrieves
   its configuration, **Then** the document contains at least the fields
   needed to address a Telegram chat (target chat identifier and message
   text).

---

### Edge Cases

- An authenticated user submits a configuration document that is not a
  valid structured object (e.g. a string or a number). The system rejects
  the change with a typed validation error and preserves the prior version.
- The external automation engine is unreachable when the user triggers a
  process. The run is recorded as "failed" with a network/timeout error
  message, and the process itself remains usable for a later retry.
- The external engine reports completion for a run identifier that the
  system does not know about (e.g. stale callback). The callback is
  rejected without modifying any record.
- Two operators edit the same process's configuration concurrently. The
  later save wins; both edits are auditable through the "last modified"
  timestamp.
- A run remains in "running" state beyond a configurable timeout. The
  system marks it as "timed out" and stops awaiting further callbacks for
  that run.
- The configuration document includes a secret value (e.g. a bot token).
  Reads return the document as stored; the system does not invent
  encryption beyond what the storage layer provides at this stage.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a backend interface where an
  authenticated user can list every automation process in the workspace,
  including for each one: name, kind, activation status, optional schedule,
  and a summary of the latest run.
- **FR-002**: The system MUST expose a backend interface where an
  authenticated user can retrieve a single process by identifier and see
  its full configuration document, activation status, optional schedule,
  and last-modified timestamp.
- **FR-003**: The system MUST allow an authenticated user to update a
  process's configuration document through a backend interface, persisting
  the new document and updating the last-modified timestamp.
- **FR-004**: The system MUST validate that an updated configuration
  document is a structured object and that it contains the fields required
  by the process's kind, by running the kind's registered typed schema
  against the document and returning field-level error messages on
  failure (missing field, wrong type, kind-specific constraint
  violation), preserving the previous version. Each kind MUST have
  exactly one registered schema.
- **FR-005**: The system MUST allow an authenticated user to manually
  trigger an active process through a backend interface, immediately
  recording a new run in a "running" state and returning its identifier.
- **FR-006**: The system MUST forward each manual trigger to the external
  automation engine by issuing an HTTP POST to a workflow-specific webhook
  endpoint stored on the Process, sending the process's current
  configuration document and the run identifier as part of the request
  payload. The system MUST NOT depend on the external engine's public
  management API to start a run.
- **FR-007**: The system MUST refuse to trigger a process that is
  deactivated and MUST NOT create a run record in that case.
- **FR-008**: The system MUST expose a callback channel through which the
  external automation engine reports run completion, transitioning the
  matching run to "succeeded" or "failed" and storing a result payload (or
  error message) for later inspection.
- **FR-009**: The system MUST reject completion callbacks for unknown run
  identifiers without modifying any record.
- **FR-010**: The system MUST allow an authenticated user to retrieve a
  single run by identifier and to list the recent runs of a given process
  in reverse-chronological order, with pagination.
- **FR-011**: The system MUST mark runs that exceed a configurable
  in-progress timeout as "timed out" so that abandoned runs do not stay in
  a pending state forever.
- **FR-012**: The system MUST require authentication for every interface
  that lists, reads, edits, or triggers processes, or that lists or reads
  runs. The completion callback channel MUST authenticate every inbound
  request by verifying an HMAC-SHA256 signature, computed over the raw
  request body using a shared secret stored in configuration, against a
  signature header on the request; requests without a valid signature
  MUST be rejected without modifying any record.
- **FR-013**: The system MUST ship at least one canonical sample process
  ("Telegram post via BotFather") preconfigured so that the end-to-end flow
  is demonstrable on a freshly initialized workspace without manual setup.
- **FR-014**: The system MUST log every trigger, completion, validation
  rejection, and unknown-run callback as a structured event so that
  operators can audit who did what.

### Key Entities *(include if feature involves data)*

- **Process**: A named automation that can be triggered. Has a kind (a
  small enumerated label such as `telegram_post`), a structured
  configuration document, an activation flag, an optional schedule
  expressed as a single 5-field cron expression (absence means
  manual-only), and a workflow-specific webhook reference (a path or URL
  on the external automation engine that, when called, starts that
  workflow).
- **ProcessRun**: A single execution attempt of a Process. Has a status
  (`running`, `succeeded`, `failed`, `timed_out`), a creation timestamp, an
  optional completion timestamp, the configuration document used when it
  was triggered, and either a result payload or an error message once it
  completes.
- **ProcessKind**: A label that classifies what the Process does and which
  fields its configuration document must contain (initially:
  `telegram_post`).
- **Sample Process**: A Process pre-created on a fresh workspace; for v1
  this is one Telegram-post sample.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An authenticated user can go from "open the workspace" to
  "see at least one process and its latest run summary" in a single
  request, returning in under 1 second on a developer laptop with a
  warm cache.
- **SC-002**: An authenticated user can save a configuration change for a
  process and have a subsequent read return the new value within 2
  seconds end-to-end.
- **SC-003**: When a user triggers a process, the system records the new
  run in the recent-runs list within 1 second, even before the external
  engine has finished executing the work.
- **SC-004**: 100% of manual triggers either record a run or return a
  user-actionable error (deactivated, validation, network); no trigger may
  silently disappear without producing either a run or an error.
- **SC-005**: 100% of completion callbacks for known run identifiers
  result in a run state transition; 100% of callbacks for unknown
  identifiers are rejected without state changes.
- **SC-006**: The endpoint test suite covers list, retrieve, update,
  trigger, callback, and run-history paths for both authenticated and
  unauthenticated callers, and is green in continuous integration.

## Assumptions

- The external automation engine reachable for this feature is the n8n
  service deployed alongside the backend; nothing in this spec depends on
  multiple external engines simultaneously.
- The external engine can be addressed both for outbound triggers (the
  backend calls it) and for inbound completion reports (it calls the
  backend). Both directions are reachable on the deployment network.
- Authentication is provided by the workspace's existing user
  authentication (any user authenticated to the workspace may use these
  endpoints). Per-process role-based access control is out of scope for
  this iteration.
- Configuration documents are stored as structured data, not as opaque
  blobs; field-level validation per kind is in scope, using one typed
  schema per Process kind (see Clarifications session 2026-06-01).
- The default in-progress run timeout duration will be finalized during
  planning; a 15-minute default is the recommended starting point.
- A single canonical sample (Telegram post) is sufficient to prove the
  end-to-end flow at this iteration. Other process kinds will be added in
  future iterations and are out of scope here.
- Frontend integration (UI screens to consume the new interfaces) is out
  of scope for this iteration; only the backend interfaces and their
  automated tests are delivered.
- Storing secrets such as bot tokens inside configuration documents at
  rest is acceptable for this iteration; transport-level encryption (TLS)
  in the deployment is assumed.
- Run-history retention is bounded by ordinary database growth controls;
  hard retention policies are not in scope for v1.
