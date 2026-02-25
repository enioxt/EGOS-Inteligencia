from __future__ import annotations

import hashlib
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd

from icarus_etl.pipelines.viagens import ViagensPipeline, _make_travel_id, _parse_money

FIXTURES = Path(__file__).parent / "fixtures"


def _make_pipeline() -> ViagensPipeline:
    driver = MagicMock()
    pipeline = ViagensPipeline(driver=driver, data_dir=str(FIXTURES.parent))
    return pipeline


def _load_fixture_data(pipeline: ViagensPipeline) -> None:
    """Load CSV fixture directly into the pipeline's raw DataFrame."""
    pipeline._raw = pd.read_csv(
        FIXTURES / "viagens" / "viagens.csv",
        dtype=str,
        delimiter=";",
        keep_default_na=False,
    )


# ── Metadata ────────────────────────────────────────────────────────


class TestViagensPipelineMetadata:
    def test_name(self) -> None:
        assert ViagensPipeline.name == "viagens"

    def test_source_id(self) -> None:
        assert ViagensPipeline.source_id == "portal_transparencia_viagens"


# ── Extract ─────────────────────────────────────────────────────────


class TestViagensExtract:
    def test_extract_reads_csvs(self, tmp_path: Path) -> None:
        viagens_dir = tmp_path / "viagens"
        viagens_dir.mkdir()
        csv_path = viagens_dir / "test.csv"
        csv_path.write_text(
            "cod_orgao_superior;nome_orgao_superior;cod_orgao;nome_orgao;"
            "cpf;nome;cargo;funcao;descricao_funcao;data_inicio;data_fim;"
            "destinos;motivo;valor_diarias;valor_passagens;valor_outros\n"
            "26000;MIN EDUCACAO;26101;UFRJ;52998224725;Joao da Silva;"
            "PROF;;;01/03/2025;05/03/2025;Brasilia;Reuniao;1200,00;850,50;0,00\n",
            encoding="latin-1",
        )

        pipeline = ViagensPipeline(driver=MagicMock(), data_dir=str(tmp_path))
        pipeline.extract()
        assert len(pipeline._raw) == 1

    def test_extract_raises_if_no_csvs(self, tmp_path: Path) -> None:
        viagens_dir = tmp_path / "viagens"
        viagens_dir.mkdir()

        pipeline = ViagensPipeline(driver=MagicMock(), data_dir=str(tmp_path))
        import pytest

        with pytest.raises(FileNotFoundError):
            pipeline.extract()

    def test_extract_reads_multiple_csvs(self, tmp_path: Path) -> None:
        viagens_dir = tmp_path / "viagens"
        viagens_dir.mkdir()
        header = (
            "cod_orgao_superior;nome_orgao_superior;cod_orgao;nome_orgao;"
            "cpf;nome;cargo;funcao;descricao_funcao;data_inicio;data_fim;"
            "destinos;motivo;valor_diarias;valor_passagens;valor_outros"
        )
        row = (
            "26000;MIN EDUCACAO;26101;UFRJ;52998224725;Joao da Silva;"
            "PROF;;;01/03/2025;05/03/2025;Brasilia;Reuniao;1200,00;850,50;0,00"
        )
        for i in range(3):
            (viagens_dir / f"viagens_20250{i+1}.csv").write_text(
                f"{header}\n{row}\n", encoding="latin-1",
            )

        pipeline = ViagensPipeline(driver=MagicMock(), data_dir=str(tmp_path))
        pipeline.extract()
        assert len(pipeline._raw) == 3


# ── Transform ───────────────────────────────────────────────────────


