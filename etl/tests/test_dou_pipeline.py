"""Tests for DOU (Diario Oficial da Uniao) pipeline.

Tests extraction from Imprensa Nacional JSON format, BigQuery parquet format,
act-type classification, CPF/CNPJ extraction from text, and Neo4j load operations.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest

from icarus_etl.pipelines.dou import (
    DouPipeline,
    _classify_act,
    _extract_cnpjs,
    _extract_cpfs,
    _make_act_id,
)

try:
    import pyarrow  # noqa: F401

    _HAS_PYARROW = True
except ImportError:
    _HAS_PYARROW = False

FIXTURES = Path(__file__).parent / "fixtures"


def _make_pipeline(data_dir: str | None = None) -> DouPipeline:
    driver = MagicMock()
    return DouPipeline(driver, data_dir=data_dir or str(FIXTURES))


# -- Metadata --


class TestMetadata:
    def test_name(self) -> None:
        assert DouPipeline.name == "dou"

    def test_source_id(self) -> None:
        assert DouPipeline.source_id == "imprensa_nacional"


# -- Extract --


class TestExtract:
    def test_raises_when_dir_missing(self) -> None:
        pipeline = _make_pipeline(data_dir="/nonexistent/path")
        try:
            pipeline.extract()
            raise AssertionError("Expected FileNotFoundError")
        except FileNotFoundError:
            pass

    def test_reads_json_fixture(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        assert len(pipeline._raw_acts) == 5

    def test_parses_act_fields(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        first = pipeline._raw_acts[0]
        assert first["urlTitle"] == "decreto-de-15-de-janeiro-de-2024-nomeacao-12345"
        assert first["title"] == "DECRETO DE 15 DE JANEIRO DE 2024"
        assert first["pubDate"] == "2024-01-15"
        assert first["pubName"] == "DO1"
        assert first["artCategory"] == "Atos do Poder Executivo"
        assert "529.982.247-25" in first["abstract"]

    def test_json_array_wrapper_format(self, tmp_path: Path) -> None:
        """JSON with 'jsonArray' wrapper (IN API format) should parse correctly."""
        dou_dir = tmp_path / "dou"
        dou_dir.mkdir()
        data = {
            "jsonArray": [
                {
                    "urlTitle": "test-act-wrapper",
                    "title": "TEST ACT",
                    "abstract": "Test abstract",
                    "pubDate": "2024-05-01",
                    "pubName": "DO1",
                    "artCategory": "Test",
                    "hierarchyStr": "Test Agency",
                }
            ]
        }
        (dou_dir / "test.json").write_text(json.dumps(data))

        pipeline = _make_pipeline(data_dir=str(tmp_path))
        pipeline.extract()
        assert len(pipeline._raw_acts) == 1
        assert pipeline._raw_acts[0]["urlTitle"] == "test-act-wrapper"

    def test_respects_limit(self) -> None:
        driver = MagicMock()
        pipeline = DouPipeline(driver, data_dir=str(FIXTURES), limit=2)
        pipeline.extract()
        assert len(pipeline._raw_acts) == 2

    def test_no_json_files_warns(self, tmp_path: Path) -> None:
        """When no JSON files exist, extract should warn and leave _raw_acts empty."""
        dou_dir = tmp_path / "dou"
        dou_dir.mkdir()

        pipeline = _make_pipeline(data_dir=str(tmp_path))
        pipeline.extract()
        assert len(pipeline._raw_acts) == 0

    @pytest.mark.skipif(not _HAS_PYARROW, reason="pyarrow not installed")
    def test_reads_parquet_from_bigquery(self, tmp_path: Path) -> None:
        """Parquet files from BigQuery should be extracted correctly."""
        dou_dir = tmp_path / "dou" / "bigquery"
        dou_dir.mkdir(parents=True)

        df = pd.DataFrame([
            {
                "titulo": "PORTARIA N 123",
                "orgao": "Ministerio da Economia",
                "ementa": "Nomear FULANO, CPF 529.982.247-25",
                "excerto": "para o cargo de Diretor",
                "secao": "1",
                "data_publicacao": "2024-03-15",
                "url": "https://www.in.gov.br/web/dou/-/portaria-n-123-456",
                "tipo_edicao": "Normal",
            },
            {
                "titulo": "EXTRATO DE CONTRATO",
                "orgao": "Ministerio da Saude",
                "ementa": "Contratada: XYZ LTDA, CNPJ 11.222.333/0001-81",
                "excerto": "",
                "secao": "3",
                "data_publicacao": "2024-03-16",
                "url": "https://www.in.gov.br/web/dou/-/extrato-de-contrato-789",
                "tipo_edicao": "Normal",
            },
        ])
        df.to_parquet(dou_dir / "secao_1.parquet", index=False)

        pipeline = _make_pipeline(data_dir=str(tmp_path))
        pipeline.extract()
        assert len(pipeline._raw_acts) == 2
        assert pipeline._raw_acts[0]["title"] == "PORTARIA N 123"
        assert pipeline._raw_acts[0]["pubDate"] == "2024-03-15"
        assert pipeline._raw_acts[0]["pubName"] == "DO1"
        assert "529.982.247-25" in pipeline._raw_acts[0]["abstract"]

    @pytest.mark.skipif(not _HAS_PYARROW, reason="pyarrow not installed")
    def test_parquet_transform_extracts_documents(self, tmp_path: Path) -> None:
        """Parquet data should be transformed with CPF/CNPJ extraction."""
        dou_dir = tmp_path / "dou" / "bigquery"
        dou_dir.mkdir(parents=True)

        df = pd.DataFrame([{
            "titulo": "PORTARIA DE NOMEACAO",
            "orgao": "Test",
            "ementa": "Nomear FULANO CPF 529.982.247-25",
            "excerto": "para cargo",
            "secao": "1",
            "data_publicacao": "2024-01-01",
            "url": "https://www.in.gov.br/web/dou/-/test-act-123",
            "tipo_edicao": "Normal",
        }])
        df.to_parquet(dou_dir / "test.parquet", index=False)

        pipeline = _make_pipeline(data_dir=str(tmp_path))
        pipeline.extract()
        pipeline.transform()
        assert len(pipeline.acts) == 1
        assert pipeline.acts[0]["act_type"] == "nomeacao"
        assert len(pipeline.person_rels) == 1
        assert pipeline.person_rels[0]["source_key"] == "529.982.247-25"


# -- Classification --


class TestClassification:
    def test_nomeacao(self) -> None:
        assert _classify_act("DECRETO DE NOMEACAO", "NOMEAR fulano") == "nomeacao"

    def test_exoneracao(self) -> None:
        assert _classify_act("PORTARIA", "EXONERAR fulano do cargo") == "exoneracao"

    def test_contrato(self) -> None:
        assert _classify_act("EXTRATO DE CONTRATO", "Contratada: XYZ LTDA") == "contrato"

    def test_penalidade(self) -> None:
        assert _classify_act("AVISO DE PENALIDADE", "suspensao temporaria") == "penalidade"

    def test_outro(self) -> None:
        assert _classify_act("PORTARIA", "Regimento interno aprovado") == "outro"

    def test_title_priority(self) -> None:
        """Classification should work when keyword is only in title."""
        assert _classify_act("CONTRATO No 42", "Objeto: servicos") == "contrato"

    def test_abstract_priority(self) -> None:
        """Classification should work when keyword is only in abstract."""
        assert _classify_act("PORTARIA", "nomear fulano para o cargo") == "nomeacao"


# -- CPF extraction --


class TestCpfExtraction:
    def test_extracts_formatted_cpf(self) -> None:
        text = "NOMEAR FULANO, CPF 529.982.247-25, para o cargo"
        result = _extract_cpfs(text)
        assert result == ["529.982.247-25"]

    def test_multiple_cpfs(self) -> None:
        text = "CPF 529.982.247-25 e CPF 111.444.777-35 nomeados"
        result = _extract_cpfs(text)
        assert len(result) == 2
        assert "529.982.247-25" in result
        assert "111.444.777-35" in result

    def test_no_cpf_returns_empty(self) -> None:
        text = "Nenhum CPF neste texto"
        result = _extract_cpfs(text)
        assert result == []


# -- CNPJ extraction --


class TestCnpjExtraction:
    def test_extracts_formatted_cnpj(self) -> None:
        text = "Empresa CNPJ 11.222.333/0001-81 contratada"
        result = _extract_cnpjs(text)
        assert result == ["11.222.333/0001-81"]

    def test_extracts_raw_cnpj(self) -> None:
        text = "Empresa com CNPJ 44555666000199 contratada"
        result = _extract_cnpjs(text)
        assert len(result) == 1
        assert result[0] == "44.555.666/0001-99"

    def test_multiple_cnpjs(self) -> None:
        text = "CNPJ 11.222.333/0001-81 e CNPJ 99.888.777/0001-66"
        result = _extract_cnpjs(text)
        assert len(result) == 2

    def test_no_cnpj_returns_empty(self) -> None:
        text = "Texto sem nenhum CNPJ"
        result = _extract_cnpjs(text)
        assert result == []

    def test_deduplicates_formatted_and_raw(self) -> None:
        """Same CNPJ appearing as formatted and raw should only appear once."""
        text = "CNPJ 11.222.333/0001-81 (11222333000181)"
        result = _extract_cnpjs(text)
        assert len(result) == 1


# -- Act ID --


class TestActId:
    def test_deterministic(self) -> None:
        id1 = _make_act_id("test-act", "2024-01-15")
        id2 = _make_act_id("test-act", "2024-01-15")
        assert id1 == id2

    def test_different_inputs_different_ids(self) -> None:
        id1 = _make_act_id("act-a", "2024-01-15")
        id2 = _make_act_id("act-b", "2024-01-15")
        assert id1 != id2

    def test_length(self) -> None:
        act_id = _make_act_id("test", "2024-01-01")
        assert len(act_id) == 16


# -- Transform --


class TestTransform:
    def test_produces_acts(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        assert len(pipeline.acts) == 5

    def test_act_fields(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()

        act = pipeline.acts[0]
        assert "act_id" in act
        assert act["title"] == "DECRETO DE 15 DE JANEIRO DE 2024"
        assert act["act_type"] == "nomeacao"
        assert act["date"] == "2024-01-15"
        assert act["section"] == "secao_1"
        assert act["agency"] == "Presidencia da Republica/Secretaria-Geral"
        assert act["source"] == "imprensa_nacional"
        assert act["url"].startswith("https://www.in.gov.br/web/dou/-/")

    def test_classifies_nomeacao(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()

        types = {a["act_type"] for a in pipeline.acts}
        assert "nomeacao" in types

    def test_classifies_exoneracao(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()

        exoneracoes = [a for a in pipeline.acts if a["act_type"] == "exoneracao"]
        assert len(exoneracoes) == 1

    def test_classifies_contrato(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()

        contratos = [a for a in pipeline.acts if a["act_type"] == "contrato"]
        assert len(contratos) == 1

    def test_classifies_penalidade(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()

        penalidades = [a for a in pipeline.acts if a["act_type"] == "penalidade"]
        assert len(penalidades) == 1

    def test_classifies_outro(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()

        outros = [a for a in pipeline.acts if a["act_type"] == "outro"]
        assert len(outros) == 1

    def test_extracts_cpfs_as_person_rels(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()

        # Fixture has 2 acts with CPFs (nomeacao + exoneracao)
        assert len(pipeline.person_rels) == 2
        cpfs = {r["source_key"] for r in pipeline.person_rels}
        assert "529.982.247-25" in cpfs
        assert "111.444.777-35" in cpfs

    def test_extracts_cnpjs_as_company_rels(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()

        # Fixture has 2 acts with CNPJs (contrato + penalidade)
        assert len(pipeline.company_rels) == 2
        cnpjs = {r["source_key"] for r in pipeline.company_rels}
        assert "11.222.333/0001-81" in cnpjs
        assert "99.888.777/0001-66" in cnpjs

    def test_skips_acts_without_url_title(self, tmp_path: Path) -> None:
        dou_dir = tmp_path / "dou"
        dou_dir.mkdir()
        data = [
            {
                "urlTitle": "",
                "title": "Bad Act",
                "abstract": "No URL title",
                "pubDate": "2024-01-01",
                "pubName": "DO1",
                "artCategory": "Test",
                "hierarchyStr": "Test",
            }
        ]
        (dou_dir / "test.json").write_text(json.dumps(data))

        pipeline = _make_pipeline(data_dir=str(tmp_path))
        pipeline.extract()
        pipeline.transform()
        assert len(pipeline.acts) == 0

    def test_skips_acts_without_date(self, tmp_path: Path) -> None:
        dou_dir = tmp_path / "dou"
        dou_dir.mkdir()
        data = [
            {
                "urlTitle": "valid-title",
                "title": "No Date Act",
                "abstract": "Missing date",
                "pubDate": "",
                "pubName": "DO1",
                "artCategory": "Test",
                "hierarchyStr": "Test",
            }
        ]
        (dou_dir / "test.json").write_text(json.dumps(data))

        pipeline = _make_pipeline(data_dir=str(tmp_path))
        pipeline.extract()
        pipeline.transform()
        assert len(pipeline.acts) == 0

    def test_text_excerpt_truncated(self, tmp_path: Path) -> None:
        dou_dir = tmp_path / "dou"
        dou_dir.mkdir()
        data = [
            {
                "urlTitle": "long-text-act",
                "title": "Long Act",
                "abstract": "A" * 1000,
                "pubDate": "2024-01-01",
                "pubName": "DO1",
                "artCategory": "Test",
                "hierarchyStr": "Test",
            }
        ]
        (dou_dir / "test.json").write_text(json.dumps(data))

        pipeline = _make_pipeline(data_dir=str(tmp_path))
        pipeline.extract()
        pipeline.transform()
        assert len(pipeline.acts[0]["text_excerpt"]) == 500

    def test_section_mapping(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()

        sections = {a["section"] for a in pipeline.acts}
        assert "secao_1" in sections
        assert "secao_2" in sections
        assert "secao_3" in sections

    def test_act_has_no_entity_links_when_no_documents(self) -> None:
        """The 'outro' fixture act has no CPF/CNPJ and should produce no links."""
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()

        outros = [a for a in pipeline.acts if a["act_type"] == "outro"]
        assert len(outros) == 1
        act_id = outros[0]["act_id"]

        person_targets = {r["target_key"] for r in pipeline.person_rels}
        company_targets = {r["target_key"] for r in pipeline.company_rels}
        assert act_id not in person_targets
        assert act_id not in company_targets


# -- Load --


class TestLoad:
    def test_creates_dou_act_nodes(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        act_calls = [c for c in run_calls if "MERGE (n:DOUAct" in str(c)]
        assert len(act_calls) >= 1

    def test_creates_publicou_relationships(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        rel_calls = [c for c in run_calls if "PUBLICOU" in str(c)]
        assert len(rel_calls) >= 1

    def test_creates_mencionou_relationships(self) -> None:
        pipeline = _make_pipeline()
        pipeline.extract()
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        rel_calls = [c for c in run_calls if "MENCIONOU" in str(c)]
        assert len(rel_calls) >= 1

    def test_no_acts_skips_load(self) -> None:
        pipeline = _make_pipeline()
        pipeline.acts = []
        pipeline.person_rels = []
        pipeline.company_rels = []
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        assert session_mock.run.call_count == 0

    def test_load_without_person_rels(self, tmp_path: Path) -> None:
        """Acts without CPFs should only load nodes and company rels."""
        dou_dir = tmp_path / "dou"
        dou_dir.mkdir()
        data = [
            {
                "urlTitle": "contrato-only",
                "title": "EXTRATO DE CONTRATO",
                "abstract": "Contratada: XYZ, CNPJ 11.222.333/0001-81",
                "pubDate": "2024-01-01",
                "pubName": "DO3",
                "artCategory": "Contratos",
                "hierarchyStr": "Test",
            }
        ]
        (dou_dir / "test.json").write_text(json.dumps(data))

        pipeline = _make_pipeline(data_dir=str(tmp_path))
        pipeline.extract()
        pipeline.transform()

        assert len(pipeline.person_rels) == 0
        assert len(pipeline.company_rels) == 1

        pipeline.load()
        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        publicou_calls = [c for c in run_calls if "PUBLICOU" in str(c)]
        assert len(publicou_calls) == 0


# -- Full pipeline run --


class TestFullRun:
    def test_run_completes(self) -> None:
        """Verify the full extract -> transform -> load pipeline runs without error."""
        pipeline = _make_pipeline()
        pipeline.run()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        assert session_mock.run.call_count >= 1
