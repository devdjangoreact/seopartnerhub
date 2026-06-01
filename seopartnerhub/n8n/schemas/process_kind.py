from __future__ import annotations

from django.db import models


class ProcessKind(models.TextChoices):
    """Enumeration of supported automation process kinds."""

    TELEGRAM_POST = "telegram_post", "Telegram post"
