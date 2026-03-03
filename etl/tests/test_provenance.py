from datetime import datetime

from bracc_etl.provenance import build_audit_fields, raw_row_hash


def test_raw_row_hash_is_stable_for_key_order() -> None:
    row_a = {"b": 2, "a": "x"}
    row_b = {"a": "x", "b": 2}
    assert raw_row_hash(row_a) == raw_row_hash(row_b)


def test_build_audit_fields_contains_expected_metadata() -> None:
    fields = build_audit_fields(
        raw_row={"id": 10, "name": "Empresa X"},
        source_url="https://dados.exemplo.gov.br/arquivo.csv",
        method="api",
        collected_at="2026-03-03T10:00:00Z",
    )

    assert fields["audit_status"] == "verified"
    assert fields["source_url"] == "https://dados.exemplo.gov.br/arquivo.csv"
    assert fields["source_method"] == "api"
    assert fields["verified_at"] == "2026-03-03T10:00:00Z"
    assert len(fields["raw_line_hash"]) == 64
    assert len(fields["source_fingerprint"]) == 64


def test_build_audit_fields_uses_current_time_when_missing_collected_at() -> None:
    fields = build_audit_fields(
        raw_row={"x": 1},
        source_url="https://x",
        method="bulk_download",
    )
    datetime.fromisoformat(fields["verified_at"].replace("Z", "+00:00"))
