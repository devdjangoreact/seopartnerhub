# Tasks: Frontend Auth Bootstrap

**Input**: Design documents from `specs/001-frontend-auth-bootstrap/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: No automated test-code tasks are generated because tests were not explicitly requested.
Each user story includes an independent manual validation criterion. Add automated tests later if
the user explicitly asks for them.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, ...)
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add frontend Docker services and package manager entry points shared by all stories.

- [ ] T001 Create shared frontend Dockerfile in `compose/local/frontend/Dockerfile`
- [ ] T002 Create frontend container start script in `compose/local/frontend/start`
- [ ] T003 Add `seopartnerhub_frontend_starter_node_modules` and `seopartnerhub_frontend_full_node_modules` volumes in `docker-compose.local.yml`
- [ ] T004 Add `frontend_starter` service with `frontend/starter-kit/`, port `3000:3000`, and Django backend environment in `docker-compose.local.yml`
- [ ] T005 Add `frontend_full` service with `frontend/full-version/`, port `3001:3000`, and no backend environment in `docker-compose.local.yml`
- [ ] T006 Update `frontend/starter-kit/package.json` scripts with `typecheck` and `generate:api`
- [ ] T007 Update `frontend/full-version/package.json` scripts with `typecheck`
- [ ] T008 Add frontend dependencies for forms and API generation in `frontend/starter-kit/package.json`
- [ ] T009 Update startup URLs and Docker commands in `readme_start.md`
- [ ] T010 Update user-facing frontend startup instructions in `README.md`

**Checkpoint**: `docker compose -f docker-compose.local.yml up --build` starts Django plus two
frontend containers, with starter on port 3000 and showcase on port 3001.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core auth, API, configuration, and typed frontend foundations required by all user
stories.

**CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T011 Enable `allauth.headless` in `THIRD_PARTY_APPS` in `config/settings/base.py`
- [ ] T012 Configure allauth headless browser settings and frontend URLs in `config/settings/base.py`
- [ ] T013 Configure local CORS and CSRF trusted origins for `http://localhost:3000` in `config/settings/local.py`
- [ ] T014 Make the CSRF cookie readable in local development by setting `CSRF_COOKIE_HTTPONLY = False` in `config/settings/local.py`
- [ ] T015 Expand `CORS_URLS_REGEX` to include both `/api/` and `/_allauth/` in `config/settings/base.py`
- [ ] T016 Register allauth headless URLs at `/_allauth/` in `config/urls.py`
- [ ] T017 Remove or isolate DRF token auth from frontend-facing documentation in `README.md`
- [ ] T018 Add Next.js rewrites for `/_allauth/:path*` and `/api/:path*` in `frontend/starter-kit/next.config.ts`
- [ ] T019 Confirm `frontend/full-version/next.config.ts` has no Django API or allauth rewrites
- [ ] T020 Create typed API error model in `frontend/starter-kit/src/lib/api/apiError.ts`
- [ ] T021 Create typed API client wrapper with `credentials: "include"` in `frontend/starter-kit/src/lib/api/apiClient.ts`
- [ ] T022 Create CSRF cookie helper for unsafe requests in `frontend/starter-kit/src/lib/auth/csrfToken.ts`
- [ ] T023 Create allauth response and user interfaces in `frontend/starter-kit/src/lib/auth/authTypes.ts`
- [ ] T024 Create auth client mapped to allauth browser endpoints in `frontend/starter-kit/src/lib/auth/authClient.ts`
- [ ] T025 Create AuthProvider with session bootstrap in `frontend/starter-kit/src/lib/auth/AuthProvider.tsx`
- [ ] T026 Create `useAuth` hook in `frontend/starter-kit/src/lib/auth/useAuth.ts`
- [ ] T027 Wrap the starter app layout with AuthProvider in `frontend/starter-kit/src/app/layout.tsx`
- [ ] T028 Add generated OpenAPI schema output placeholder in `frontend/starter-kit/src/lib/api/schema.ts`
- [ ] T029 Create sign-in lockout service skeleton in `seopartnerhub/users/services/sign_in_lockout_service.py`
- [ ] T030 Add configurable lockout settings in `config/settings/base.py`
- [ ] T031 Add authentication event logging configuration notes in `config/settings/base.py`

**Checkpoint**: Starter frontend can call the session endpoint through Next rewrites and receive a
typed unauthenticated state without raw fetch calls in components.

