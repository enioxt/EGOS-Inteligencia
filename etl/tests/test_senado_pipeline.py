from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd

from icarus_etl.pipelines.senado import SenadoPipeline, _make_expense_id, _parse_brl_value

FIXTURES = Path(__file__).parent / "fixtures"


def _make_pipeline() -> SenadoPipeline:
    driver = MagicMock()
    return SenadoPipeline(driver=driver, data_dir=str(FIXTURES.parent))


def _load_fixture_data(pipeline: SenadoPipeline) -> None:
    """Load CSV fixture directly into the pipeline's raw DataFrame."""
    pipeline._raw = pd.read_csv(
        FIXTURES / "senado_ceaps.csv",
        sep=";",
        dtype=str,
        encoding="latin-1",
        keep_default_na=False,
        skiprows=1,
    )


class TestSenadoPipelineMetadata:
    def test_name(self) -> None:
        assert SenadoPipeline.name == "senado"

    def test_source_id(self) -> None:
        assert SenadoPipeline.source_id == "senado"


class TestParseBrlValue:
    def test_standard_format(self) -> None:
        assert _parse_brl_value("5.000,00") == 5000.0

    def test_simple_value(self) -> None:
        assert _parse_brl_value("678,90") == 678.9

    def test_empty_string(self) -> None:
        assert _parse_brl_value("") == 0.0

    def test_invalid_value(self) -> None:
        assert _parse_brl_value("abc") == 0.0


class TestMakeExpenseId:
    def test_deterministic(self) -> None:
        id1 = _make_expense_id("SENADOR EXEMPLO", "2024-01-15", "12.345.678/0001-99", "5000.0")
        id2 = _make_expense_id("SENADOR EXEMPLO", "2024-01-15", "12.345.678/0001-99", "5000.0")
        assert id1 == id2

    def test_different_inputs_different_ids(self) -> None:
        id1 = _make_expense_id("SENADOR EXEMPLO", "2024-01-15", "12.345.678/0001-99", "5000.0")
        id2 = _make_expense_id("SENADORA TESTE", "2024-01-15", "12.345.678/0001-99", "5000.0")
        assert id1 != id2

    def test_returns_16_char_hex(self) -> None:
        result = _make_expense_id("SENADOR", "2024-01-15", "12.345.678/0001-99", "5000.0")
        assert len(result) == 16
        assert all(c in "0123456789abcdef" for c in result)


class TestSenadoTransform:
    def test_produces_expenses(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        assert len(pipeline.expenses) == 6

    def test_produces_suppliers(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        # 6 unique CNPJ suppliers
        assert len(pipeline.suppliers) == 6

    def test_normalizes_senator_names(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        names = {e["senator_name"] for e in pipeline.expenses}
        assert "SENADOR EXEMPLO" in names
        assert "SENADORA TESTE" in names
        assert "SENADOR SILVA" in names

    def test_formats_supplier_cnpj(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        cnpjs = {s.get("cnpj", "") for s in pipeline.suppliers}
        assert "12.345.678/0001-99" in cnpjs

    def test_parses_values(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        values = {e["value"] for e in pipeline.expenses}
        assert 5000.0 in values
        assert 1234.56 in values

    def test_parses_dates(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        dates = {e["date"] for e in pipeline.expenses}
        assert "2024-01-15" in dates

    def test_expense_fields(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        e = pipeline.expenses[0]
        assert "expense_id" in e
        assert "senator_name" in e
        assert "type" in e
        assert "value" in e
        assert "date" in e
        assert "source" in e
        assert e["source"] == "senado"

    def test_expense_has_description(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        # First expense has DETALHAMENTO
        e = pipeline.expenses[0]
        assert e["description"]

    def test_forneceu_rels_created(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        assert len(pipeline.forneceu_rels) == 6

    def test_limit_truncates(self) -> None:
        pipeline = _make_pipeline()
        pipeline.limit = 2
        _load_fixture_data(pipeline)
        pipeline.transform()

        assert len(pipeline.expenses) <= 2

    def test_empty_dataframe_skips(self) -> None:
        pipeline = _make_pipeline()
        pipeline._raw = pd.DataFrame()
        pipeline.transform()

        assert len(pipeline.expenses) == 0

    def test_skips_rows_without_supplier_doc(self) -> None:
        pipeline = _make_pipeline()
        pipeline._raw = pd.DataFrame([{
            "SENADOR": "TESTE",
            "TIPO_DESPESA": "Aluguel",
            "CNPJ_CPF": "",
            "FORNECEDOR": "FORNECEDOR",
            "DOCUMENTO": "DOC",
            "DATA": "15/01/2024",
            "DETALHAMENTO": "Teste",
            "VALOR_REEMBOLSADO": "1.000,00",
        }])
        pipeline.transform()

        assert len(pipeline.expenses) == 0


class TestSenadoLoad:
    def test_loads_expense_nodes(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        expense_calls = [
            c for c in run_calls if "MERGE (n:Expense" in str(c)
        ]
        assert len(expense_calls) >= 1

    def test_loads_company_supplier_nodes(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        company_calls = [
            c for c in run_calls if "MERGE (n:Company" in str(c)
        ]
        assert len(company_calls) >= 1

    def test_creates_forneceu_relationships(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        forneceu_calls = [
            c for c in run_calls if "FORNECEU" in str(c)
        ]
        assert len(forneceu_calls) >= 1

    def test_empty_expenses_skips_load(self) -> None:
        pipeline = _make_pipeline()
        pipeline.expenses = []
        pipeline.suppliers = []
        pipeline.forneceu_rels = []
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        assert session_mock.run.call_count == 0
