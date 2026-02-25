from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd

from icarus_etl.pipelines.senado_cpis import (
    SenadoCpisPipeline,
    _make_cpi_id,
)

FIXTURES = Path(__file__).parent / "fixtures"


class TestSenadoCpisMetadata:
    def test_name(self) -> None:
        p = SenadoCpisPipeline(driver=MagicMock())
        assert p.name == "senado_cpis"

    def test_source_id(self) -> None:
        p = SenadoCpisPipeline(driver=MagicMock())
        assert p.source_id == "senado_cpis"


class TestMakeCpiId:
    def test_deterministic(self) -> None:
        a = _make_cpi_id("CPI001", "CPI da Petrobras")
        b = _make_cpi_id("CPI001", "CPI da Petrobras")
        assert a == b

    def test_different_inputs_different_ids(self) -> None:
        a = _make_cpi_id("CPI001", "CPI da Petrobras")
        b = _make_cpi_id("CPI002", "CPI do BNDES")
        assert a != b

    def test_length(self) -> None:
        result = _make_cpi_id("X", "Y")
        assert len(result) == 16


class TestSenadoCpisTransform:
    def _make_pipeline(self) -> SenadoCpisPipeline:
        p = SenadoCpisPipeline(driver=MagicMock())
        p._raw = pd.read_csv(
            FIXTURES / "senado_cpis" / "cpis.csv",
            dtype=str,
            keep_default_na=False,
        )
        return p

    def test_produces_cpis(self) -> None:
        p = self._make_pipeline()
        p.transform()
        # 3 unique CPIs (CPI001 appears twice but deduped, row 5 has no name)
        assert len(p.cpis) == 3

    def test_produces_senator_rels(self) -> None:
        p = self._make_pipeline()
        p.transform()
        # Rows 1-3 have senator names, row 4 has empty name, row 5 has no CPI name
        assert len(p.senator_rels) == 3

    def test_skips_empty_cpi_name(self) -> None:
        p = self._make_pipeline()
        p.transform()
        names = [c["name"] for c in p.cpis]
        assert "" not in names

    def test_preserves_code(self) -> None:
        p = self._make_pipeline()
        p.transform()
        codes = {c["code"] for c in p.cpis}
        assert "CPI001" in codes
        assert "CPI002" in codes

    def test_preserves_subject(self) -> None:
        p = self._make_pipeline()
        p.transform()
        subjects = {c["subject"] for c in p.cpis}
        assert "Irregularidades na Petrobras" in subjects

    def test_preserves_dates(self) -> None:
        p = self._make_pipeline()
        p.transform()
        first = next(c for c in p.cpis if c["code"] == "CPI001")
        assert first["date_start"] != ""

    def test_source_field(self) -> None:
        p = self._make_pipeline()
        p.transform()
        for c in p.cpis:
            assert c["source"] == "senado_cpis"

    def test_cpi_id_is_hex_hash(self) -> None:
        p = self._make_pipeline()
        p.transform()
        for c in p.cpis:
            assert len(c["cpi_id"]) == 16
            assert all(ch in "0123456789abcdef" for ch in c["cpi_id"])

    def test_deduplicates_cpis(self) -> None:
        p = self._make_pipeline()
        p.transform()
        ids = [c["cpi_id"] for c in p.cpis]
        assert len(ids) == len(set(ids))

    def test_senator_name_normalized(self) -> None:
        p = self._make_pipeline()
        p.transform()
        names = [r["senator_name"] for r in p.senator_rels]
        assert all(n == n.upper() for n in names)

    def test_senator_rel_role_preserved(self) -> None:
        p = self._make_pipeline()
        p.transform()
        roles = {r["role"] for r in p.senator_rels}
        assert "Presidente" in roles
        assert "Relator" in roles

    def test_senator_rel_links_to_cpi(self) -> None:
        p = self._make_pipeline()
        p.transform()
        cpi_ids = {c["cpi_id"] for c in p.cpis}
        for rel in p.senator_rels:
            assert rel["cpi_id"] in cpi_ids

    def test_skips_senator_with_empty_name(self) -> None:
        p = self._make_pipeline()
        p.transform()
        senator_names = [r["senator_name"] for r in p.senator_rels]
        assert "" not in senator_names


class TestSenadoCpisLoad:
    def test_load_creates_cpi_nodes(self) -> None:
        p = SenadoCpisPipeline(driver=MagicMock())
        p.cpis = [
            {
                "cpi_id": "abc123",
                "code": "CPI001",
                "name": "Test CPI",
                "date_start": "2020-01-01",
                "date_end": "",
                "subject": "Test",
                "source": "senado_cpis",
            }
        ]
        p.senator_rels = []
        p.load()

    def test_load_creates_participou_rels(self) -> None:
        p = SenadoCpisPipeline(driver=MagicMock())
        p.cpis = []
        p.senator_rels = [
            {
                "senator_name": "JOSE DA SILVA",
                "cpi_id": "abc123",
                "role": "Presidente",
            }
        ]
        p.load()

    def test_load_skips_when_empty(self) -> None:
        p = SenadoCpisPipeline(driver=MagicMock())
        p.cpis = []
        p.senator_rels = []
        p.load()  # Should not raise