---

## Phase 3: User Story 1 - Visitor Registers an Account (Priority: P1) MVP

**Goal**: A visitor can create an account, receive a verification email, verify it, and land in an
authenticated frontend state.

**Independent Test**: Open `http://localhost:3000/register`, register with a new email, open
Mailpit at `http://localhost:8025`, follow the verification link, and confirm the frontend shows an
authenticated state.

### Implementation for User Story 1

- [ ] T032 [P] [US1] Create registration page shell in `frontend/starter-kit/src/app/(auth)/register/page.tsx`
- [ ] T033 [P] [US1] Create register form schema in `frontend/starter-kit/src/lib/auth/registerSchema.ts`
- [ ] T034 [US1] Implement register form with typed validation in `frontend/starter-kit/src/app/(auth)/register/page.tsx`
- [ ] T035 [US1] Wire register form submission to `authClient.signup` in `frontend/starter-kit/src/app/(auth)/register/page.tsx`
- [ ] T036 [US1] Add duplicate-submit protection and loading state in `frontend/starter-kit/src/app/(auth)/register/page.tsx`
- [ ] T037 [US1] Create email verification page in `frontend/starter-kit/src/app/(auth)/verify-email/[key]/page.tsx`
- [ ] T038 [US1] Wire email verification page to `authClient.verifyEmail` in `frontend/starter-kit/src/app/(auth)/verify-email/[key]/page.tsx`
- [ ] T039 [US1] Configure allauth email confirmation frontend URL to point to `/verify-email/{key}` in `config/settings/base.py`
- [ ] T040 [US1] Add user-friendly expired or used verification link state in `frontend/starter-kit/src/app/(auth)/verify-email/[key]/page.tsx`
- [ ] T041 [US1] Add auth event logging for signup and email verification in `seopartnerhub/users/adapters.py`

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Registered User Signs In (Priority: P1)

**Goal**: A verified user signs in, reaches the dashboard, and remains authenticated across reloads.

**Independent Test**: With a verified account, open `http://localhost:3000/login`, sign in, reload
the page, and confirm the session persists.

### Implementation for User Story 2

- [ ] T042 [P] [US2] Create login page shell in `frontend/starter-kit/src/app/(auth)/login/page.tsx`
- [ ] T043 [P] [US2] Create login form schema in `frontend/starter-kit/src/lib/auth/loginSchema.ts`
- [ ] T044 [US2] Implement login form with typed validation in `frontend/starter-kit/src/app/(auth)/login/page.tsx`
- [ ] T045 [US2] Wire login form submission to `authClient.login` in `frontend/starter-kit/src/app/(auth)/login/page.tsx`
- [ ] T046 [US2] Implement generic invalid-credentials and unverified-email error handling in `frontend/starter-kit/src/app/(auth)/login/page.tsx`
- [ ] T047 [US2] Integrate sign-in lockout checks into allauth login flow in `seopartnerhub/users/adapters.py`
- [ ] T048 [US2] Persist failed sign-in counters through `SignInLockoutService` in `seopartnerhub/users/services/sign_in_lockout_service.py`
- [ ] T049 [US2] Clear sign-in lockout counter after successful login in `seopartnerhub/users/services/sign_in_lockout_service.py`
- [ ] T050 [US2] Add login success and failure event logging in `seopartnerhub/users/adapters.py`
- [ ] T051 [US2] Redirect authenticated users to dashboard after login in `frontend/starter-kit/src/app/(auth)/login/page.tsx`

**Checkpoint**: User Story 2 works independently with a pre-existing verified account.

---

## Phase 5: User Story 3 - Signed-In User Accesses Protected Pages (Priority: P1)

**Goal**: Protected frontend pages are visible only to signed-in users; signed-out users redirect to
login and return after authentication.

**Independent Test**: Visit a protected URL while signed out, confirm redirect to login, sign in,
and confirm redirect back to the original URL.

### Implementation for User Story 3

