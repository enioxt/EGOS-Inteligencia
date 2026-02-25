from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd

from icarus_etl.pipelines.eu_sanctions import (
    VALID_EU_TYPES,
    EuSanctionsPipeline,
    _clean_entity_type,
    _generate_sanction_id,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _make_pipeline() -> EuSanctionsPipeline:
    driver = MagicMock()
    return EuSanctionsPipeline(driver, data_dir=str(FIXTURES))


def _extract_and_transform(pipeline: EuSanctionsPipeline) -> None:
    pipeline.extract()
    pipeline.transform()


# --- Pipeline metadata ---


def test_pipeline_name() -> None:
    pipeline = _make_pipeline()
    assert pipeline.name == "eu_sanctions"


def test_pipeline_source_id() -> None:
    pipeline = _make_pipeline()
    assert pipeline.source_id == "eu_sanctions"


# --- Generate sanction ID ---


def test_generate_sanction_id_deterministic() -> None:
    id1 = _generate_sanction_id("Sergei IVANOV", "RUSSIA", "EU.1.01")
    id2 = _generate_sanction_id("Sergei IVANOV", "RUSSIA", "EU.1.01")
    assert id1 == id2


def test_generate_sanction_id_different_inputs() -> None:
    id1 = _generate_sanction_id("Sergei IVANOV", "RUSSIA", "EU.1.01")
    id2 = _generate_sanction_id("Ali HASSAN", "SYRIA", "EU.3.03")
    assert id1 != id2


def test_generate_sanction_id_length() -> None:
    sid = _generate_sanction_id("Sergei IVANOV", "RUSSIA", "EU.1.01")
    assert len(sid) == 16


# --- Clean entity type ---


def test_clean_entity_type_person() -> None:
    assert _clean_entity_type("person") == "person"


def test_clean_entity_type_enterprise() -> None:
    assert _clean_entity_type("enterprise") == "enterprise"


def test_clean_entity_type_whitespace() -> None:
    assert _clean_entity_type("  person  ") == "person"


# --- Extract ---


def test_extract_reads_csv() -> None:
    pipeline = _make_pipeline()
    pipeline.extract()
    assert len(pipeline._raw) == 5


def test_extract_has_expected_columns() -> None:
    pipeline = _make_pipeline()
    pipeline.extract()
    assert "Entity_LogicalId" in pipeline._raw.columns
    assert "NameAlias_WholeName" in pipeline._raw.columns
    assert "Entity_SubjectType" in pipeline._raw.columns
    assert "Regulation_Programme" in pipeline._raw.columns


def test_extract_missing_file_no_error() -> None:
    driver = MagicMock()
    pipeline = EuSanctionsPipeline(driver, data_dir="/nonexistent")
    pipeline.extract()
    assert len(pipeline._raw) == 0


def test_extract_respects_limit() -> None:
    driver = MagicMock()
    pipeline = EuSanctionsPipeline(driver, data_dir=str(FIXTURES), limit=2)
    pipeline.extract()
    assert len(pipeline._raw) == 2


# --- Transform ---


def test_transform_produces_sanctions() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    # 5 rows: 2 persons, 2 enterprises, 1 person with empty name (skipped)
    assert len(pipeline.sanctions) == 4


def test_transform_skips_empty_name() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    names = {s["original_name"] for s in pipeline.sanctions}
    assert "" not in names


def test_transform_normalizes_name() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    sanction = next(
        s for s in pipeline.sanctions if s["original_name"] == "Sergei IVANOV"
    )
    assert sanction["name"] == "SERGEI IVANOV"


def test_transform_preserves_fields() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    sanction = next(
        s for s in pipeline.sanctions if s["original_name"] == "Sergei IVANOV"
    )
    assert sanction["entity_type"] == "person"
    assert sanction["program"] == "RUSSIA"
    assert sanction["regulation"] == "EU.1.01"
    assert sanction["listed_date"] == "2022-03-01"
    assert sanction["source"] == "eu_sanctions"
    assert sanction["source_list"] == "EU"


def test_transform_enterprise_type() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    sanction = next(
        s for s in pipeline.sanctions if s["original_name"] == "PETROCHEM TRADING LLC"
    )
    assert sanction["entity_type"] == "enterprise"


def test_transform_sanction_id_is_16_char_hash() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    for s in pipeline.sanctions:
        assert len(s["sanction_id"]) == 16


def test_transform_builds_person_rels() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    # 2 persons with valid names: Sergei IVANOV, Ali HASSAN
    assert len(pipeline.person_rels) == 2


def test_transform_builds_company_rels() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    # 2 enterprises: PETROCHEM TRADING LLC, GOLDEN EXPORT LTD
    assert len(pipeline.company_rels) == 2


def test_transform_rel_fields() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    rel = pipeline.person_rels[0]
    assert "sanction_id" in rel
    assert "name" in rel
    assert len(rel["sanction_id"]) == 16


# --- Deduplication ---


def test_transform_deduplicates() -> None:
    pipeline = _make_pipeline()
    pipeline.extract()
    # Inject duplicate row
    dup = pipeline._raw.iloc[0:1].copy()
    pipeline._raw = pd.concat([pipeline._raw, dup], ignore_index=True)
    pipeline.transform()
    ids = [s["sanction_id"] for s in pipeline.sanctions]
    # Same name+program+regulation produces same ID, dedup removes it
    assert len(ids) == len(set(ids))


# --- Load ---


def test_load_creates_sanction_nodes() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    pipeline.load()

    session = pipeline.driver.session.return_value.__enter__.return_value
    run_calls = session.run.call_args_list
    sanction_calls = [
        call for call in run_calls if "MERGE (n:InternationalSanction" in str(call)
    ]
    assert len(sanction_calls) >= 1


def test_load_creates_person_rels() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    pipeline.load()

    session = pipeline.driver.session.return_value.__enter__.return_value
    run_calls = session.run.call_args_list
    rel_calls = [
        call for call in run_calls
        if "SANCIONADA_INTERNACIONALMENTE" in str(call)
        and "Person" in str(call)
    ]
    assert len(rel_calls) >= 1


def test_load_creates_company_rels() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    pipeline.load()

    session = pipeline.driver.session.return_value.__enter__.return_value
    run_calls = session.run.call_args_list
    rel_calls = [
        call for call in run_calls
        if "SANCIONADA_INTERNACIONALMENTE" in str(call)
        and "Company" in str(call)
    ]
    assert len(rel_calls) >= 1


def test_load_empty_pipeline_no_calls() -> None:
    pipeline = _make_pipeline()
    pipeline.sanctions = []
    pipeline.person_rels = []
    pipeline.company_rels = []
    pipeline.load()

    session = pipeline.driver.session.return_value.__enter__.return_value
    assert session.run.call_count == 0


# --- Constants ---


def test_valid_eu_types() -> None:
    assert "person" in VALID_EU_TYPES
    assert "enterprise" in VALID_EU_TYPES
    assert "vessel" not in VALID_EU_TYPES
