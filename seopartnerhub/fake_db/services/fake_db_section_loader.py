from __future__ import annotations

import json
import logging
from pathlib import Path
from threading import Lock

logger = logging.getLogger(__name__)


class FakeDbSectionLoader:
    """STUB DATA loader for ``seopartnerhub/fake_db/data/``.

    Reads JSON fixtures lazily and caches them in-process. The on-disk layout
    mirrors ``frontend/full-version/src/fake-db-json/``:

        data/
          apps/<filename>.json    e.g. apps/academy.json
          pages/<filename>.json   e.g. pages/userProfile.json

    Public API: :meth:`load`, :meth:`manifest`.
    """

    _ALLOWED_GROUPS: frozenset[str] = frozenset({"apps", "pages"})

    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir
        self._cache: dict[tuple[str, str], object] = {}
        self._lock = Lock()

    def load(self, group: str, section: str) -> object:
        """Return parsed JSON for ``<group>/<section>.json`` or raise
        :class:`FileNotFoundError` / :class:`ValueError` if absent.
        """
        if group not in self._ALLOWED_GROUPS:
            raise ValueError("unknown fake-db group", {"group": group})

        if not section.replace("-", "").replace("_", "").isalnum():
            raise ValueError("invalid fake-db section name", {"section": section})

        cache_key = (group, section)
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        path = self._data_dir / group / f"{section}.json"
        if not path.is_file():
            raise FileNotFoundError(str(path))

        with self._lock:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached

            with path.open(encoding="utf-8") as handle:
                payload = json.load(handle)

            self._cache[cache_key] = payload
            logger.info(
                "fake_db_section_loaded",
                extra={"group": group, "section": section, "path": str(path)},
            )
            return payload

    def manifest(self) -> dict[str, list[str]]:
        """Return ``{group: [sections...]}`` listing every JSON fixture on
        disk. Used by ``/api/fake-db/manifest/`` so the frontend can discover
        available stub sections.
        """
        result: dict[str, list[str]] = {}
        for group in sorted(self._ALLOWED_GROUPS):
            group_dir = self._data_dir / group
            if not group_dir.is_dir():
                result[group] = []
                continue
            result[group] = sorted(p.stem for p in group_dir.glob("*.json"))
        return result
