"""End-to-end browser tests for the starter-kit auth surface.

Covered scenarios:

* registration (including password confirmation validation),
* email verification (mandatory before sign-in),
* sign-in,
* password reset (request + confirm + sign-in with the new password).
"""

from __future__ import annotations

import logging

from .conftest import (
    RESET_LINK_RE,
    VERIFY_LINK_RE,
    MailpitInbox,
    RegisteredUser,
    extract_link,
    goto_ready,
)

logger = logging.getLogger(__name__)


def test_registration_requires_matching_password_confirmation(
    page,  # noqa: ANN001 (pytest-playwright Page)
    frontend_url: str,
    unique_email: str,
    password: str,
) -> None:
    """The register form must reject mismatched password confirmation client-side."""

    goto_ready(page, f"{frontend_url}/register")
    page.get_by_label("Work email").fill(unique_email)
    page.get_by_label("Password", exact=True).fill(password)
    page.get_by_label("Confirm password").fill(password + "-different")
    page.get_by_role("button", name="Create account").click()

    page.get_by_text("Passwords do not match").wait_for()


def test_registration_and_email_verification_full_flow(
    page,  # noqa: ANN001
    frontend_url: str,
    mailpit: MailpitInbox,
    unique_email: str,
    password: str,
) -> None:
    """Register, receive verification email in Mailpit, follow the link, verify."""

    goto_ready(page, f"{frontend_url}/register")
    page.get_by_label("Work email").fill(unique_email)
    page.get_by_label("Password", exact=True).fill(password)
    page.get_by_label("Confirm password").fill(password)
    page.get_by_role("button", name="Create account").click()
    page.get_by_text("Check your inbox").wait_for()

    message = mailpit.latest_for(unique_email, subject_contains="Confirm")
    verify_url = extract_link(VERIFY_LINK_RE, message.text)
    goto_ready(page, verify_url)
    page.get_by_text("Your email is verified").wait_for()


def test_sign_in_after_verification(
    page,  # noqa: ANN001
    frontend_url: str,
    registered_user: RegisteredUser,
) -> None:
    """A verified user can sign in and lands on the protected dashboard."""

    goto_ready(page, f"{frontend_url}/login")
    page.get_by_label("Work email").fill(registered_user.email)
    page.get_by_label("Password", exact=True).fill(registered_user.password)
    page.get_by_role("button", name="Sign in").click()

    page.wait_for_url(f"{frontend_url}/home", timeout=10_000)
    page.get_by_role("button", name="Sign out").wait_for()


def test_password_reset_flow(
    page,  # noqa: ANN001
    frontend_url: str,
    mailpit: MailpitInbox,
    registered_user: RegisteredUser,
) -> None:
    """Request a password reset, follow the email link, set + sign in with the new password."""

    new_password = registered_user.password + "-rotated!"

    goto_ready(page, f"{frontend_url}/reset-password")
    page.get_by_label("Work email").fill(registered_user.email)
    page.get_by_role("button", name="Send reset link").click()
    page.get_by_text("If an account exists").wait_for()

    message = mailpit.latest_for(registered_user.email, subject_contains="Password")
    reset_url = extract_link(RESET_LINK_RE, message.text)
    goto_ready(page, reset_url)
    page.get_by_label("New password", exact=True).fill(new_password)
    page.get_by_label("Confirm new password").fill(new_password)
    page.get_by_role("button", name="Set new password").click()
    page.get_by_text("Password updated").wait_for()

    goto_ready(page, f"{frontend_url}/login")
    page.get_by_label("Work email").fill(registered_user.email)
    page.get_by_label("Password", exact=True).fill(new_password)
    page.get_by_role("button", name="Sign in").click()
    page.wait_for_url(f"{frontend_url}/home", timeout=10_000)
