# Feature Specification: Frontend Auth Bootstrap

**Feature Branch**: `001-frontend-auth-bootstrap`

**Created**: 2026-06-01

**Status**: Draft

**Input**: User description: "Start the frontend integration — run it from
Docker and wire up registration / login / identification through the
REST surface that django-allauth already exposes. Docker must run both
frontend variants; only the starter-kit talks to the Django API;
full-version is a browsable component donor."

## Clarifications

### Session 2026-06-01

- Q: Should multi-factor authentication be included in v1? → A: No, defer MFA to v2. Keep `django-allauth[mfa]` installed but disabled; ship baseline auth only.
- Q: Should role-based access control be included in v1? → A: No RBAC in v1. Every signed-in user has full access to protected frontend pages; keep the design open for future roles and permissions.
- Q: What sign-in lockout policy should v1 use? → A: After 5 failed sign-in attempts for the same identifier, lock further attempts for 60 seconds. The threshold and duration must be configurable.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visitor registers an account (Priority: P1)

A first-time visitor opens the SEOPartnerHub web app, picks "Create an
account", enters their work email and a password, and receives a
verification email. After the visitor confirms the email they land
inside the application as an authenticated user.

**Why this priority**: Without registration there are no users; this is
the entry point for every other story.

**Independent Test**: From a clean state, open the app, complete the
registration form, open the inbox in the local mail viewer, click the
verification link, and confirm the visitor is shown an authenticated
state. Delivers value as soon as one account can be created end-to-end.

**Acceptance Scenarios**:

1. **Given** the visitor is on the registration page, **When** they
   submit a valid, previously-unused email and a strong password,
   **Then** the system creates the account, sends a verification
   email, and shows a "check your inbox" message.
2. **Given** the visitor opens the verification link from the email,
   **When** the link is still valid, **Then** the email is marked
   verified and the visitor is signed in.
3. **Given** the visitor submits an email that already has an account,
   **When** they try to register, **Then** the system shows a clear,
   non-enumeration-leaking message and does not create a duplicate.

---

### User Story 2 - Registered user signs in (Priority: P1)

A user who already has an account opens the app, enters email and
password on the sign-in page, and reaches the dashboard. The session
persists across reloads and across closing/opening the browser tab.

**Why this priority**: Returning users are the dominant traffic; sign-in
is the daily entry to all internal tooling.

**Independent Test**: Pre-create a verified account. From a clean
browser, open the app, sign in, reload the page, and confirm the user
is still authenticated.

**Acceptance Scenarios**:

1. **Given** a verified account exists, **When** the user submits the
   correct email and password, **Then** the system creates a session
   and redirects to the dashboard landing page.
2. **Given** the user reloads the page after sign-in, **When** the
   page loads, **Then** the system still recognises them as
   authenticated and does not require credentials again.
3. **Given** the user submits an incorrect password, **When** they
   submit the form, **Then** the system shows a generic
   "invalid credentials" message that does not reveal whether the
   email exists.

---

### User Story 3 - Signed-in user accesses protected pages (Priority: P1)

An authenticated user can reach pages that are only meant for
authenticated users (e.g. dashboard, profile). An unauthenticated user
who tries to open these pages is redirected to sign-in and, after
signing in, returns to the page they originally requested.

**Why this priority**: The whole point of having auth is to gate the
internal tooling; without this gate the product has no security.

**Independent Test**: Visit a protected URL while signed out, confirm
the redirect to sign-in; sign in; confirm the redirect back to the
original URL.

**Acceptance Scenarios**:

1. **Given** the user is not signed in, **When** they navigate to a
   protected URL, **Then** they are redirected to the sign-in page
   and the original destination is preserved.
2. **Given** the user is signed in, **When** they navigate to the
   same URL, **Then** the page renders without further prompts.
3. **Given** the user's session has expired, **When** they perform an
   action that requires authentication, **Then** the system signs
   them out gracefully and asks them to sign in again.

---

### User Story 4 - User resets a forgotten password (Priority: P2)

A user who cannot remember their password requests a reset, receives an
email with a secure link, opens it, sets a new password, and is signed
in.

