from __future__ import annotations

JsonScalar = str | int | float | bool | None
JsonValue = JsonScalar | "JsonArray" | "JsonObject"
JsonArray = list[JsonValue]
JsonObject = dict[str, JsonValue]