- [ ] T052 [P] [US3] Create protected dashboard layout guard in `frontend/starter-kit/src/app/(dashboard)/layout.tsx`
- [ ] T053 [P] [US3] Create auth route helper in `frontend/starter-kit/src/lib/auth/requireAuth.ts`
- [ ] T054 [US3] Preserve requested destination in login redirect query in `frontend/starter-kit/src/lib/auth/requireAuth.ts`
- [ ] T055 [US3] Consume preserved destination after successful login in `frontend/starter-kit/src/app/(auth)/login/page.tsx`
- [ ] T056 [US3] Display current user identity in dashboard shell in `frontend/starter-kit/src/app/(dashboard)/layout.tsx`
- [ ] T057 [US3] Handle expired session state in AuthProvider in `frontend/starter-kit/src/lib/auth/AuthProvider.tsx`
- [ ] T058 [US3] Add service-unavailable auth state handling in `frontend/starter-kit/src/lib/auth/AuthProvider.tsx`

**Checkpoint**: Protected pages never render protected content to anonymous users.

---

## Phase 6: User Story 4 - User Resets a Forgotten Password (Priority: P2)

**Goal**: A user requests a password reset, receives an email, sets a new password, and can sign in.

**Independent Test**: Request reset for an existing account, open Mailpit, follow the reset link,
set a new password, and sign in with it.

### Implementation for User Story 4

- [ ] T059 [P] [US4] Create password reset request page in `frontend/starter-kit/src/app/(auth)/reset-password/page.tsx`
- [ ] T060 [P] [US4] Create password reset request schema in `frontend/starter-kit/src/lib/auth/passwordResetRequestSchema.ts`
- [ ] T061 [US4] Wire reset request form to `authClient.requestPasswordReset` in `frontend/starter-kit/src/app/(auth)/reset-password/page.tsx`
- [ ] T062 [US4] Always show non-enumerating reset request confirmation in `frontend/starter-kit/src/app/(auth)/reset-password/page.tsx`
- [ ] T063 [P] [US4] Create password reset confirm page in `frontend/starter-kit/src/app/(auth)/reset-password/[key]/page.tsx`
- [ ] T064 [P] [US4] Create password reset confirm schema in `frontend/starter-kit/src/lib/auth/passwordResetConfirmSchema.ts`
- [ ] T065 [US4] Wire reset confirm form to `authClient.confirmPasswordReset` in `frontend/starter-kit/src/app/(auth)/reset-password/[key]/page.tsx`
- [ ] T066 [US4] Configure allauth password reset frontend URL to point to `/reset-password/{key}` in `config/settings/base.py`
- [ ] T067 [US4] Add expired or used reset link recovery state in `frontend/starter-kit/src/app/(auth)/reset-password/[key]/page.tsx`
- [ ] T068 [US4] Add password reset request and success event logging in `seopartnerhub/users/adapters.py`

**Checkpoint**: Password reset flow works independently of registration when an account already
exists.

---

## Phase 7: User Story 5 - User Signs Out (Priority: P2)

**Goal**: A signed-in user signs out and can no longer access protected pages.

**Independent Test**: Sign in, click sign out, then open a protected page and confirm redirect to
login.

### Implementation for User Story 5

- [ ] T069 [P] [US5] Add `authClient.logout` method in `frontend/starter-kit/src/lib/auth/authClient.ts`
- [ ] T070 [US5] Expose logout action from AuthProvider in `frontend/starter-kit/src/lib/auth/AuthProvider.tsx`
- [ ] T071 [US5] Add sign-out UI action in dashboard layout in `frontend/starter-kit/src/app/(dashboard)/layout.tsx`
- [ ] T072 [US5] Redirect to login after logout in `frontend/starter-kit/src/app/(dashboard)/layout.tsx`
- [ ] T073 [US5] Add logout event logging in `seopartnerhub/users/adapters.py`

**Checkpoint**: Browser back navigation after sign-out does not expose protected content.

---

## Phase 8: User Story 6 - Engineer Browses Component Showcase (Priority: P3)

**Goal**: The full-version frontend remains browsable as a backend-free component showcase.

**Independent Test**: Open `http://localhost:3001`, navigate through the showcase, and confirm no
requests hit `/api/` or `/_allauth/`.

### Implementation for User Story 6

- [ ] T074 [US6] Ensure `frontend_full` service starts full-version on container port 3000 and host port 3001 in `docker-compose.local.yml`
- [ ] T075 [US6] Verify `frontend/full-version/next.config.ts` does not add backend rewrites or auth redirects
- [ ] T076 [US6] Document full-version as component donor in `README.md`
- [ ] T077 [US6] Document full-version as component donor in `readme_start.md`
- [ ] T078 [US6] Add manual browser verification notes for full-version in `specs/001-frontend-auth-bootstrap/quickstart.md`

