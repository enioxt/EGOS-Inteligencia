from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd

from icarus_etl.pipelines.ceaf import CeafPipeline

FIXTURES = Path(__file__).parent / "fixtures"


def _make_pipeline() -> CeafPipeline:
    driver = MagicMock()
    pipeline = CeafPipeline(driver=driver, data_dir=str(FIXTURES.parent))
    return pipeline


def _load_fixture_data(pipeline: CeafPipeline) -> None:
    """Load CSV fixture directly into the pipeline's raw DataFrame."""
    pipeline._raw = pd.read_csv(
        FIXTURES / "ceaf" / "ceaf.csv",
        dtype=str,
        keep_default_na=False,
    )


class TestCeafPipelineMetadata:
    def test_name(self) -> None:
        assert CeafPipeline.name == "ceaf"

    def test_source_id(self) -> None:
        assert CeafPipeline.source_id == "ceaf"


class TestCeafTransform:
    def test_produces_expulsions(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        # All 5 rows have names, so all produce expulsions (masked CPFs kept)
        assert len(pipeline.expulsions) == 5

    def test_produces_person_rels(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        assert len(pipeline.person_rels) == 3

    def test_normalizes_names(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        names = {e["name"] for e in pipeline.expulsions}
        assert "JOAO DA SILVA" in names
        assert "MARIA SOUZA" in names
        assert "PEDRO SANTOS" in names

    def test_formats_cpf(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        cpfs = {e["cpf"] for e in pipeline.expulsions}
        assert "529.982.247-25" in cpfs
        assert "111.444.777-35" in cpfs
        assert "987.654.321-00" in cpfs

    def test_skips_invalid_cpf_from_person_rels(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        # Invalid CPF rows are kept as expulsions but NOT linked to Person nodes
        rel_cpfs = {r["source_key"] for r in pipeline.person_rels}
        assert len(pipeline.person_rels) == 3
        assert all(len(c.replace(".", "").replace("-", "")) == 11 for c in rel_cpfs)

    def test_empty_cpf_kept_as_expulsion(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        # Empty CPF row is kept as expulsion but not linked to Person
        names = {e["name"] for e in pipeline.expulsions}
        assert "SEM CPF" in names
        rel_names = {r.get("person_name") for r in pipeline.person_rels}
        assert "SEM CPF" not in rel_names

    def test_parses_date(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        dates = {e["date"] for e in pipeline.expulsions}
        assert "2020-03-15" in dates
        assert "2021-07-01" in dates
        assert "2022-12-10" in dates

    def test_expulsion_fields(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        e = pipeline.expulsions[0]
        assert "expulsion_id" in e
        assert "cpf" in e
        assert "name" in e
        assert "position" in e
        assert "punishment_type" in e
        assert "date" in e
        assert "decree" in e
        assert "uf" in e
        assert "source" in e
        assert e["source"] == "ceaf"

    def test_expulsion_id_format(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        for e in pipeline.expulsions:
            assert e["expulsion_id"].startswith("ceaf_")

    def test_punishment_types_preserved(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        types = {e["punishment_type"] for e in pipeline.expulsions}
        assert "Demissão" in types or "Demissao" in types
        assert "Cassação de Aposentadoria" in types or "Cassacao de Aposentadoria" in types


class TestCeafLoad:
    def test_load_creates_expulsion_nodes(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        expulsion_calls = [
            call for call in run_calls
            if "MERGE (n:Expulsion" in str(call)
        ]
        assert len(expulsion_calls) >= 1

    def test_load_creates_person_nodes(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        person_calls = [
            call for call in run_calls
            if "MERGE (n:Person" in str(call)
        ]
        assert len(person_calls) >= 1

    def test_load_creates_expulso_relationships(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        rel_calls = [
            call for call in run_calls
            if "EXPULSO" in str(call)
        ]
        assert len(rel_calls) >= 1