**Why this priority**: Reduces support load and is a baseline
expectation for any auth product.

**Independent Test**: Trigger password reset for an existing account,
open the email in the local mail viewer, follow the link, set a new
password, and sign in with it.

**Acceptance Scenarios**:

1. **Given** the user enters an email on the "forgot password" form,
   **When** they submit, **Then** the system always shows the same
   confirmation message (so that account existence is not leaked)
   and, if the account exists, sends a reset email.
2. **Given** the user opens a valid reset link, **When** they submit a
   new password, **Then** the password is changed and they are
   signed in.
3. **Given** the user opens an expired or already-used reset link,
   **When** the page loads, **Then** the system explains the link is
   no longer valid and offers to request a new one.

---

### User Story 5 - User signs out (Priority: P2)

A signed-in user opens a menu, picks "Sign out", and is returned to the
sign-in page; their session no longer grants access to protected pages.

**Why this priority**: Required for shared workstations and security
hygiene; trivial to ship once sign-in is working.

**Independent Test**: Sign in, click sign-out, try to open a protected
page, confirm redirect to sign-in.

**Acceptance Scenarios**:

1. **Given** the user is signed in, **When** they pick sign-out,
   **Then** the session is destroyed and they are redirected to the
   sign-in page.
2. **Given** the user is signed out, **When** they hit the browser
   back button to a protected page, **Then** they are redirected to
   sign-in.

---

### User Story 6 - Engineer browses the component showcase (Priority: P3)

An engineer working on the product opens a separate URL and browses the
full-version component showcase to copy components into the active
product UI. The showcase does not need any account and does not call
the backend.

**Why this priority**: Internal productivity for the dev team — useful
but not customer-facing.

**Independent Test**: Start the local environment, open the showcase
URL in a browser, navigate through pages, and confirm none of them
require sign-in or make backend calls.

**Acceptance Scenarios**:

1. **Given** the local environment is running, **When** the engineer
   opens the showcase URL, **Then** the showcase renders and is fully
   navigable without sign-in.
2. **Given** the engineer is viewing the showcase, **When** they open
   the browser network panel, **Then** no requests are made to the
   product API or to the authentication surface.

---

### Edge Cases

- A user submits the registration form twice in quick succession (e.g.
  double-clicks). The system must not create two accounts and must not
  send two verification emails.
- A user clicks a verification or password-reset link more than once.
  The first use succeeds; later uses show a clear "already used /
  expired" message.
- A user tries to sign in before confirming their email. The system
  must communicate clearly that the email needs to be verified and
  must offer to resend the verification email.
- The user's session expires while they have an unsaved form open.
  The system must not silently discard their input; it should sign
  them out, ask them to sign in, and ideally return them to the form
  state.
- The frontend cannot reach the backend (backend is down or restarting).
  The user sees a clear "service unavailable, please try again" message
  rather than a blank screen or a raw error.
- The user enters an email in the wrong shape (`alice@`, no @,
  trailing spaces). Validation runs on both ends and shows the same
  message.
- A bot or attacker tries to brute-force sign-in. The system must rate
  limit and must not reveal whether a given email is registered.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow a visitor to register a new account
  using an email address and a password.
- **FR-002**: System MUST send a verification email to the address used
  during registration before treating the account as fully active.
- **FR-003**: System MUST allow a registered user to sign in using
  their email and password and MUST create a persistent session on
  success.
- **FR-004**: System MUST allow a signed-in user to sign out, ending
  the session immediately.
- **FR-005**: System MUST allow a user to request a password reset by
  email and MUST allow them to set a new password using a secure,
  expiring link.
- **FR-006**: System MUST keep the user signed in across page reloads
  and browser tab restarts within a configured session lifetime.
- **FR-007**: System MUST restrict access to product pages to
  authenticated users and MUST preserve and restore the originally
  requested URL after sign-in. For v1, all authenticated users have
  the same full access to protected frontend pages.
- **FR-008**: System MUST surface the current user's identity (at
  minimum: display name or email) in the product UI when signed in.
