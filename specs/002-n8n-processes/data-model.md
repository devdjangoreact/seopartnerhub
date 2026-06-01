# Data Model: n8n Processes Management

## Process

Represents one automation process exposed to authenticated users.

### Fields

| Field | Type | Required | Notes |
| ----- | ---- | -------- | ----- |
| `id` | integer | yes | Primary key. |
| `name` | string | yes | Human-readable display name. |
| `kind` | enum | yes | Initial value set: `telegram_post`. |
| `is_active` | boolean | yes | Inactive processes cannot be triggered or scheduled. |
| `settings_json` | JSON object | yes | Validated against the typed schema registered for `kind`. |
| `webhook_path` | string | yes | n8n workflow-specific webhook path. Joined with `N8N_BASE_URL` at trigger time. |
| `schedule_cron` | string or null | no | 5-field cron expression. Null/blank means manual-only. |
| `created_at` | datetime | yes | Set on creation. |
| `updated_at` | datetime | yes | Changes when editable process fields change. |

### Relationships

- One `Process` has many `ProcessRun` records.
- `ProcessRun.process` is protected from deletion for v1; deleting a process with history is out of scope.

### Validation rules

- `name` cannot be blank.
- `kind` must match a registered `ProcessKind`.
- `settings_json` must be a JSON object and must validate against the registered typed schema for `kind`.
- `webhook_path` cannot be blank and must be a relative path or an absolute URL accepted by the n8n webhook client.
- `schedule_cron`, when provided, must contain exactly five cron fields.
- A `Process` can be triggered only when `is_active` is true.

### Indexes / uniqueness

- Index `kind`.
- Index `is_active`.
- Index `schedule_cron` for scheduled-process selection.
- `name` is not globally unique in v1; API clients should use `id`.

## ProcessRun

Represents one execution attempt for a process.

### Fields

| Field | Type | Required | Notes |
| ----- | ---- | -------- | ----- |
| `id` | UUID | yes | Public run identifier passed to n8n and callback payloads. |
| `process` | foreign key | yes | Parent `Process`. |
| `status` | enum | yes | `running`, `succeeded`, `failed`, `timed_out`. |
| `trigger_source` | enum | yes | `manual`, `scheduled`. |
| `settings_snapshot_json` | JSON object | yes | Exact settings used for this run. |
| `request_payload_json` | JSON object | yes | Payload sent to n8n. |
| `result_json` | JSON object or null | no | Completion payload on success/failure. |
| `error_message` | string or null | no | Human-readable failure or timeout detail. |
| `started_by` | foreign key to user or null | no | User for manual triggers; null for scheduled runs. |
| `started_at` | datetime | yes | Set when run is created. |
| `finished_at` | datetime or null | no | Set for terminal states. |
| `created_at` | datetime | yes | Set on creation. |
| `updated_at` | datetime | yes | Changes when status/result changes. |

### Relationships

- Each `ProcessRun` belongs to exactly one `Process`.
- `started_by` references the Django user model and is nullable for scheduled execution.

### Status transitions

```text
running -> succeeded
running -> failed
running -> timed_out
```

Terminal states (`succeeded`, `failed`, `timed_out`) must not transition again. A duplicate callback for a terminal run is accepted as a no-op only if it does not change persisted data; otherwise it is rejected.

### Validation rules

- `settings_snapshot_json` must be a JSON object.
- `request_payload_json` must include the run identifier and settings snapshot sent to n8n.
- `finished_at` is required when status is terminal and must be null while status is `running`.
- `error_message` is required for `failed` and `timed_out`.

### Indexes

- Composite index `(process, -started_at)` for recent run history.
- Index `status` for timeout sweeps.
- Index `started_at` for timeout sweeps.

## ProcessKind

Small enum describing the process behavior and settings schema.

### Values

| Value | Description |
| ----- | ----------- |
| `telegram_post` | Send a Telegram group/channel post through a BotFather-created bot. |

## TelegramPostSettings

Typed schema for `Process.kind == "telegram_post"`.

### Fields

| Field | Type | Required | Notes |
| ----- | ---- | -------- | ----- |
| `chat_id` | string | yes | Telegram chat/channel identifier. |
| `message` | string | yes | Message body to send. |
| `parse_mode` | enum or null | no | Allowed values: `MarkdownV2`, `HTML`, or null/no formatting. |
| `disable_web_page_preview` | boolean | no | Defaults to false. |

### Validation rules

- `chat_id` cannot be blank.
- `message` cannot be blank.
- `parse_mode`, when present, must be one of the allowed values.

## CallbackPayload

Payload sent by n8n to Django when a run completes.

### Fields

| Field | Type | Required | Notes |
| ----- | ---- | -------- | ----- |
| `runId` | UUID string | yes | Matches `ProcessRun.id`. |
| `status` | enum | yes | `succeeded` or `failed`. |
| `result` | JSON object | no | Result details from n8n. |
| `error` | string | no | Required when status is `failed`. |

### Validation rules

- Raw request body must verify against `X-Signature` HMAC before JSON parsing result is trusted.
- Unknown `runId` is rejected without state changes.
- `failed` payloads must include `error`.
