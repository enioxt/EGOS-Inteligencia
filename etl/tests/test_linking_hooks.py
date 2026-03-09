from pathlib import Path
from unittest.mock import MagicMock

from bracc_etl.linking_hooks import _run_script, run_post_load_hooks


def test_run_script_passes_query_params(tmp_path: Path) -> None:
    script_path = tmp_path / "hook.cypher"
    script_path.write_text("RETURN $run_id AS run_id;", encoding="utf-8")

    driver = MagicMock()
    session = MagicMock()
    driver.session.return_value.__enter__.return_value = session

    _run_script(
        driver=driver,
        neo4j_database="neo4j",
        script_path=script_path,
        params={"run_id": "test_run"},
    )

    session.run.assert_called_once_with("RETURN $run_id AS run_id", {"run_id": "test_run"})


def test_run_post_load_hooks_for_cnpj_forwards_run_id(monkeypatch) -> None:
    calls: list[tuple[Path, dict[str, str] | None]] = []

    def fake_run_script(
        driver: MagicMock,
        neo4j_database: str,
        script_path: Path,
        params: dict[str, str] | None = None,
    ) -> None:
        calls.append((script_path, params))

    monkeypatch.setattr("bracc_etl.linking_hooks._run_script", fake_run_script)

    run_post_load_hooks(
        driver=MagicMock(),
        source="cnpj",
        neo4j_database="neo4j",
        linking_tier="full",
        run_id="cnpj_20260306160000",
    )

    assert [path.name for path, _ in calls] == [
        "link_partners_probable.cypher",
        "link_persons.cypher",
    ]
    assert all(params == {"run_id": "cnpj_20260306160000"} for _, params in calls)