class TestViagensTransform:
    def test_produces_travel_records(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        # All 5 rows have names, so all produce travel records (masked CPFs kept)
        assert len(pipeline.travels) == 5

    def test_produces_person_rels(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        assert len(pipeline.person_rels) == 3

    def test_normalizes_names(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        names = {t["traveler_name"] for t in pipeline.travels}
        assert "JOAO DA SILVA" in names
        assert "MARIA SOUZA" in names
        assert "PEDRO SANTOS" in names

    def test_formats_cpf(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        cpfs = {t["traveler_cpf"] for t in pipeline.travels}
        assert "529.982.247-25" in cpfs
        assert "111.444.777-35" in cpfs
        assert "987.654.321-00" in cpfs

    def test_invalid_cpf_kept_but_not_linked(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        # Invalid CPF rows are kept as travel records but NOT linked to Person
        names = {t["traveler_name"] for t in pipeline.travels}
        assert "NOME INVALIDO" in names
        # Only 3 valid CPFs get person rels
        assert len(pipeline.person_rels) == 3

    def test_empty_cpf_kept_as_travel(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        names = {t["traveler_name"] for t in pipeline.travels}
        assert "SEM CPF" in names
        rel_names = {r.get("person_name") for r in pipeline.person_rels}
        assert "SEM CPF" not in rel_names

    def test_parses_dates(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        start_dates = {t["start_date"] for t in pipeline.travels}
        assert "2025-03-01" in start_dates
        assert "2025-04-15" in start_dates
        assert "2025-05-10" in start_dates

    def test_end_dates_parsed(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        end_dates = {t["end_date"] for t in pipeline.travels}
        assert "2025-03-05" in end_dates
        assert "2025-04-18" in end_dates

    def test_travel_fields(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        t = pipeline.travels[0]
        assert "travel_id" in t
        assert "traveler_name" in t
        assert "traveler_cpf" in t
        assert "agency" in t
        assert "destination" in t
        assert "start_date" in t
        assert "end_date" in t
        assert "amount" in t
        assert "justification" in t
        assert "source" in t
        assert t["source"] == "portal_transparencia_viagens"

    def test_amount_sums_components(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        # First row: 1200.00 + 850.50 + 0.00 = 2050.50
        joao = [t for t in pipeline.travels if t["traveler_name"] == "JOAO DA SILVA"][0]
        assert joao["amount"] == 2050.50

        # Second row: 900.00 + 1200.00 + 150.00 = 2250.00
        maria = [t for t in pipeline.travels if t["traveler_name"] == "MARIA SOUZA"][0]
        assert maria["amount"] == 2250.00

        # Third row: 1500.00 + 2300.00 + 200.00 = 4000.00
        pedro = [t for t in pipeline.travels if t["traveler_name"] == "PEDRO SANTOS"][0]
        assert pedro["amount"] == 4000.00

    def test_destination_preserved(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        destinations = {t["destination"] for t in pipeline.travels}
        assert "Brasília/DF" in destinations or "Brasilia/DF" in destinations

    def test_justification_preserved(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        justifications = {t["justification"] for t in pipeline.travels}
        assert "Reunião de trabalho" in justifications or "Reuniao de trabalho" in justifications

    def test_agency_preserved(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        agencies = {t["agency"] for t in pipeline.travels}
        assert "UNIVERSIDADE FEDERAL DO RIO DE JANEIRO" in agencies
        assert "RECEITA FEDERAL" in agencies

    def test_limit_respected(self) -> None:
        pipeline = _make_pipeline()
        pipeline.limit = 2
        _load_fixture_data(pipeline)
        pipeline.transform()

        assert len(pipeline.travels) <= 2

    def test_deduplicates_by_travel_id(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()

        ids = [t["travel_id"] for t in pipeline.travels]
        assert len(ids) == len(set(ids))


# ── Travel ID generation ────────────────────────────────────────────


class TestTravelId:
    def test_deterministic(self) -> None:
        id1 = _make_travel_id("529.982.247-25", "Brasilia", "2025-03-01", 2050.50)
        id2 = _make_travel_id("529.982.247-25", "Brasilia", "2025-03-01", 2050.50)
        assert id1 == id2

    def test_different_inputs_differ(self) -> None:
        id1 = _make_travel_id("529.982.247-25", "Brasilia", "2025-03-01", 2050.50)
        id2 = _make_travel_id("529.982.247-25", "Sao Paulo", "2025-03-01", 2050.50)
        assert id1 != id2

    def test_format(self) -> None:
        travel_id = _make_travel_id("529.982.247-25", "Brasilia", "2025-03-01", 2050.50)
        assert len(travel_id) == 16
        # Should be hex characters
        assert all(c in "0123456789abcdef" for c in travel_id)

    def test_hash_matches_manual(self) -> None:
        cpf = "529.982.247-25"
        dest = "Brasilia"
        date = "2025-03-01"
        amount = 2050.50
        raw = f"{cpf}|{dest}|{date}|{amount:.2f}"
        expected = hashlib.sha256(raw.encode()).hexdigest()[:16]
        assert _make_travel_id(cpf, dest, date, amount) == expected


# ── Money parsing ───────────────────────────────────────────────────


class TestParseMoney:
    def test_brazilian_format(self) -> None:
        assert _parse_money("1.200,00") == 1200.00

    def test_decimals(self) -> None:
        assert _parse_money("850,50") == 850.50

    def test_empty_string(self) -> None:
        assert _parse_money("") == 0.0

    def test_zero(self) -> None:
        assert _parse_money("0,00") == 0.0

    def test_large_value(self) -> None:
        assert _parse_money("12.345.678,90") == 12345678.90

    def test_invalid(self) -> None:
        assert _parse_money("abc") == 0.0

    def test_whitespace(self) -> None:
        assert _parse_money("  1.200,00  ") == 1200.00


# ── Load ────────────────────────────────────────────────────────────


class TestViagensLoad:
    def test_load_creates_govtravel_nodes(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        travel_calls = [
            call for call in run_calls if "MERGE (n:GovTravel" in str(call)
        ]
        assert len(travel_calls) >= 1

    def test_load_creates_viajou_relationships(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        rel_calls = [call for call in run_calls if "VIAJOU" in str(call)]
        assert len(rel_calls) >= 1

    def test_load_merges_person_nodes(self) -> None:
        pipeline = _make_pipeline()
        _load_fixture_data(pipeline)
        pipeline.transform()
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        run_calls = session_mock.run.call_args_list

        person_calls = [
            call for call in run_calls if "MERGE (p:Person" in str(call)
        ]
        assert len(person_calls) >= 1

    def test_load_noop_with_empty_data(self) -> None:
        pipeline = _make_pipeline()
        pipeline.travels = []
        pipeline.person_rels = []
        pipeline.load()

        session_mock = pipeline.driver.session.return_value.__enter__.return_value
        assert session_mock.run.call_count == 0
