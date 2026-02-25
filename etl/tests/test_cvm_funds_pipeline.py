from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest

from icarus_etl.pipelines.cvm_funds import CvmFundsPipeline

FIXTURES = Path(__file__).parent / "fixtures"


def _make_pipeline(*, limit: int | None = None) -> CvmFundsPipeline:
    driver = MagicMock()
    return CvmFundsPipeline(driver=driver, data_dir=str(FIXTURES.parent), limit=limit)


def _load_fixture(pipeline: CvmFundsPipeline) -> None:
    """Load CSV fixture directly into the pipeline's raw DataFrame."""
    pipeline._raw = pd.read_csv(
        FIXTURES / "cvm_funds" / "cad_fi.csv",
        sep=";",
        dtype=str,
        keep_default_na=False,
        encoding="utf-8",
    )


class TestCvmFundsPipelineMetadata:
    def test_name(self) -> None:
        assert CvmFundsPipeline.name == "cvm_funds"

    def test_source_id(self) -> None:
        assert CvmFundsPipeline.source_id == "cvm_funds"


class TestCvmFundsExtract:
    def test_extract_reads_csv(self) -> None:
        pipeline = _make_pipeline()
        # Point data_dir to fixtures so extract finds cvm_funds/cad_fi.csv
        pipeline.data_dir = str(FIXTURES)
        pipeline.extract()

        assert not pipeline._raw.empty
        assert "CNPJ_FUNDO" in pipeline._raw.columns
        assert "DENOM_SOCIAL" in pipeline._raw.columns

    def test_extract_raises_on_missing_file(self) -> None:
        pipeline = _make_pipeline()
        pipeline.data_dir = "/nonexistent/path"

        with pytest.raises(FileNotFoundError):
            pipeline.extract()


