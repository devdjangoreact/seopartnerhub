from __future__ import annotations

import logging
import typing

from allauth.account.adapter import DefaultAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.http import JsonResponse

from seopartnerhub.users.services.sign_in_lockout_service import SignInLockoutService

if typing.TYPE_CHECKING:
    from allauth.account.models import EmailAddress
    from allauth.socialaccount.models import SocialLogin
    from django.contrib.auth.models import AbstractBaseUser
    from django.http import HttpRequest

    from seopartnerhub.users.models import User


logger = logging.getLogger(__name__)
auth_logger = logging.getLogger("seopartnerhub.auth")


def _redact_identifier(value: str | None) -> str:
    if value is None or value == "":
        return ""

    return SignInLockoutService.normalize(value)


def _credentials_identifier(credentials: dict[str, typing.Any]) -> str:
    raw = (
        credentials.get("email")
        or credentials.get("login")
        or credentials.get("username")
        or ""
    )

    return _redact_identifier(str(raw))


class AccountAdapter(DefaultAccountAdapter):
    """Project account adapter.

    Adds:
    - Auth event logging through `seopartnerhub.auth` logger (no `print()`).
    - Sign-in lockout enforcement via `SignInLockoutService` (FR-011 of
      `001-frontend-auth-bootstrap`).
    """

    def is_open_for_signup(self, request: HttpRequest) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def get_lockout_service(self) -> SignInLockoutService:
        return SignInLockoutService()

    def pre_authenticate(self, request: HttpRequest, **credentials: typing.Any) -> None:
        identifier = _credentials_identifier(credentials)

        if identifier == "":
            return super().pre_authenticate(request, **credentials)

        status = self.get_lockout_service().status(identifier)

        if status.is_locked:
            auth_logger.warning(
                "sign_in.blocked.lockout",
                extra={
                    "identifier": identifier,
                    "retry_after_seconds": status.retry_after_seconds,
                },
            )
            payload = {
                "status": 429,
                "errors": [
                    {
                        "code": "rate_limited",
                        "message": (
                            "Too many failed sign-in attempts. "
                            f"Try again in {status.retry_after_seconds} seconds."
                        ),
                    },
                ],
            }

            raise ImmediateHttpResponse(JsonResponse(payload, status=429))

        return super().pre_authenticate(request, **credentials)

    def authenticate(
        self,
        request: HttpRequest,
        **credentials: typing.Any,
    ) -> AbstractBaseUser | None:
        identifier = _credentials_identifier(credentials)
        user = super().authenticate(request, **credentials)

        if user is None and identifier != "":
            self.get_lockout_service().register_failure(identifier)

        return user

    def login(self, request: HttpRequest, user: AbstractBaseUser) -> None:
        super().login(request, user)
        raw_identifier = getattr(user, "email", None) or getattr(user, "username", None)
        identifier = _redact_identifier(raw_identifier)

        if identifier != "":
            self.get_lockout_service().clear(identifier)

        auth_logger.info(
            "sign_in.success",
            extra={
                "identifier": identifier,
                "user_id": getattr(user, "pk", None),
            },
        )

    def logout(self, request: HttpRequest) -> None:
        user_id = getattr(getattr(request, "user", None), "pk", None)

        super().logout(request)
        auth_logger.info("sign_out", extra={"user_id": user_id})

    def save_user(
        self,
        request: HttpRequest,
        user: AbstractBaseUser,
        form: typing.Any,
        commit: bool = True,  # noqa: FBT001, FBT002 (matches allauth parent signature)
    ) -> AbstractBaseUser:
        saved = super().save_user(request, user, form, commit=commit)

        auth_logger.info(
            "sign_up",
            extra={
                "user_id": getattr(saved, "pk", None),
                "identifier": _redact_identifier(getattr(saved, "email", None)),
            },
        )

        return saved

    def confirm_email(self, request: HttpRequest, email_address: EmailAddress) -> bool:
        # `DefaultAccountAdapter.confirm_email` returns a bool; downstream
        # `mark_email_address_as_verified` treats a falsy value as "not
        # confirmed" and the headless verify view returns HTTP 500 in that
        # case. Preserve the upstream return value.
        confirmed = bool(super().confirm_email(request, email_address))

        if confirmed:
            auth_logger.info(
                "email_verification.success",
                extra={
                    "identifier": _redact_identifier(email_address.email),
                    "user_id": getattr(email_address, "user_id", None),
                },
            )

        return confirmed

    def send_password_reset_mail(
        self,
        request: HttpRequest,
        email: str,
        context: dict[str, typing.Any],
    ) -> None:
        super().send_password_reset_mail(request, email, context)
        auth_logger.info(
            "password_reset.request",
            extra={"identifier": _redact_identifier(email)},
        )

    def set_password(self, user: AbstractBaseUser, password: str) -> None:
        super().set_password(user, password)
        auth_logger.info(
            "password_reset.success",
            extra={"user_id": getattr(user, "pk", None)},
        )


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
    ) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def populate_user(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
        data: dict[str, typing.Any],
    ) -> User:
        """
        Populates user information from social provider info.

        See: https://docs.allauth.org/en/latest/socialaccount/advanced.html#creating-and-populating-user-instances
        """
        user = super().populate_user(request, sociallogin, data)
        if not user.name:
            if name := data.get("name"):
                user.name = name
            elif first_name := data.get("first_name"):
                user.name = first_name
                if last_name := data.get("last_name"):
                    user.name += f" {last_name}"
        return user
