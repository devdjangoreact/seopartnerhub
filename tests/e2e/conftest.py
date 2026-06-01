"""Shared fixtures and helpers for browser-based auth E2E tests.

These tests run against the locally running stack and do NOT touch the
Django ORM directly: registration goes through the real allauth headless
browser API via Next.js rewrites, email links are read from Mailpit, and
sign-in is verified through the dashboard UI.

The pytest-django plugin is disabled in `pytest.ini` so this folder can
be executed standalone with `uvx` in an isolated environment.
"""

from __future__ import annotations

import logging
import os
import re
import time
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING
from urllib.parse import unquote
from urllib.request import Request, urlopen
import json

import pytest

if TYPE_CHECKING:
    from collections.abc import Iterator

logger = logging.getLogger(__name__)

DEFAULT_FRONTEND_URL = "http://localhost:3000"
DEFAULT_MAILPIT_URL = "http://localhost:8025"
DEFAULT_PASSWORD = "Sup3rSecret-Pass!"  # noqa: S105 (test fixture password)
MAILPIT_POLL_TIMEOUT_SECONDS = 30
MAILPIT_POLL_INTERVAL_SECONDS = 1.0

VERIFY_LINK_RE = re.compile(r"http://[^\s]+/verify-email/[^\s)]+")
RESET_LINK_RE = re.compile(r"http://[^\s]+/reset-password/[^\s)]+")


@pytest.fixture(scope="session")
def frontend_url() -> str:
    return os.environ.get("E2E_FRONTEND_URL", DEFAULT_FRONTEND_URL).rstrip("/")


@pytest.fixture(scope="session")
def mailpit_url() -> str:
    return os.environ.get("E2E_MAILPIT_URL", DEFAULT_MAILPIT_URL).rstrip("/")


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict[str, object]) -> dict[str, object]:
    """Use the system Chrome so no Chromium download is required on Windows."""

    return {**browser_type_launch_args, "channel": "chrome"}


@pytest.fixture
def unique_email() -> str:
    return f"e2e-{uuid.uuid4().hex[:12]}@example.test"


@dataclass(frozen=True)
class MailpitMessage:
    message_id: str
    subject: str
    text: str


@dataclass(frozen=True)
class MailpitInbox:
    base_url: str

    def latest_for(self, recipient: str, *, subject_contains: str | None = None) -> MailpitMessage:
        deadline = time.monotonic() + MAILPIT_POLL_TIMEOUT_SECONDS

        while True:
            messages = self._search(f"to:{recipient}")
            if subject_contains is not None:
                messages = [m for m in messages if subject_contains.lower() in m["Subject"].lower()]

            if messages:
                head = messages[0]
                message_id: str = head["ID"]
                body = self._get_json(f"/api/v1/message/{message_id}")
                return MailpitMessage(
                    message_id=message_id,
                    subject=body.get("Subject", ""),
                    text=body.get("Text", ""),
                )

            if time.monotonic() >= deadline:
                logger.warning("mailpit_timeout", extra={"to": recipient})
                msg = f"No Mailpit message for {recipient} within {MAILPIT_POLL_TIMEOUT_SECONDS}s"
                raise TimeoutError(msg)

            time.sleep(MAILPIT_POLL_INTERVAL_SECONDS)

    def _search(self, query: str) -> list[dict[str, object]]:
        payload = self._get_json(f"/api/v1/search?query={query}")
        messages: list[dict[str, object]] = payload.get("messages") or []
        return messages

    def _get_json(self, path: str) -> dict[str, object]:
        url = f"{self.base_url}{path}"
        request = Request(url, headers={"Accept": "application/json"})  # noqa: S310 (localhost)
        with urlopen(request, timeout=10) as response:  # noqa: S310 (localhost)
            return json.loads(response.read().decode("utf-8"))


@pytest.fixture
def mailpit(mailpit_url: str) -> MailpitInbox:
    return MailpitInbox(base_url=mailpit_url)


def extract_link(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    if match is None:
        msg = "Expected link not found in email body"
        raise AssertionError(msg)
    return unquote(match.group(0))


@pytest.fixture
def password() -> str:
    return DEFAULT_PASSWORD


@dataclass(frozen=True)
class RegisteredUser:
    email: str
    password: str


def goto_ready(page, url: str) -> None:  # noqa: ANN001 (pytest-playwright Page)
    """Navigate and wait until initial network is idle.

    The starter-kit's `AuthProvider` issues a `GET /_allauth/browser/v1/auth/session`
    on mount, and that response is the one that seeds the `csrftoken` cookie.
    Submitting a form before this completes results in a 403 from Django
    because the request goes out without `X-CSRFToken`.
    """

    page.goto(url, wait_until="networkidle")


@pytest.fixture
def registered_user(
    page,  # noqa: ANN001 (pytest-playwright provides Page)
    frontend_url: str,
    mailpit: MailpitInbox,
    unique_email: str,
    password: str,
) -> Iterator[RegisteredUser]:
    """Register + verify a fresh user. Yields the credentials."""

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

    yield RegisteredUser(email=unique_email, password=password)