**Checkpoint**: Showcase remains accessible even if Django is unavailable.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Final consistency, docs, quality, and Spec Kit alignment.

- [ ] T079 [P] Update frontend requirements in `readme_spec.md` if implementation choices changed
- [ ] T080 [P] Update active plan notes in `specs/001-frontend-auth-bootstrap/plan.md` if implementation paths changed
- [ ] T081 Update `specs/001-frontend-auth-bootstrap/contracts/auth-headless-browser.md` with final allauth endpoint names if implementation discovers differences
- [ ] T082 Update `specs/001-frontend-auth-bootstrap/contracts/frontend-docker.md` with final Docker service names and ports
- [ ] T083 Run backend formatting and lint commands from `.cursor/commands/ship.md`
- [ ] T084 Run frontend lint, typecheck, and build for `frontend/starter-kit`
- [ ] T085 Run frontend lint, typecheck, and build for `frontend/full-version`
- [ ] T086 Manually validate quickstart flow in `specs/001-frontend-auth-bootstrap/quickstart.md`
- [ ] T087 Confirm no TypeScript `any` remains in `frontend/starter-kit/src`
- [ ] T088 Confirm `frontend/full-version` has no `/api/` or `/_allauth/` backend calls
- [ ] T089 Review docs for stale ports, URLs, and command names in `README.md`, `readme_start.md`, and `readme_spec.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks every user story.
- **User Stories (Phases 3-8)**: Depend on Foundational completion.
- **Polish**: Depends on desired user stories being complete.

### User Story Dependencies

- **US1 Registration (P1)**: Can start after Foundational.
- **US2 Sign-in (P1)**: Can start after Foundational; needs lockout foundation.
- **US3 Protected pages (P1)**: Depends on the auth provider from Foundational and works best after US2 login.
- **US4 Password reset (P2)**: Can start after Foundational; independent of US1 if a verified account exists.
- **US5 Sign-out (P2)**: Depends on AuthProvider and sign-in flow.
- **US6 Component showcase (P3)**: Can start after Docker setup and does not depend on auth stories.

### MVP Scope

MVP is Phase 1 + Phase 2 + Phase 3 (US1). For a practical login demo, include Phase 4 (US2).

---

## Parallel Opportunities

- T006 and T007 can run in parallel because they edit different package files.
- T020-T024 can run in parallel after T018 because they create separate frontend library files.
- T032 and T033 can run in parallel for US1.
- T042 and T043 can run in parallel for US2.
- T052 and T053 can run in parallel for US3.
- T059, T060, T063, and T064 can run in parallel for US4.
- T079 and T080 can run in parallel during polish.

## Parallel Example: User Story 1

```text
Task: "T032 [P] [US1] Create registration page shell in frontend/starter-kit/src/app/(auth)/register/page.tsx"
Task: "T033 [P] [US1] Create register form schema in frontend/starter-kit/src/lib/auth/registerSchema.ts"
```

## Parallel Example: User Story 4

```text
Task: "T059 [P] [US4] Create password reset request page in frontend/starter-kit/src/app/(auth)/reset-password/page.tsx"
Task: "T060 [P] [US4] Create password reset request schema in frontend/starter-kit/src/lib/auth/passwordResetRequestSchema.ts"
Task: "T063 [P] [US4] Create password reset confirm page in frontend/starter-kit/src/app/(auth)/reset-password/[key]/page.tsx"
Task: "T064 [P] [US4] Create password reset confirm schema in frontend/starter-kit/src/lib/auth/passwordResetConfirmSchema.ts"
```

---

## Implementation Strategy

### MVP First

1. Complete Setup and Foundational phases.
2. Complete US1 registration and email verification.
3. Validate US1 independently through Mailpit.
4. Add US2 sign-in for a usable daily auth loop.

### Incremental Delivery

1. Docker + auth foundation.
2. US1 registration.
3. US2 sign-in.
4. US3 protected pages.
5. US4 password reset.
6. US5 sign-out.
7. US6 showcase hardening.

### Notes

- Do not create custom auth endpoints.
- Do not introduce bearer tokens.
- Do not connect `frontend/full-version` to Django.
- Keep MFA and RBAC deferred for v2.
- Keep lockout threshold and duration configurable.
