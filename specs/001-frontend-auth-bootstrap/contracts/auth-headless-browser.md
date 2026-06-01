# Contract: Browser Auth Flow

This contract describes how `frontend/starter-kit/` talks to Django auth. It is not an OpenAPI
replacement for django-allauth; it is the project-level contract the frontend must follow.

## Base URL

Local browser URL:

```text
http://localhost:3000/_allauth/browser/v1
```

Next.js rewrites this to Django:

```text
http://django:8000/_allauth/browser/v1
```

Direct backend URL for debugging:

```text
http://localhost:8000/_allauth/browser/v1
```

## Client Rules

- Every request uses `credentials: "include"`.
- Unsafe methods (`POST`, `PUT`, `PATCH`, `DELETE`) include `X-CSRFToken`.
- The auth client reads the CSRF token from the configured CSRF cookie.
- No bearer token or localStorage token is introduced.
- React components call `authClient`, never `fetch()` directly.

## Session Status

```http
GET /auth/session
```

Expected outcomes:

- `200`: authenticated session with user payload.
- `401`: not authenticated; frontend sets `status = "unauthenticated"`.
- `410`: stale/invalid session; frontend clears local auth state and asks user to sign in again.

## Sign In

```http
POST /auth/login
Content-Type: application/json
X-CSRFToken: <token>
```

Request body:

```json
{
  "email": "user@example.com",
  "password": "password"
}
```

Frontend behavior:

- On success: refresh session state and redirect to the preserved destination or dashboard.
- On invalid credentials: show a generic error that does not reveal whether the email exists.
- On lockout: show a user-friendly wait/retry message.

## Sign Out

```http
DELETE /auth/session
X-CSRFToken: <token>
```

Frontend behavior:

- Clear auth context.
- Redirect to `/login`.
- A browser back navigation to a protected page must redirect to `/login`.

## Registration

```http
POST /auth/signup
Content-Type: application/json
X-CSRFToken: <token>
```

Request body:

```json
{
  "email": "user@example.com",
  "password": "password"
}
```

Frontend behavior:

- Show "check your inbox" after submission.
- Do not leak whether the email was already registered.

## Email Verification

```http
POST /auth/email/verify
Content-Type: application/json
X-CSRFToken: <token>
```

Request body:

```json
{
  "key": "<email-confirmation-key>"
}
```

Frontend behavior:

- Valid key: mark email verified and refresh auth state.
- Expired/used key: show recovery path to request a new verification email.

## Password Reset

Request reset:

```http
POST /auth/password/request
Content-Type: application/json
X-CSRFToken: <token>
```

Confirm reset:

```http
POST /auth/password/reset
Content-Type: application/json
X-CSRFToken: <token>
```

Frontend behavior:

- Request always shows the same confirmation message regardless of whether the account exists.
- Confirm success signs the user in or redirects to sign-in depending on allauth response state.

## Errors

The auth client normalizes server errors to:

```ts
interface AuthError {
  code: string
  message: string
  fieldErrors: Record<string, string[]>
  status: number
}
```

No component consumes raw allauth responses directly.
