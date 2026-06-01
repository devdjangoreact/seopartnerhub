"""Cache-backed sign-in lockout service.

Implements FR-011 of spec `001-frontend-auth-bootstrap`: after
`SIGN_IN_LOCKOUT_THRESHOLD` failed sign-in attempts for the same identifier,
further attempts are locked for `SIGN_IN_LOCKOUT_SECONDS`. Both settings are
env-driven and live in `config/settings/base.py`.

Stateless from the service's perspective; all state lives in Django's cache so
no migration is needed. Keyed by a normalized identifier (lowercased email by
default).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from django.conf import settings
from django.core.cache import BaseCache
from django.core.cache import cache as default_cache

logger = logging.getLogger(__name__)
auth_logger = logging.getLogger("seopartnerhub.auth")


@dataclass(frozen=True)
class LockoutStatus:
    """Snapshot of lockout state for one identifier."""

    is_locked: bool
    failed_attempts: int
    retry_after_seconds: int


class SignInLockoutService:
    """Throttle repeated failed sign-in attempts per identifier."""

    def __init__(
        self,
        cache: BaseCache | None = None,
        threshold: int | None = None,
        lockout_seconds: int | None = None,
        cache_prefix: str | None = None,
    ) -> None:
        self._cache = cache if cache is not None else default_cache
        self._threshold = (
            threshold
            if threshold is not None
            else int(getattr(settings, "SIGN_IN_LOCKOUT_THRESHOLD", 5))
        )
        self._lockout_seconds = (
            lockout_seconds
            if lockout_seconds is not None
            else int(getattr(settings, "SIGN_IN_LOCKOUT_SECONDS", 60))
        )
        self._cache_prefix = (
            cache_prefix
            if cache_prefix is not None
            else str(getattr(settings, "SIGN_IN_LOCKOUT_CACHE_PREFIX", "auth:lockout:"))
        )

    @staticmethod
    def normalize(identifier: str) -> str:
        return identifier.strip().lower()

    def _attempts_key(self, identifier: str) -> str:
        return f"{self._cache_prefix}attempts:{self.normalize(identifier)}"

    def _locked_key(self, identifier: str) -> str:
        return f"{self._cache_prefix}locked_until:{self.normalize(identifier)}"

    def status(self, identifier: str) -> LockoutStatus:
        locked_until = self._cache.get(self._locked_key(identifier))
        attempts = int(self._cache.get(self._attempts_key(identifier), 0))

        if isinstance(locked_until, (int, float)):
            now = time.time()
            remaining = int(max(0, locked_until - now))

            if remaining > 0:
                return LockoutStatus(
                    is_locked=True,
                    failed_attempts=attempts,
                    retry_after_seconds=remaining,
                )

        return LockoutStatus(
            is_locked=False,
            failed_attempts=attempts,
            retry_after_seconds=0,
        )

    def register_failure(self, identifier: str) -> LockoutStatus:
        attempts_key = self._attempts_key(identifier)

        try:
            new_attempts = int(self._cache.incr(attempts_key))
        except ValueError:
            self._cache.set(attempts_key, 1, timeout=self._lockout_seconds * 10)
            new_attempts = 1

        if new_attempts >= self._threshold:
            locked_until = time.time() + self._lockout_seconds

            self._cache.set(
                self._locked_key(identifier),
                locked_until,
                timeout=self._lockout_seconds,
            )
            auth_logger.warning(
                "sign_in.lockout.triggered",
                extra={
                    "identifier": self.normalize(identifier),
                    "failed_attempts": new_attempts,
                    "locked_for_seconds": self._lockout_seconds,
                },
            )

            return LockoutStatus(
                is_locked=True,
                failed_attempts=new_attempts,
                retry_after_seconds=self._lockout_seconds,
            )

        auth_logger.info(
            "sign_in.failure",
            extra={
                "identifier": self.normalize(identifier),
                "failed_attempts": new_attempts,
            },
        )

        return LockoutStatus(
            is_locked=False,
            failed_attempts=new_attempts,
            retry_after_seconds=0,
        )

    def clear(self, identifier: str) -> None:
        self._cache.delete_many(
            [self._attempts_key(identifier), self._locked_key(identifier)],
        )
        auth_logger.info(
            "sign_in.lockout.cleared",
            extra={"identifier": self.normalize(identifier)},
        )
