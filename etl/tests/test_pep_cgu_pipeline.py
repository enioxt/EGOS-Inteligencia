from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd

from icarus_etl.pipelines.pep_cgu import PepCguPipeline

FIXTURES = Path(__file__).parent / "fixtures"


def _make_pipeline(*, limit: int | None = None) -> PepCguPipeline:
    driver = MagicMock()
    return PepCguPipeline(driver=driver, data_dir=str(FIXTURES), limit=limit)


def _load_fixture(pipeline: PepCguPipeline) -> None:
    """Load CSV fixture directly into the pipeline's raw DataFrame."""
    pipeline._raw = pd.read_csv(
        FIXTURES / "pep_cgu" / "pep.csv",
        sep=";",
        dtype=str,
        keep_default_na=False,
    )


class TestPepCguPipelineMetadata:
    def test_name(self) -> None:
        assert PepCguPipeline.name == "pep_cgu"

    def test_source_id(self) -> None:
        assert PepCguPipeline.source_id == "cgu_pep"


class TestPepCguExtract:
    def test_extract_reads_csv(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        # 5 rows total in fixture (3 valid + 2 invalid CPFs)
        assert len(pipeline._raw) == 5

    def test_extract_raises_when_missing(self) -> None:
        driver = MagicMock()
        pipeline = PepCguPipeline(driver, data_dir="/nonexistent/path")
        try:
            pipeline.extract()
            raise AssertionError("Expected FileNotFoundError")
        except FileNotFoundError:
            pass


class TestPepCguTransform:
    def test_produces_pep_records(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()

        # All 5 rows have names, so all produce PEP records (masked CPFs kept)
        assert len(pipeline.pep_records) == 5

    def test_formats_cpf(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()

        cpfs = {r["cpf"] for r in pipeline.pep_records}
        assert "123.456.789-01" in cpfs
        assert "987.654.321-00" in cpfs
        assert "111.222.333-44" in cpfs

    def test_invalid_cpf_kept_but_not_linked(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()

        # Invalid/empty CPF rows are kept as PEP records but NOT linked to Person
        names = {r["name"] for r in pipeline.pep_records}
        assert "BAD RECORD" in names
        assert "EMPTY CPF" in names
        # Only 3 valid CPFs get person links
        assert len(pipeline.person_links) == 3

    def test_normalizes_names(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()

        names = {r["name"] for r in pipeline.pep_records}
        assert "JOAO DA SILVA" in names
        assert "MARIA SANTOS" in names
        assert "ANA OLIVEIRA" in names

    def test_deduplicates(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()

        pep_ids = [r["pep_id"] for r in pipeline.pep_records]
        assert len(pep_ids) == len(set(pep_ids))

    def test_record_fields(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()

        r = pipeline.pep_records[0]
        assert "pep_id" in r
        assert "cpf" in r
        assert "name" in r
        assert "role" in r
        assert "role_description" in r
        assert "level" in r
        assert "org" in r
        assert "start_date" in r
        assert "end_date" in r
        assert "grace_end_date" in r
        assert r["source"] == "cgu_pep"

    def test_parses_dates(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()

        # First record: 01/01/2023 -> 2023-01-01
        first = pipeline.pep_records[0]
        assert first["start_date"] == "2023-01-01"
        assert first["end_date"] == "2024-12-31"
        assert first["grace_end_date"] == "2025-06-30"

    def test_empty_dates_parsed(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()

        # Second record (MARIA SANTOS) has no end_date or grace_end_date
        maria = next(r for r in pipeline.pep_records if r["name"] == "MARIA SANTOS")
        assert maria["end_date"] == ""
        assert maria["grace_end_date"] == ""

    def test_person_links_created(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()

        assert len(pipeline.person_links) == 3
        source_keys = {link["source_key"] for link in pipeline.person_links}
        assert "123.456.789-01" in source_keys

    def test_respects_limit(self) -> None:
        pipeline = _make_pipeline(limit=1)
        _load_fixture(pipeline)
        pipeline.transform()

        assert len(pipeline.pep_records) <= 1

    def test_role_fields_populated(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()

        first = pipeline.pep_records[0]
        assert first["role"] == "DAS-6"
        assert first["role_description"] == "Ministro de Estado"
        assert first["level"] == "6"
        assert first["org"] == "MINISTERIO DA EDUCACAO"


class TestPepCguLoad:
    def test_loads_pep_record_nodes(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        pep_calls = [c for c in run_calls if "MERGE (n:PEPRecord" in str(c)]
        assert len(pep_calls) >= 1

    def test_loads_pep_registrada_relationships(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        rel_calls = [c for c in run_calls if "PEP_REGISTRADA" in str(c)]
        assert len(rel_calls) >= 1

    def test_empty_records_skip_load(self) -> None:
        pipeline = _make_pipeline()
        pipeline.pep_records = []
        pipeline.person_links = []
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        assert session_mock.run.call_count == 0
