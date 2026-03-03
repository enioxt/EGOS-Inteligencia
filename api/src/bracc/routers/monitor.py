

import logging
import os
from datetime import UTC, datetime
from typing import Any

import httpx
from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/monitor", tags=["monitor"])

PORTAL_API_KEY = os.environ.get("PORTAL_TRANSPARENCIA_API_KEY", "")
PORTAL_BASE = "https://api.portaldatransparencia.gov.br/api-de-dados"
PORTAL_HEADERS = {"Accept": "application/json", "chave-api-dados": PORTAL_API_KEY}


@router.get("/sanctions/recent")
async def recent_sanctions() -> dict[str, Any]:
    """Get most recent sanctions (CEIS + CNEP) for monitoring."""
    results: list[dict[str, Any]] = []
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            for endpoint, label in [("ceis", "CEIS"), ("cnep", "CNEP")]:
                resp = await client.get(
                    f"{PORTAL_BASE}/{endpoint}",
                    params={"pagina": "1"},
                    headers=PORTAL_HEADERS,
                )
                if resp.status_code == 200:
                    for s in resp.json()[:10]:
                        san = s.get("sancionado", {})
                        results.append({
                            "cadastro": label,
                            "nome": san.get("nome", ""),
                            "cnpj_cpf": san.get("cnpjCpf", ""),
                            "orgao": s.get("orgaoSancionador", {}).get("nome", "") if isinstance(s.get("orgaoSancionador"), dict) else "",
                            "tipo": s.get("tipoSancao", {}).get("descricaoResumida", "") if isinstance(s.get("tipoSancao"), dict) else "",
                            "data_inicio": s.get("dataInicioSancao", ""),
                        })
    except Exception as e:
        logger.warning("Sanctions monitor failed: %s", e)

    return {"sanctions": results, "total": len(results), "checked_at": datetime.now(UTC).isoformat()}


@router.get("/report/{municipio}")
async def municipality_report(municipio: str) -> dict[str, Any]:
    """Auto-generate investigation report for a municipality."""
    report: dict[str, Any] = {
        "municipio": municipio,
        "generated_at": datetime.now(UTC).isoformat(),
        "sections": {},
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. Emendas
            try:
                resp = await client.get(
                    "https://api.transferegov.sistema.gov.br/siconv/v1/proposta/consultar",
                    params={"nome_proponente": municipio, "pagina": "1", "quantidade": "10"},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    report["sections"]["emendas_transferencias"] = {
                        "total": len(data) if isinstance(data, list) else 0,
                        "amostra": data[:5] if isinstance(data, list) else [],
                    }
            except Exception:
                pass

            # 2. Gazette (Querido Diário)
            try:
                resp = await client.get(
                    "https://queridodiario.ok.org.br/api/gazettes",
                    params={"querystring": municipio, "size": "5", "sort_by": "descending_date"},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    gazettes = data.get("gazettes", [])
                    report["sections"]["diarios_oficiais"] = {
                        "total": data.get("total_gazettes", 0),
                        "recentes": [{"data": g.get("date"), "excerto": g.get("excerpts", [""])[0][:200]} for g in gazettes[:5]],
                    }
            except Exception:
                pass

            # 3. CEIS sanctions
            if PORTAL_API_KEY:
                try:
                    resp = await client.get(
                        f"{PORTAL_BASE}/ceis",
                        params={"nomeSancionado": municipio, "pagina": "1"},
                        headers=PORTAL_HEADERS,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        report["sections"]["sancoes"] = {
                            "total": len(data) if isinstance(data, list) else 0,
                            "empresas": [s.get("sancionado", {}).get("nome", "") for s in (data[:5] if isinstance(data, list) else [])],
                        }
                except Exception:
                    pass

    except Exception as e:
        report["error"] = str(e)

    return report
