from __future__ import annotations

from enum import Enum

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class TelegramParseMode(str, Enum):
    MARKDOWN_V2 = "MarkdownV2"
    HTML = "HTML"


class TelegramPostSettings(BaseModel):
    """Typed settings schema for processes of kind ``telegram_post``."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    chat_id: str = Field(min_length=1, description="Telegram chat or channel id")
    message: str = Field(min_length=1, description="Message body to send")
    parse_mode: TelegramParseMode | None = Field(
        default=None,
        description="Optional Telegram parse mode",
    )
    disable_web_page_preview: bool = Field(default=False)
