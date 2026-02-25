from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from icarus_etl.pipelines.un_sanctions import (
    VALID_ENTITY_TYPES,
    UnSanctionsPipeline,
    _generate_sanction_id,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _make_pipeline() -> UnSanctionsPipeline:
    driver = MagicMock()
    return UnSanctionsPipeline(driver, data_dir=str(FIXTURES))


def _extract_and_transform(pipeline: UnSanctionsPipeline) -> None:
    pipeline.extract()
    pipeline.transform()


# --- Pipeline metadata ---


def test_pipeline_name() -> None:
    pipeline = _make_pipeline()
    assert pipeline.name == "un_sanctions"


def test_pipeline_source_id() -> None:
    pipeline = _make_pipeline()
    assert pipeline.source_id == "un_sanctions"


# --- Generate sanction ID ---


def test_generate_sanction_id_deterministic() -> None:
    id1 = _generate_sanction_id("QDi.001", "SAYF AL-ADL")
    id2 = _generate_sanction_id("QDi.001", "SAYF AL-ADL")
    assert id1 == id2


def test_generate_sanction_id_different_inputs() -> None:
    id1 = _generate_sanction_id("QDi.001", "SAYF AL-ADL")
    id2 = _generate_sanction_id("QDi.002", "AMIN AL-HAQ")
    assert id1 != id2


def test_generate_sanction_id_length() -> None:
    sanction_id = _generate_sanction_id("QDi.001", "SAYF AL-ADL")
    assert len(sanction_id) == 16


# --- Extract ---


def test_extract_reads_json() -> None:
    pipeline = _make_pipeline()
    pipeline.extract()
    assert len(pipeline._raw) == 5


def test_extract_missing_file_no_error() -> None:
    driver = MagicMock()
    pipeline = UnSanctionsPipeline(driver, data_dir="/nonexistent")
    pipeline.extract()
    assert len(pipeline._raw) == 0


def test_extract_respects_limit() -> None:
    driver = MagicMock()
    pipeline = UnSanctionsPipeline(driver, data_dir=str(FIXTURES), limit=2)
    pipeline.extract()
    assert len(pipeline._raw) == 2


# --- Transform ---


def test_transform_filters_valid_entries() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    # 5 entries: 3 individuals with names, 1 entity, 1 individual with empty name (skipped)
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
        s for s in pipeline.sanctions if s["reference_number"] == "QDi.001"
    )
    assert sanction["name"] == "SAYF AL-ADL"


def test_transform_preserves_fields() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    sanction = next(
        s for s in pipeline.sanctions if s["reference_number"] == "QDi.001"
    )
    assert sanction["entity_type"] == "individual"
    assert sanction["listed_date"] == "2001-01-25"
    assert sanction["un_list_type"] == "Al-Qaida"
    assert sanction["nationality"] == "Egypt"
    assert sanction["source"] == "un_sanctions"
    assert sanction["source_list"] == "UN"


def test_transform_entity_type() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    sanction = next(
        s for s in pipeline.sanctions if s["reference_number"] == "QDe.004"
    )
    assert sanction["entity_type"] == "entity"
    assert sanction["name"] == "MAMOUN DARKAZANLI IMPORT-EXPORT COMPANY"


def test_transform_sanction_id_is_hash() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    for sanction in pipeline.sanctions:
        assert len(sanction["sanction_id"]) == 16


def test_transform_aliases_joined() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    sanction = next(
        s for s in pipeline.sanctions if s["reference_number"] == "QDi.001"
    )
    assert "aliases" in sanction
    assert "SAIF AL-ADEL" in sanction["aliases"]
    assert "MUHAMAD IBRAHIM MAKKAWI" in sanction["aliases"]
    assert "|" in sanction["aliases"]


def test_transform_no_aliases_field_when_empty() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    sanction = next(
        s for s in pipeline.sanctions if s["reference_number"] == "QDe.004"
    )
    assert "aliases" not in sanction


def test_transform_builds_person_rels() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    # 3 individuals with names should produce 3 person rels
    assert len(pipeline.person_rels) == 3


def test_transform_builds_company_rels() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    # 1 entity should produce 1 company rel
    assert len(pipeline.company_rels) == 1


def test_transform_person_rel_keys() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    for rel in pipeline.person_rels:
        assert "source_key" in rel  # sanction_id
        assert "target_key" in rel  # normalized name
        assert len(rel["source_key"]) == 16


def test_transform_company_rel_keys() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    for rel in pipeline.company_rels:
        assert "source_key" in rel
        assert "target_key" in rel
        assert len(rel["source_key"]) == 16


# --- Deduplication ---


def test_transform_deduplicates() -> None:
    pipeline = _make_pipeline()
    pipeline.extract()
    # Inject duplicate entry
    pipeline._raw.append(pipeline._raw[0].copy())
    pipeline.transform()
    ids = [s["sanction_id"] for s in pipeline.sanctions]
    first_id = _generate_sanction_id("QDi.001", "SAYF AL-ADL")
    assert ids.count(first_id) == 1


# --- Load ---


def test_load_calls_batch_loader() -> None:
    pipeline = _make_pipeline()
    _extract_and_transform(pipeline)
    pipeline.load()

    driver = pipeline.driver
    session = driver.session.return_value.__enter__.return_value
    assert session.run.call_count >= 1


def test_load_empty_pipeline_no_calls() -> None:
    pipeline = _make_pipeline()
    pipeline.sanctions = []
    pipeline.person_rels = []
    pipeline.company_rels = []
    pipeline.load()

    driver = pipeline.driver
    session = driver.session.return_value.__enter__.return_value
    assert session.run.call_count == 0


# --- Constants ---


def test_valid_entity_types() -> None:
    assert "individual" in VALID_ENTITY_TYPES
    assert "entity" in VALID_ENTITY_TYPES
    assert "vessel" not in VALID_ENTITY_TYPES