class TestCvmFundsTransform:
    def test_keeps_all_fund_statuses(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()

        # All 5 rows kept — historical data valuable for connection analysis
        assert len(pipeline.funds) == 5

    def test_formats_fund_cnpj(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()

        cnpjs = {f["fund_cnpj"] for f in pipeline.funds}
        # Check formatted CNPJ pattern (XX.XXX.XXX/XXXX-XX)
        for cnpj in cnpjs:
            assert "/" in cnpj
            assert "-" in cnpj

    def test_normalizes_fund_names(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()

        names = {f["fund_name"] for f in pipeline.funds}
        # normalize_name uppercases and strips accents
        assert "FUNDO DE INVESTIMENTO ALFA" in names
        assert "FUNDO MULTIMERCADO GAMA FI" in names

    def test_fund_fields_present(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()

        fund = pipeline.funds[0]
        expected_fields = {
            "fund_cnpj", "fund_name", "fund_type", "administrator_cnpj",
            "administrator_name", "manager_cnpj", "manager_name", "status", "source",
        }
        assert expected_fields.issubset(fund.keys())
        assert fund["source"] == "cvm_funds"

    def test_fund_type_preserved(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()

        types = {f["fund_type"] for f in pipeline.funds}
        assert "Fundo de Renda Fixa" in types
        assert "Fundo Multimercado" in types

    def test_admin_cnpj_formatted(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()

        admin_cnpjs = {f["administrator_cnpj"] for f in pipeline.funds if f["administrator_cnpj"]}
        # All should be formatted
        for cnpj in admin_cnpjs:
            assert "/" in cnpj

    def test_manager_cnpj_only_for_pj(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()

        # All fixture rows have PF_PJ_GESTOR=PJ, so all should have manager_cnpj
        for fund in pipeline.funds:
            assert fund["manager_cnpj"], f"Expected manager_cnpj for {fund['fund_name']}"

    def test_admin_rels_created(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()

        # All 5 funds have admin CNPJs (some share admins, deduped by pair)
        assert len(pipeline.admin_rels) >= 3

    def test_manager_rels_created(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()

        # All 5 funds, all PJ managers (some share managers, deduped by pair)
        assert len(pipeline.manager_rels) >= 3

    def test_admin_rel_fields(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()

        rel = pipeline.admin_rels[0]
        assert "source_key" in rel
        assert "target_key" in rel
        assert "admin_name" in rel
        assert "/" in rel["source_key"]  # formatted CNPJ

    def test_manager_rel_fields(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()

        rel = pipeline.manager_rels[0]
        assert "source_key" in rel
        assert "target_key" in rel
        assert "manager_name" in rel

    def test_cancelled_fund_included(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()

        cnpjs = {f["fund_cnpj"] for f in pipeline.funds}
        # All funds kept, including cancelled — status stored on node
        assert "05.555.123/0001-77" in cnpjs

    def test_limit_truncates(self) -> None:
        pipeline = _make_pipeline(limit=2)
        _load_fixture(pipeline)
        pipeline.transform()

        assert len(pipeline.funds) <= 2

    def test_deduplicates_funds(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        # Add duplicate row
        pipeline._raw = pd.concat(
            [pipeline._raw, pipeline._raw.iloc[:1]],
            ignore_index=True,
        )
        pipeline.transform()

        cnpjs = [f["fund_cnpj"] for f in pipeline.funds]
        assert len(cnpjs) == len(set(cnpjs))

    def test_skips_invalid_cnpj(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        # Add row with invalid CNPJ (too short)
        bad_row = pd.DataFrame([{
            "CNPJ_FUNDO": "123",
            "DENOM_SOCIAL": "BAD FUND",
            "SIT": "EM FUNCIONAMENTO NORMAL",
            "CLASSE": "Test",
            "CNPJ_ADMIN": "33.000.167/0001-01",
            "ADMIN": "ADMIN",
            "PF_PJ_GESTOR": "PJ",
            "CPF_CNPJ_GESTOR": "02.332.886/0001-04",
            "GESTOR": "GESTOR",
        }])
        pipeline._raw = pd.concat(
            [pipeline._raw, bad_row], ignore_index=True,
        )
        pipeline.transform()

        # Still only 5 valid funds (bad CNPJ row excluded)
        assert len(pipeline.funds) == 5

    def test_deduplicates_admin_rels(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        # Duplicate the whole dataframe to create duplicate rels
        pipeline._raw = pd.concat(
            [pipeline._raw, pipeline._raw],
            ignore_index=True,
        )
        pipeline.transform()

        # Should be deduplicated by (source_key, target_key) pair
        pairs = [(r["source_key"], r["target_key"]) for r in pipeline.admin_rels]
        assert len(pairs) == len(set(pairs))


class TestCvmFundsLoad:
    def test_loads_fund_nodes(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        fund_calls = [c for c in run_calls if "MERGE (n:Fund" in str(c)]
        assert len(fund_calls) >= 1

    def test_creates_administra_relationships(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        rel_calls = [c for c in run_calls if "ADMINISTRA" in str(c)]
        assert len(rel_calls) >= 1

    def test_creates_gere_relationships(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        rel_calls = [c for c in run_calls if "GERE" in str(c)]
        assert len(rel_calls) >= 1

    def test_administra_query_merges_company(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        admin_calls = [c for c in run_calls if "ADMINISTRA" in str(c)]
        for call in admin_calls:
            query = str(call[0][0])
            assert "MERGE (c:Company" in query
            assert "row.source_key" in query

    def test_gere_query_merges_company(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        gere_calls = [c for c in run_calls if "GERE" in str(c)]
        for call in gere_calls:
            query = str(call[0][0])
            assert "MERGE (c:Company" in query

    def test_empty_funds_skips_load(self) -> None:
        pipeline = _make_pipeline()
        pipeline.funds = []
        pipeline.admin_rels = []
        pipeline.manager_rels = []
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        assert session_mock.run.call_count == 0

    def test_company_on_create_sets_name(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        admin_calls = [c for c in run_calls if "ADMINISTRA" in str(c)]
        for call in admin_calls:
            query = str(call[0][0])
            assert "ON CREATE SET" in query
            assert "razao_social" in query
