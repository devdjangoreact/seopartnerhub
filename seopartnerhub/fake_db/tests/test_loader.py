from __future__ import annotations

import json
from pathlib import Path

import pytest

from seopartnerhub.fake_db.services.fake_db_section_loader import FakeDbSectionLoader

_HERE = Path(__file__).resolve().parent
_DATA_DIR = _HERE.parent / "data"


class TestFakeDbSectionLoader:
    @pytest.fixture
    def loader(self) -> FakeDbSectionLoader:
        return FakeDbSectionLoader(data_dir=_DATA_DIR)

    def test_manifest_lists_all_sections(self, loader: FakeDbSectionLoader) -> None:
        manifest = loader.manifest()

        assert set(manifest.keys()) == {"apps", "pages"}
        assert "userProfile" in manifest["pages"]
        assert "academy" in manifest["apps"]

    def test_load_pages_user_profile_returns_parsed_json(
        self, loader: FakeDbSectionLoader
    ) -> None:
        payload = loader.load(group="pages", section="userProfile")

        raw = json.loads((_DATA_DIR / "pages" / "userProfile.json").read_text("utf-8"))

        assert payload == raw

    def test_load_caches_result(self, loader: FakeDbSectionLoader) -> None:
        first = loader.load(group="apps", section="academy")
        second = loader.load(group="apps", section="academy")

        assert first is second

    def test_unknown_group_raises(self, loader: FakeDbSectionLoader) -> None:
        with pytest.raises(ValueError, match="unknown fake-db group"):
            loader.load(group="evil", section="academy")

    def test_invalid_section_raises(self, loader: FakeDbSectionLoader) -> None:
        with pytest.raises(ValueError, match="invalid fake-db section name"):
            loader.load(group="apps", section="../etc/passwd")

    def test_missing_section_raises(self, loader: FakeDbSectionLoader) -> None:
        with pytest.raises(FileNotFoundError):
            loader.load(group="apps", section="does_not_exist")