- **FR-009**: System MUST validate user input on the form, on the
  client, and on the server, and MUST present user-friendly,
  consistent error messages.
- **FR-010**: System MUST NOT leak whether a given email is registered
  in any error message, response status, or response time on the
  sign-in, registration, or password-reset flows.
- **FR-011**: System MUST rate-limit sign-in and password-reset
  requests to mitigate brute-force and enumeration attempts. After 5
  failed sign-in attempts for the same identifier, further attempts
  MUST be locked for 60 seconds. The threshold and duration MUST be
  configurable.
- **FR-012**: System MUST run the product UI and the component
  showcase as two independently browsable web applications, both
  available locally as part of the standard one-command project
  startup.
- **FR-013**: The component showcase MUST be browsable without any
  account and MUST NOT make calls to the product API or to the
  authentication surface.
- **FR-014**: System MUST keep all v1 auth flows (registration,
  sign-in, email verification, password reset) implemented entirely
  through the existing server auth product (`django-allauth`) — no
  parallel auth surface is allowed. Multi-factor authentication is
  deferred to v2; `django-allauth[mfa]` remains installed but disabled
  for this feature.
- **FR-015**: System MUST log every authentication-relevant event
  (registration, sign-in success, sign-in failure, sign-out, password
  reset request, password reset success) with enough context to
  investigate incidents, without recording passwords or reset tokens.

### Key Entities *(include if feature involves data)*

- **User Account**: represents one person who can sign in. Holds an
  email (unique), a credential (stored only as a one-way hash), an
  email-verified flag, the account creation timestamp, and a display
  name. Role / permission data is out of scope for v1 but must remain
  possible to add later without replacing the authentication model.
- **Session**: represents an authenticated browser; tied to a single
  User Account, has a creation timestamp and an expiry, and is
  invalidated on sign-out or password change.
- **Verification Token**: short-lived, single-use token used to confirm
  an email address.
- **Password Reset Token**: short-lived, single-use token used to set a
  new password.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A first-time visitor can complete registration, email
  verification, and reach the product UI as an authenticated user in
  under 2 minutes from the moment they open the landing page.
- **SC-002**: A returning user signs in and reaches the product UI in
  under 5 seconds on a standard broadband connection.
- **SC-003**: 100 % of attempts to reach a protected page while signed
  out are redirected to sign-in; none ever render protected content.
- **SC-004**: 0 sign-in, registration, or password-reset response
  bodies reveal whether a given email is registered.
- **SC-005**: A new developer can start the project with a single
  one-line command and see the sign-in page of the product UI and the
  landing page of the showcase, in two browser tabs, within 5 minutes
  on a clean machine.
- **SC-006**: After five consecutive failed sign-in attempts for the
  same identifier, further attempts are throttled (response delayed or
  rejected) for at least one minute.
- **SC-007**: 0 password-reset or verification links can be reused
  after they have been consumed once.

## Assumptions

- The existing server-side auth product (`django-allauth`) is reused
  for the entire auth surface; no custom auth endpoints are introduced.
- The two existing frontend variants (`starter-kit` and
  `full-version`) are kept as-is on disk; this feature wires them
  into the existing container setup and connects only the
  `starter-kit` to the backend.
- All outbound email in local development goes to the local mail
  viewer that is already part of the project's container setup.
- Users access the product from modern, evergreen browsers; mobile
  layout polish is out of scope for v1 of this feature.
- The product is internal to the organisation; social-login providers
  (Google, GitHub, etc.) are out of scope for v1.
- The product UI runs at one local URL and the showcase runs at a
  separate local URL; both URLs are documented in the project quick
  start.
- Branding, copy, and visual design are kept to whatever the
  `starter-kit` ships with; design polish is a follow-up feature.
- Account self-deletion and account-administration screens (list, edit,
  disable other users) are out of scope for v1 and tracked separately.
- Role-based access control is out of scope for v1. Every signed-in
  user has full access to protected frontend pages; the design must
  leave room to add roles and permissions later.
- Sign-in lockout policy for v1 is 5 failed attempts for the same
  identifier followed by a 60-second lockout. The threshold and lockout
  duration are configurable.
