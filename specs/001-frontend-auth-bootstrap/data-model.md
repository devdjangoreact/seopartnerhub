# Data Model: Frontend Auth Bootstrap

No new persisted domain tables are required for v1. The feature reuses Django and django-allauth
auth/account/session models.

## User Account

**Source**: Existing custom Django user model (`seopartnerhub.users.User`) and allauth email address
records.

**Fields used by this feature**:

- `id`: stable internal identifier.
- `email`: unique login identifier, normalized by allauth/account configuration.
- `display`: frontend-facing display value returned by allauth session responses.
- `has_usable_password`: used by the session response to understand password-backed accounts.
- `email_verified`: derived from allauth email address state.
- `created_at`: existing account creation timestamp where available.

**Validation rules**:

- Email is required and unique.
- Password must satisfy Django password validators.
- Registration cannot produce duplicate user accounts for the same normalized email.

**State transitions**:

```text
visitor -> registered_unverified -> email_verified -> authenticated
authenticated -> signed_out
authenticated -> password_reset_requested -> password_changed -> authenticated
```

**Future extension**:

- RBAC is out of scope for v1. User role/permission data must be addable later without replacing the
  authentication model.

## Browser Session

**Source**: Existing Django session framework.

**Fields used by this feature**:

- Session key: stored in a HttpOnly cookie.
- User id: backend-owned relationship between session and user.
- Expiry: configured by Django session settings.

**Validation rules**:

- Session cookie is HttpOnly.
- Unsafe browser requests require a valid CSRF token header.
- Session is invalid after sign-out, password change, expiry, or explicit invalidation.

**State transitions**:

```text
anonymous -> authenticated_session -> expired_session
authenticated_session -> signed_out
authenticated_session -> password_changed -> renewed_session
```

## Verification Token

**Source**: django-allauth email confirmation state.

**Fields used by this feature**:

- Key/token: opaque value from email link.
- Email address: target being verified.
- Expiry / single-use status: allauth-managed.

**Validation rules**:

- Token is single-use.
- Expired or already-used tokens render a user-friendly recovery path.

## Password Reset Token

**Source**: django-allauth password reset flow.

**Fields used by this feature**:

- Key/token: opaque value from email link.
- User account: account whose password is reset.
- Expiry / single-use status: allauth-managed.

**Validation rules**:

- Token is single-use.
- New password must satisfy Django password validators.
- A successful password reset invalidates old authentication state.

## Sign-In Lockout Record

**Source**: Cache-backed runtime record; no table in v1.

**Key**: normalized login identifier (email) plus client dimension if needed later.

**Fields**:

- `failed_attempt_count`: integer.
- `first_failed_at`: timestamp.
- `locked_until`: timestamp or absent.

**Validation rules**:

- After 5 failed sign-in attempts for the same identifier, further attempts are locked for 60 seconds.
- Threshold and duration are settings-driven.
- Successful sign-in clears the failure counter.

**State transitions**:

```text
clear -> counting_failures -> locked -> clear
```

## Frontend Auth State

**Source**: In-memory React context backed by allauth session endpoint. Not persisted outside browser
cookies.

**Fields**:

- `status`: `loading | authenticated | unauthenticated | error`.
- `user`: current allauth user payload when authenticated.
- `error`: normalized frontend auth error when present.

**Validation rules**:

- Components never read cookies directly except through the auth client for CSRF.
- Components do not call `fetch()` directly; they use the typed auth/API clients.
