from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd

from icarus_etl.pipelines.cvm import CvmPipeline

FIXTURES = Path(__file__).parent / "fixtures"


def _make_pipeline() -> CvmPipeline:
    driver = MagicMock()
    return CvmPipeline(driver=driver, data_dir=str(FIXTURES.parent))


def _load_fixture_data(pipeline: CvmPipeline) -> None:
    """Load CSV fixtures directly into the pipeline's raw DataFrames."""
    pipeline._raw_processos = pd.read_csv(
        FIXTURES / "cvm_pas_processo.csv",
        sep=";",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8",
    )
    pipeline._raw_acusados = pd.read_csv(
        FIXTURES / "cvm_pas_resultado.csv",
        sep=";",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8",
    )


class TestCvmPipelineMetadata:
    def test_name(self) -> None:
        assert CvmPipeline.name == "cvm"

    def test_source_id(self) -> None:
        assert CvmPipeline.source_id == "cvm"


class TestCvmTransform:
    def test_produces_proceedings(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        assert len(pipeline.proceedings) == 5

    def test_produces_accused_entities(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        assert len(pipeline.accused_entities) == 6

    def test_normalizes_names(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        names = {e["entity_name"] for e in pipeline.accused_entities}
        assert "ACME INVESTIMENTOS SA" in names
        assert "JOAO DA SILVA" in names

    def test_parses_dates(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        dates = {p["date"] for p in pipeline.proceedings}
        assert "2023-03-15" in dates
        assert "2024-01-10" in dates

    def test_proceeding_fields(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        p = pipeline.proceedings[0]
        assert "pas_id" in p
        assert "date" in p
        assert "status" in p
        assert "description" in p
        assert "source" in p
        assert p["source"] == "cvm"

    def test_proceeding_status_from_fase(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        statuses = {p["status"] for p in pipeline.proceedings}
        assert "Finalizado" in statuses
        assert "Em andamento" in statuses

    def test_proceeding_description_from_ementa(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        first = pipeline.proceedings[0]
        assert "Termo de Acusacao" in first["description"]

    def test_nup_as_pas_id(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        ids = {p["pas_id"] for p in pipeline.proceedings}
        assert "19957000073202414" in ids

    def test_accused_linked_to_nup(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        # NUP 19957000073202414 has 2 accused
        nup_accused = [
            e for e in pipeline.accused_entities
            if e["target_key"] == "19957000073202414"
        ]
        assert len(nup_accused) == 2

    def test_limit_truncates(self) -> None:
        pipeline = _make_pipeline()
        pipeline.limit = 2
        _load_fixture_data(pipeline)
        pipeline.transform()

        assert len(pipeline.proceedings) <= 2

    def test_deduplicates_proceedings(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        # Add duplicate row
        pipeline._raw_processos = pd.concat(
            [pipeline._raw_processos, pipeline._raw_processos.iloc[:1]],
            ignore_index=True,
        )
        pipeline.transform()

        ids = [p["pas_id"] for p in pipeline.proceedings]
        assert len(ids) == len(set(ids))

    def test_skips_empty_nup(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        # Add row with empty NUP
        empty_row = pd.DataFrame([{"NUP": "", "Objeto": "x", "Ementa": "x",
                                    "Data_Abertura": "", "Componente_Organizacional_Instrucao": "",
                                    "Fase_Atual": "", "Subfase_Atual": "", "Local_Atual": "",
                                    "Data_Ultima_Movimentacao": ""}])
        pipeline._raw_processos = pd.concat(
            [pipeline._raw_processos, empty_row], ignore_index=True,
        )
        pipeline.transform()

        assert len(pipeline.proceedings) == 5


class TestCvmLoad:
    def test_loads_proceeding_nodes(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        proceeding_calls = [
            c for c in run_calls if "MERGE (n:CVMProceeding" in str(c)
        ]
        assert len(proceeding_calls) >= 1

    def test_creates_cvm_sancionada_relationships(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        rel_calls = [
            c for c in run_calls if "CVM_SANCIONADA" in str(c)
        ]
        assert len(rel_calls) >= 1

    def test_empty_proceedings_skips_load(self) -> None:
        pipeline = _make_pipeline()
        pipeline.proceedings = []
        pipeline.accused_entities = []
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        assert session_mock.run.call_count == 0

    def test_name_based_matching_query(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        rel_calls = [
            c for c in run_calls if "CVM_SANCIONADA" in str(c)
        ]
        # Verify query uses name-based matching (no cpf/cnpj)
        for call in rel_calls:
            query = str(call[0][0])
            assert "entity_name" in query
