from __future__ import annotations

import hashlib
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd

from icarus_etl.pipelines.cpgf import CpgfPipeline, _make_expense_id, _parse_brl_value

FIXTURES = Path(__file__).parent / "fixtures"


def _make_pipeline() -> CpgfPipeline:
    driver = MagicMock()
    pipeline = CpgfPipeline(driver=driver, data_dir=str(FIXTURES.parent))
    return pipeline


def _load_fixture_data(pipeline: CpgfPipeline) -> None:
    """Load CSV fixture directly into the pipeline's raw DataFrame."""
    pipeline._raw = pd.read_csv(
        FIXTURES / "cpgf" / "cpgf.csv",
        sep="\t",
        dtype=str,
        keep_default_na=False,
    )


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------
class TestCpgfPipelineMetadata:
    def test_name(self) -> None:
        assert CpgfPipeline.name == "cpgf"

    def test_source_id(self) -> None:
        assert CpgfPipeline.source_id == "cpgf"


# ---------------------------------------------------------------------------
# Extract
# ---------------------------------------------------------------------------
class TestCpgfExtract:
    def test_extract_reads_csv(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        assert len(pipeline._raw) == 6

    def test_extract_has_expected_columns(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        assert "CPF PORTADOR" in pipeline._raw.columns
        assert "NOME PORTADOR" in pipeline._raw.columns
        assert "VALOR TRANSACAO" in pipeline._raw.columns


# ---------------------------------------------------------------------------
# Transform
# ---------------------------------------------------------------------------
class TestCpgfTransform:
    def test_produces_expenses(self) -> None:
        """5 rows with names and non-zero amounts (masked CPFs kept). Zero amount skipped."""
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        assert len(pipeline.expenses) == 5

    def test_produces_cardholders(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        assert len(pipeline.cardholders) == 3

    def test_produces_gastou_cartao_rels(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        assert len(pipeline.gastou_cartao_rels) == 3

    def test_normalizes_names(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        names = {e["cardholder_name"] for e in pipeline.expenses}
        assert "JOAO DA SILVA" in names
        assert "MARIA SOUZA" in names
        assert "PEDRO SANTOS" in names

    def test_formats_cpf(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        cpfs = {e["cardholder_cpf"] for e in pipeline.expenses}
        assert "529.982.247-25" in cpfs
        assert "111.444.777-35" in cpfs
        assert "987.654.321-00" in cpfs

    def test_invalid_cpf_kept_but_not_linked(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        names = {e["cardholder_name"] for e in pipeline.expenses}
        assert "NOME INVALIDO" in names
        # Only 3 valid CPFs get person links
        assert len(pipeline.cardholders) == 3
        assert len(pipeline.gastou_cartao_rels) == 3

    def test_empty_cpf_kept_as_expense(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        names = {e["cardholder_name"] for e in pipeline.expenses}
        assert "SEM CPF" in names
        rel_cpfs = {r["source_key"] for r in pipeline.gastou_cartao_rels}
        assert "" not in rel_cpfs

    def test_filters_zero_amount(self) -> None:
        """Ana Oliveira has amount 0,00 — should be filtered out."""
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        names = {e["cardholder_name"] for e in pipeline.expenses}
        assert "ANA OLIVEIRA" not in names

    def test_parses_amounts(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        amounts = {e["amount"] for e in pipeline.expenses}
        assert 1234.56 in amounts
        assert 2500.00 in amounts
        assert 350.75 in amounts

    def test_parses_dates(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        dates = {e["date"] for e in pipeline.expenses}
        assert "2024-03-15" in dates
        assert "2024-04-20" in dates
        assert "2024-05-10" in dates

    def test_expense_fields(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        e = pipeline.expenses[0]
        assert "expense_id" in e
        assert "cardholder_name" in e
        assert "cardholder_cpf" in e
        assert "agency" in e
        assert "amount" in e
        assert "date" in e
        assert "description" in e
        assert "transaction_type" in e
        assert "source" in e
        assert e["source"] == "cpgf"

    def test_agency_preserved(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        agencies = {e["agency"] for e in pipeline.expenses}
        assert "MINISTERIO DA EDUCACAO" in agencies
        assert "PRESIDENCIA DA REPUBLICA" in agencies
        assert "MINISTERIO DA SAUDE" in agencies

    def test_transaction_type_preserved(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        types = {e["transaction_type"] for e in pipeline.expenses}
        assert "Compra com cartao" in types

    def test_deduplicates_expenses(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        ids = [e["expense_id"] for e in pipeline.expenses]
        assert len(ids) == len(set(ids))

    def test_limit_caps_expenses(self) -> None:
        pipeline = _make_pipeline()
        pipeline.limit = 1
        _load_fixture_data(pipeline)
        pipeline.transform()
        assert len(pipeline.expenses) <= 1

    def test_empty_dataframe_produces_no_output(self) -> None:
        pipeline = _make_pipeline()
        pipeline._raw = pd.DataFrame()
        pipeline.transform()
        assert len(pipeline.expenses) == 0
        assert len(pipeline.cardholders) == 0
        assert len(pipeline.gastou_cartao_rels) == 0


# ---------------------------------------------------------------------------
# Expense ID hash
# ---------------------------------------------------------------------------
class TestExpenseIdHash:
    def test_deterministic(self) -> None:
        id1 = _make_expense_id("529.982.247-25", "2024-03-15", "1234.56", "COMPANHIA AEREA XYZ")
        id2 = _make_expense_id("529.982.247-25", "2024-03-15", "1234.56", "COMPANHIA AEREA XYZ")
        assert id1 == id2

    def test_different_inputs_different_ids(self) -> None:
        id1 = _make_expense_id("529.982.247-25", "2024-03-15", "100.0", "X")
        id2 = _make_expense_id("529.982.247-25", "2024-03-15", "200.0", "X")
        assert id1 != id2

    def test_length(self) -> None:
        expense_id = _make_expense_id("529.982.247-25", "2024-03-15", "100.0", "X")
        assert len(expense_id) == 16

    def test_hex_chars_only(self) -> None:
        expense_id = _make_expense_id("529.982.247-25", "2024-03-15", "100.0", "X")
        assert all(c in "0123456789abcdef" for c in expense_id)

    def test_matches_sha256_prefix(self) -> None:
        cpf = "529.982.247-25"
        date = "2024-03-15"
        amount = "100.0"
        desc = "TEST"
        expected = hashlib.sha256(f"cpgf_{cpf}_{date}_{amount}_{desc}".encode()).hexdigest()[:16]
        assert _make_expense_id(cpf, date, amount, desc) == expected


# ---------------------------------------------------------------------------
# BRL Value Parsing
# ---------------------------------------------------------------------------
class TestParseBrlValue:
    def test_normal_value(self) -> None:
        assert _parse_brl_value("1.234,56") == 1234.56

    def test_zero(self) -> None:
        assert _parse_brl_value("0,00") == 0.0

    def test_empty(self) -> None:
        assert _parse_brl_value("") == 0.0

    def test_whitespace(self) -> None:
        assert _parse_brl_value("  ") == 0.0

    def test_no_thousands(self) -> None:
        assert _parse_brl_value("350,75") == 350.75

    def test_large_value(self) -> None:
        assert _parse_brl_value("1.000.000,00") == 1_000_000.0

    def test_invalid_returns_zero(self) -> None:
        assert _parse_brl_value("abc") == 0.0


# ---------------------------------------------------------------------------
# Load
# ---------------------------------------------------------------------------
class TestCpgfLoad:
    def test_load_creates_govcardexpense_nodes(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        node_calls = [
            call for call in run_calls
            if "MERGE (n:GovCardExpense" in str(call)
        ]
        assert len(node_calls) >= 1

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

    def test_load_creates_gastou_cartao_relationships(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        rel_calls = [
            call for call in run_calls
            if "GASTOU_CARTAO" in str(call)
        ]
        assert len(rel_calls) >= 1

    def test_load_skips_when_no_expenses(self) -> None:
        pipeline = _make_pipeline()
        pipeline.expenses = []
        pipeline.cardholders = []
        pipeline.gastou_cartao_rels = []
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        assert session_mock.run.call_count == 0
