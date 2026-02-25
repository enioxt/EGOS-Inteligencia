from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd

from icarus_etl.pipelines.caged import (
    CagedPipeline,
    _build_movement_date,
    _generate_movement_id,
    _parse_salary,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _make_pipeline() -> CagedPipeline:
    driver = MagicMock()
    pipeline = CagedPipeline(driver=driver, data_dir=str(FIXTURES.parent))
    return pipeline


def _load_fixture_data(pipeline: CagedPipeline) -> None:
    """Load CSV fixture directly into the pipeline's raw DataFrame."""
    pipeline._raw = pd.read_csv(
        FIXTURES / "caged" / "caged.csv",
        dtype=str,
        keep_default_na=False,
    )


class TestCagedPipelineMetadata:
    def test_name(self) -> None:
        assert CagedPipeline.name == "caged"

    def test_source_id(self) -> None:
        assert CagedPipeline.source_id == "caged"


class TestGenerateMovementId:
    def test_deterministic(self) -> None:
        id1 = _generate_movement_id("12345678000100", "12345678901", "2023-06", "admissao")
        id2 = _generate_movement_id("12345678000100", "12345678901", "2023-06", "admissao")
        assert id1 == id2

    def test_different_inputs_different_ids(self) -> None:
        id1 = _generate_movement_id("12345678000100", "12345678901", "2023-06", "admissao")
        id2 = _generate_movement_id("98765432000100", "98765432109", "2023-07", "desligamento")
        assert id1 != id2

    def test_length(self) -> None:
        movement_id = _generate_movement_id("12345678000100", "12345678901", "2023-06", "admissao")
        assert len(movement_id) == 16


class TestBuildMovementDate:
    def test_pads_single_digit_month(self) -> None:
        assert _build_movement_date("2023", "6") == "2023-06"

    def test_double_digit_month(self) -> None:
        assert _build_movement_date("2023", "12") == "2023-12"


class TestParseSalary:
    def test_simple_float(self) -> None:
        assert _parse_salary("2500.00") == 2500.0

    def test_brazilian_format(self) -> None:
        assert _parse_salary("1.500,50") == 1500.5

    def test_comma_decimal(self) -> None:
        assert _parse_salary("1800,50") == 1800.5

    def test_empty_returns_none(self) -> None:
        assert _parse_salary("") is None

    def test_negative_returns_none(self) -> None:
        assert _parse_salary("-100") is None

    def test_unicode_minus_returns_none(self) -> None:
        assert _parse_salary("\u2212100") is None


class TestCagedTransform:
    def test_produces_movements(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        # 5 rows: row 4 has CNPJ "123" (3 digits, invalid), rest are 8-digit roots padded to 14
        assert len(pipeline.movements) == 4

    def test_produces_company_rels(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        assert len(pipeline.company_rels) == 4

    def test_formats_cnpj(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        cnpjs = {m["cnpj"] for m in pipeline.movements}
        assert "12.345.678/0001-00" in cnpjs
        assert "98.765.432/0001-00" in cnpjs

    def test_skips_invalid_cnpj(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        cnpjs = {m["cnpj"] for m in pipeline.movements}
        # Row with CNPJ "123" should be skipped
        for cnpj in cnpjs:
            assert len(cnpj) == 18  # formatted CNPJ is 18 chars

    def test_movement_fields(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        movement = pipeline.movements[0]
        assert "movement_id" in movement
        assert "cnpj" in movement
        assert "movement_type" in movement
        assert "movement_date" in movement
        assert "cbo_code" in movement
        assert "cnae_code" in movement
        assert "municipality_code" in movement
        assert "uf" in movement
        assert "source" in movement
        assert movement["source"] == "caged"

    def test_movement_id_is_deterministic_hash(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        for movement in pipeline.movements:
            assert len(movement["movement_id"]) == 16

    def test_parses_salary(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        movements_with_salary = [m for m in pipeline.movements if "salary" in m]
        assert len(movements_with_salary) >= 1

        # First row has salary 2500.00
        first = pipeline.movements[0]
        assert first["salary"] == 2500.0

    def test_movement_types(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        types = {m["movement_type"] for m in pipeline.movements}
        assert "admissao" in types
        assert "desligamento" in types

    def test_movement_date_format(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        for movement in pipeline.movements:
            date = movement["movement_date"]
            assert len(date) == 7  # YYYY-MM
            assert date[4] == "-"

    def test_company_rels_link_cnpj_to_movement_id(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        for rel in pipeline.company_rels:
            assert "source_key" in rel  # CNPJ
            assert "target_key" in rel  # movement_id
            assert "." in rel["source_key"]  # formatted CNPJ
            assert len(rel["target_key"]) == 16  # hash ID

    def test_no_person_rels_without_cpf(self) -> None:
        """Fixture rows have no CPF column, so person_rels should be empty."""
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        assert len(pipeline.person_rels) == 0

    def test_pads_8_digit_cnpj_root(self) -> None:
        """8-digit cnpj_raiz should be padded to 14 digits (root + 000100)."""
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        cnpjs = {m["cnpj"] for m in pipeline.movements}
        # 12345678 -> 12345678000100 -> 12.345.678/0001-00
        assert "12.345.678/0001-00" in cnpjs


class TestCagedLoad:
    def test_load_creates_labor_movement_nodes(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        movement_calls = [
            call for call in run_calls
            if "MERGE (n:LaborMovement" in str(call)
        ]
        assert len(movement_calls) >= 1

    def test_load_creates_company_nodes(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        company_calls = [
            call for call in run_calls
            if "MERGE (n:Company" in str(call)
        ]
        assert len(company_calls) >= 1

    def test_load_creates_movimentou_relationships(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        rel_calls = [
            call for call in run_calls
            if "MOVIMENTOU" in str(call)
        ]
        assert len(rel_calls) >= 1

    def test_load_skips_when_empty(self) -> None:
        pipeline = _make_pipeline()
        # Don't load fixture data -- movements and rels remain empty
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        assert session_mock.run.call_count == 0
