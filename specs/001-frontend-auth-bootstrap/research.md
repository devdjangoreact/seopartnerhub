# Research: Frontend Auth Bootstrap

## Decision: Use django-allauth headless browser client endpoints

**Decision**: Use `/_allauth/browser/v1/...` for registration, sign-in, sign-out, session status,
email verification, and password reset.

**Rationale**: The allauth headless browser client is designed for browser-based apps and uses
Django sessions plus CSRF protection. This matches the project requirement to use HttpOnly session
cookies and avoid bearer tokens for v1. The endpoint set is versioned under `/v1/`, and session
status is available at `GET /_allauth/browser/v1/auth/session`.

**Source**: Django Allauth documentation, "Authentication Flows" and "Headless API Endpoints":
https://pennersr-django-allauth.mintlify.app/headless/authentication and
https://pennersr-django-allauth.mintlify.app/api/headless/endpoints

**Alternatives considered**:

- DRF token auth via `/api/auth-token/`: rejected because it creates a parallel auth surface and
  stores bearer tokens client-side.
- allauth app client (`/_allauth/app/v1/...`): rejected for v1 because it is intended for token-based
  mobile/app clients, not same-origin browser sessions.

## Decision: Keep session cookies HttpOnly and expose CSRF token to the frontend

**Decision**: Use HttpOnly Django session cookies for auth state and a readable CSRF cookie for
state-changing browser requests. Frontend requests use `credentials: "include"` and send the
`X-CSRFToken` header for unsafe methods.

**Rationale**: Browser allauth endpoints rely on sessions and CSRF. The session cookie should remain
HttpOnly to reduce XSS impact. The CSRF cookie must be readable by JavaScript so the frontend can
echo it into the request header for POST/PUT/PATCH/DELETE.

**Source**: Django Allauth browser flow docs and Django CSRF docs:
https://pennersr-django-allauth.mintlify.app/headless/authentication and
https://docs.djangoproject.com/en/5.2/ref/csrf/

**Alternatives considered**:

- JWT in localStorage: rejected due to XSS exposure and because the spec forbids bearer tokens in v1.
- HttpOnly CSRF cookie: rejected because the frontend cannot read it to set `X-CSRFToken`.

## Decision: Use Next.js rewrites for local same-origin developer flow

**Decision**: `frontend/starter-kit/next.config.ts` rewrites `/_allauth/:path*` and `/api/:path*` to
the Django service during local development. The browser talks to `http://localhost:3000`, while
Next proxies to Django.

**Rationale**: Same-origin browser URLs reduce local CORS complexity while preserving the real
Django endpoints. Next.js 16 still supports `async rewrites()` in `next.config.ts`, returning either
an array or an object with `beforeFiles`, `afterFiles`, and `fallback`.

**Source**: Next.js rewrites documentation:
https://nextjs.org/docs/app/api-reference/config/next-config-js/rewrites

**Alternatives considered**:

- Direct browser calls to `http://localhost:8000`: works but requires CORS/CSRF setup and creates
  a different local flow than production same-origin deployment.
- Backend serving built frontend assets: rejected for v1 to keep frontend dev server fast and simple.

## Decision: Configure credentialed CORS/CSRF for fallback and future deployments

**Decision**: Set exact local origins for `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS`; set
`CORS_ALLOW_CREDENTIALS = True`. Do not use wildcard origins with credentialed requests.

**Rationale**: `django-cors-headers` requires explicit origins for credentialed requests, and Django
CSRF referer/origin checks are separate from CORS. Both CORS and CSRF trusted origins are required
when the frontend and backend use different origins.

**Source**: django-cors-headers README and Django CSRF documentation:
https://github.com/adamchainz/django-cors-headers/blob/main/README.rst and
https://docs.djangoproject.com/en/5.2/ref/csrf/

**Alternatives considered**:

- `CORS_ALLOW_ALL_ORIGINS = True`: rejected because it is incompatible with secure credentialed
  requests and violates security policy.
- Relying only on Next.js rewrites: rejected because direct backend calls and non-local deployments
  still need explicit settings.

## Decision: Docker runs both frontend variants from one reusable Dockerfile

**Decision**: Add a shared `compose/local/frontend/Dockerfile` and two compose services:
`frontend_starter` on port 3000 and `frontend_full` on port 3001. Each service uses a separate
node_modules volume.

**Rationale**: Both frontend variants have separate lockfiles and dependencies. Separate
node_modules volumes avoid dependency conflicts while keeping the Dockerfile shared.

**Alternatives considered**:

- One service with a runtime argument to choose variant: rejected because both variants must be
  visible in the browser at the same time.
- Copying `full-version` components directly into `starter-kit` now: rejected because this feature
  is auth/bootstrap, not component migration.

## Decision: No new backend domain tables in v1

**Decision**: Reuse Django user/session/allauth tables. Add only configuration, URL routing, and
possibly a cache-backed lockout service.

**Rationale**: v1 explicitly excludes RBAC and MFA. Existing allauth/account/session models already
cover account, email verification, sessions, and password reset. Lockout policy can be implemented
through cache keys keyed by normalized identifier.

**Alternatives considered**:

- New `LoginAttempt` table: rejected for v1 because the spec requires throttling but not historical
  reporting. It can be added later if audit/compliance reporting becomes a requirement.
