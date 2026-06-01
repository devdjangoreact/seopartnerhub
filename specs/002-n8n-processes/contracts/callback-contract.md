# n8n Callback Contract

## Purpose

n8n calls Django after a process run completes. The callback updates the matching `ProcessRun` from `running` to a terminal state.

## Endpoint

```text
POST /api/n8n/callbacks/runs/
```

This endpoint is not authenticated with a user session. It is authenticated with an HMAC signature over the raw request body.

## Request Headers

| Header | Required | Description |
| ------ | -------- | ----------- |
| `Content-Type: application/json` | yes | Body is JSON. |
| `X-Signature` | yes | Lowercase hex HMAC-SHA256 digest of the raw request body using `N8N_CALLBACK_HMAC_SECRET`. |

## Request Body

```json
{
  "runId": "15b96703-4fe9-41d0-85b7-13ed013bd8e3",
  "status": "succeeded",
  "result": {
    "telegramMessageId": "12345",
    "chatId": "-100111222333"
  }
}
```

Failure payload:

```json
{
  "runId": "15b96703-4fe9-41d0-85b7-13ed013bd8e3",
  "status": "failed",
  "error": "Telegram API rejected the message"
}
```

## Body Fields

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `runId` | UUID string | yes | Public `ProcessRun.id` created by Django and sent to n8n on trigger. |
| `status` | string enum | yes | `succeeded` or `failed`. |
| `result` | JSON object | no | Structured completion result. Optional on success; allowed on failure. |
| `error` | string | required when failed | Human-readable failure reason. |

## Signature Algorithm

```text
signature = hex(HMAC_SHA256(secret=N8N_CALLBACK_HMAC_SECRET, message=raw_request_body))
```

Django compares the received signature with `hmac.compare_digest`.

## Responses

| Status | Meaning |
| ------ | ------- |
| `200 OK` | Callback accepted and run state updated. |
| `202 Accepted` | Callback is a duplicate for an already terminal run and did not change state. |
| `400 Bad Request` | JSON body or field validation failed. |
| `401 Unauthorized` | Missing or invalid signature. |
| `404 Not Found` | `runId` does not match a known run. |
| `409 Conflict` | Callback attempts to change a terminal run to a different terminal result. |

## n8n Workflow Notes

- The Django trigger payload sent to n8n includes `runId` and `settings`.
- The n8n workflow should preserve `runId` and include it unchanged in the callback body.
- The workflow should compute the HMAC signature over the exact JSON body it sends to Django.
- The Telegram sample workflow should call Telegram's send-message operation and return the Telegram message id in `result`.
