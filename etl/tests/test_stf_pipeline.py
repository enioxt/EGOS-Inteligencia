from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd

from icarus_etl.pipelines.stf import StfPipeline, _generate_case_id

FIXTURES = Path(__file__).parent / "fixtures"


def _make_pipeline() -> StfPipeline:
    driver = MagicMock()
    pipeline = StfPipeline(driver=driver, data_dir=str(FIXTURES.parent))
    return pipeline


def _load_fixture_data(pipeline: StfPipeline) -> None:
    """Load CSV fixture directly into the pipeline's raw DataFrame."""
    pipeline._raw = pd.read_csv(
        FIXTURES / "stf" / "decisoes.csv",
        dtype=str,
        keep_default_na=False,
    )


class TestStfPipelineMetadata:
    def test_name(self) -> None:
        assert StfPipeline.name == "stf"

    def test_source_id(self) -> None:
        assert StfPipeline.source_id == "stf"


class TestGenerateCaseId:
    def test_deterministic(self) -> None:
        id1 = _generate_case_id("ADI", "6341", "2020")
        id2 = _generate_case_id("ADI", "6341", "2020")
        assert id1 == id2

    def test_different_inputs_different_ids(self) -> None:
        id1 = _generate_case_id("ADI", "6341", "2020")
        id2 = _generate_case_id("ADPF", "672", "2020")
        assert id1 != id2

    def test_length(self) -> None:
        case_id = _generate_case_id("ADI", "6341", "2020")
        assert len(case_id) == 16

    def test_hex_characters(self) -> None:
        case_id = _generate_case_id("RE", "1017365", "2021")
        assert all(c in "0123456789abcdef" for c in case_id)


class TestStfTransform:
    def test_produces_cases(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        # 5 rows, but ADI 6341 2020 appears twice -> dedup to 4
        assert len(pipeline.cases) == 4

    def test_produces_rapporteur_rels(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        # 5 rows total, 1 has empty rapporteur -> 4 rels (before dedup)
        # But ADI 6341 2020 produces 2 rels with same source/target
        assert len(pipeline.rapporteur_rels) == 4

    def test_normalizes_rapporteur_name(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        rapporteurs = {c["rapporteur"] for c in pipeline.cases}
        assert "MARCO AURELIO" in rapporteurs
        assert "ALEXANDRE DE MORAES" in rapporteurs
        assert "EDSON FACHIN" in rapporteurs

    def test_skips_empty_required_fields(self) -> None:
        pipeline = _make_pipeline()
        pipeline._raw = pd.DataFrame(
            [
                {
                    "classe": "",
                    "numero": "123",
                    "ano": "2020",
                    "relator": "X",
                    "tipo_decisao": "",
                    "data_decisao": "",
                    "assunto": "",
                    "procedencia": "",
                },
                {
                    "classe": "ADI",
                    "numero": "",
                    "ano": "2020",
                    "relator": "X",
                    "tipo_decisao": "",
                    "data_decisao": "",
                    "assunto": "",
                    "procedencia": "",
                },
                {
                    "classe": "ADI",
                    "numero": "123",
                    "ano": "",
                    "relator": "X",
                    "tipo_decisao": "",
                    "data_decisao": "",
                    "assunto": "",
                    "procedencia": "",
                },
            ]
        )
        pipeline.transform()
        assert len(pipeline.cases) == 0

    def test_skips_rapporteur_rel_when_empty(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        # HC 164493 has empty rapporteur
        rel_targets = {r["target_key"] for r in pipeline.rapporteur_rels}
        hc_case_id = _generate_case_id("HC", "164493", "2019")
        assert hc_case_id not in rel_targets

    def test_case_fields(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        case = pipeline.cases[0]
        expected_fields = {
            "case_id",
            "case_class",
            "case_number",
            "year",
            "rapporteur",
            "decision_type",
            "decision_date",
            "subject",
            "origin",
            "source",
        }
        assert expected_fields.issubset(case.keys())
        assert case["source"] == "stf"

    def test_case_id_is_deterministic_hash(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        for case in pipeline.cases:
            assert len(case["case_id"]) == 16

    def test_deduplicates_cases(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        # ADI 6341 2020 appears twice in fixture, should be deduped
        case_ids = [c["case_id"] for c in pipeline.cases]
        assert len(case_ids) == len(set(case_ids))

    def test_preserves_origin(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        origins = {c["origin"] for c in pipeline.cases}
        assert "DF" in origins
        assert "SC" in origins
        assert "SP" in origins

    def test_rapporteur_rels_link_name_to_case_id(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        for rel in pipeline.rapporteur_rels:
            assert "source_key" in rel  # rapporteur name
            assert "target_key" in rel  # case_id
            assert len(rel["target_key"]) == 16  # hash ID


class TestStfLoad:
    def test_load_creates_legal_case_nodes(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        case_calls = [call for call in run_calls if "MERGE (n:LegalCase" in str(call)]
        assert len(case_calls) >= 1

    def test_load_creates_relator_de_relationships(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        rel_calls = [call for call in run_calls if "RELATOR_DE" in str(call)]
        assert len(rel_calls) >= 1

    def test_load_skips_when_empty(self) -> None:
        pipeline = _make_pipeline()
        # Don't load fixture data — cases and rapporteur_rels remain empty
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        assert session_mock.run.call_count == 0

    def test_load_skips_rels_when_no_rapporteurs(self) -> None:
        pipeline = _make_pipeline()
        pipeline._raw = pd.DataFrame(
            [
                {
                    "classe": "HC",
                    "numero": "164493",
                    "ano": "2019",
                    "relator": "",
                    "tipo_decisao": "Acordao",
                    "data_decisao": "2019-11-07",
                    "assunto": "Execucao penal",
                    "procedencia": "SP",
                },
            ]
        )
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        # Should have LegalCase MERGE but no RELATOR_DE
        case_calls = [c for c in run_calls if "LegalCase" in str(c)]
        rel_calls = [c for c in run_calls if "RELATOR_DE" in str(c)]
        assert len(case_calls) >= 1
        assert len(rel_calls) == 0
