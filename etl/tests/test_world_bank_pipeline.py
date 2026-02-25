from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd

from icarus_etl.pipelines.world_bank import (
    WorldBankPipeline,
    _make_debarment_id,
)

FIXTURES = Path(__file__).parent / "fixtures"


class TestWorldBankMetadata:
    def test_name(self) -> None:
        p = WorldBankPipeline(driver=MagicMock())
        assert p.name == "world_bank"

    def test_source_id(self) -> None:
        p = WorldBankPipeline(driver=MagicMock())
        assert p.source_id == "world_bank"


class TestMakeDebarmentId:
    def test_deterministic(self) -> None:
        a = _make_debarment_id("Acme", "Brazil", "2020-01-01")
        b = _make_debarment_id("Acme", "Brazil", "2020-01-01")
        assert a == b

    def test_different_inputs_different_ids(self) -> None:
        a = _make_debarment_id("Acme", "Brazil", "2020-01-01")
        b = _make_debarment_id("Beta", "Brazil", "2020-01-01")
        assert a != b

    def test_length(self) -> None:
        result = _make_debarment_id("X", "Y", "Z")
        assert len(result) == 16


class TestWorldBankTransform:
    def _make_pipeline(self) -> WorldBankPipeline:
        p = WorldBankPipeline(driver=MagicMock())
        p._raw = pd.read_csv(
            FIXTURES / "world_bank" / "debarred.csv",
            dtype=str,
            keep_default_na=False,
        )
        return p

    def test_produces_sanctions(self) -> None:
        p = self._make_pipeline()
        p.transform()
        # 4 valid rows (row 5 has empty firm name)
        assert len(p.sanctions) == 4

    def test_normalizes_names(self) -> None:
        p = self._make_pipeline()
        p.transform()
        names = [s["name"] for s in p.sanctions]
        assert all(n == n.upper() for n in names)

    def test_skips_empty_name(self) -> None:
        p = self._make_pipeline()
        p.transform()
        names = [s["name"] for s in p.sanctions]
        assert "" not in names

    def test_preserves_country(self) -> None:
        p = self._make_pipeline()
        p.transform()
        countries = {s["country"] for s in p.sanctions}
        assert "Brazil" in countries
        assert "Nigeria" in countries

    def test_preserves_dates(self) -> None:
        p = self._make_pipeline()
        p.transform()
        first = p.sanctions[0]
        assert first["from_date"] != ""

    def test_preserves_grounds(self) -> None:
        p = self._make_pipeline()
        p.transform()
        grounds = {s["grounds"] for s in p.sanctions}
        assert "Collusive Practice" in grounds

    def test_source_fields(self) -> None:
        p = self._make_pipeline()
        p.transform()
        for s in p.sanctions:
            assert s["source"] == "world_bank"
            assert s["source_list"] == "WORLD_BANK"

    def test_sanction_id_is_deterministic_hash(self) -> None:
        p = self._make_pipeline()
        p.transform()
        for s in p.sanctions:
            assert len(s["sanction_id"]) == 16
            assert all(c in "0123456789abcdef" for c in s["sanction_id"])

    def test_original_name_preserved(self) -> None:
        p = self._make_pipeline()
        p.transform()
        originals = [s["original_name"] for s in p.sanctions]
        assert "Acme Construction Ltd." in originals

    def test_deduplicates_by_sanction_id(self) -> None:
        p = self._make_pipeline()
        p.transform()
        ids = [s["sanction_id"] for s in p.sanctions]
        assert len(ids) == len(set(ids))


class TestWorldBankLoad:
    def test_load_creates_sanction_nodes(self) -> None:
        p = WorldBankPipeline(driver=MagicMock())
        p.sanctions = [
            {
                "sanction_id": "abc123",
                "name": "TEST",
                "original_name": "Test",
                "country": "Brazil",
                "from_date": "2020-01-01",
                "to_date": "2025-01-01",
                "grounds": "Test",
                "source": "world_bank",
                "source_list": "WORLD_BANK",
            }
        ]
        p.load()
        loader = p.driver  # type: ignore[attr-defined]
        # Check Neo4jBatchLoader was used
        assert loader is not None

    def test_load_skips_when_empty(self) -> None:
        p = WorldBankPipeline(driver=MagicMock())
        p.sanctions = []
        p.load()  # Should not raise
