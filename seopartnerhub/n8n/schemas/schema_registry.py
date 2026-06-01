from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel
from pydantic import ValidationError

from seopartnerhub.n8n.schemas.process_kind import ProcessKind
from seopartnerhub.n8n.schemas.telegram_post_settings import TelegramPostSettings

if TYPE_CHECKING:
    from seopartnerhub.n8n.schemas.json_value import JsonObject


class SchemaRegistry:
    """Maps :class:`ProcessKind` to its typed Pydantic settings schema."""

    _SCHEMAS: dict[str, type[BaseModel]] = {
        ProcessKind.TELEGRAM_POST.value: TelegramPostSettings,
    }

    @classmethod
    def get_schema(cls, kind: str) -> type[BaseModel]:
        try:
            return cls._SCHEMAS[kind]
        except KeyError as exc:
            msg = "unknown_process_kind"
            raise ValueError(msg) from exc

    @classmethod
    def validate(cls, kind: str, payload: JsonObject) -> JsonObject:
        """Validate ``payload`` for ``kind``; return the canonical dict.

        Raises :class:`pydantic.ValidationError` on invalid input.
        """

        schema = cls.get_schema(kind)
        instance = schema.model_validate(payload)
        return instance.model_dump(mode="json", exclude_none=False)

    @classmethod
    def is_known_kind(cls, kind: str) -> bool:
        return kind in cls._SCHEMAS


__all__ = ["SchemaRegistry", "ValidationError"]
