"""Transparency & web search tools for the EGOS Inteligência chatbot.

Tools:
- web_search: DuckDuckGo HTML search (no API key needed)
- search_emendas: Portal da Transparência emendas by city/state
- search_transferencias: Federal transfers to municipalities
- search_ceap: CEAP parliamentary expenses
- search_pep_city: Politically exposed persons by city
"""

import logging
import re
from typing import Any
from urllib.parse import quote_plus

import httpx

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/json",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}

# Portal da Transparência base (public, no key needed for HTML scraping)
_PT_BASE = "https://api.portaldatransparencia.gov.br/api-de-dados"
# TransfereGov API
_TG_BASE = "https://api.transferegov.gestao.gov.br"


async def tool_web_search(query: str, max_results: int = 5) -> list[dict[str, str]]:
    """Search the web using DuckDuckGo HTML (no API key).
    Returns list of {title, url, snippet}."""
    results: list[dict[str, str]] = []
    url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=_HEADERS)
            html = resp.text

        # Parse results from DDG HTML
        # Each result is in <div class="result__body">
        snippets = re.findall(
            r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.+?)</a>.*?'
            r'<a[^>]+class="result__snippet"[^>]*>(.+?)</a>',
            html, re.DOTALL
        )
        for href, title, snippet in snippets[:max_results]:
            # DDG redirects through //duckduckgo.com/l/?uddg=...
            actual_url = href
            if "uddg=" in href:
                m = re.search(r"uddg=([^&]+)", href)
                if m:
                    from urllib.parse import unquote
                    actual_url = unquote(m.group(1))
            results.append({
                "title": re.sub(r"<[^>]+>", "", title).strip(),
                "url": actual_url,
                "snippet": re.sub(r"<[^>]+>", "", snippet).strip()[:300],
            })
    except Exception as e:
        logger.warning("Web search failed: %s", e)
        results.append({"title": "Erro na busca", "url": "", "snippet": str(e)[:200]})

    return results


async def tool_search_emendas(municipio: str, uf: str = "", ano: int = 2024) -> dict[str, Any]:
    """Search parliamentary amendments (emendas) for a municipality.
    Uses Portal da Transparência web scraping."""
    query = f"emendas parlamentares {municipio} {uf} {ano} site:portaldatransparencia.gov.br"
    web_results = await tool_web_search(query, max_results=3)

    # Also search for actual data via TransfereGov if possible
    tg_results: list[dict[str, Any]] = []
    try:
        search_url = f"https://api.transferegov.gestao.gov.br/transferenciasespeciais/transferencia?nome_municipio=ilike.*{quote_plus(municipio)}*&limit=10"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(search_url, headers={"Accept": "application/json"})
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    for item in data[:10]:
                        tg_results.append({
                            "parlamentar": item.get("nome_parlamentar", ""),
                            "valor": item.get("valor_transferencia", 0),
                            "municipio": item.get("nome_municipio", ""),
                            "uf": item.get("sigla_uf", ""),
                            "objeto": item.get("objeto", "")[:200],
                            "ano": item.get("ano_emenda", ""),
                        })
    except Exception as e:
        logger.warning("TransfereGov API failed: %s", e)

    return {
        "municipio": municipio,
        "uf": uf,
        "ano": ano,
        "transferegov_results": tg_results,
        "web_references": web_results,
        "fonte": "TransfereGov API + Portal da Transparência",
    }


async def tool_search_transferencias(municipio: str, uf: str = "", ano: int = 2024) -> dict[str, Any]:
    """Search federal transfers to a municipality."""
    query = f"transferencias federais {municipio} {uf} {ano} site:portaldatransparencia.gov.br OR site:tesourotransparente.gov.br"
    web_results = await tool_web_search(query, max_results=3)

    # Try TransfereGov convenios API
    convenios: list[dict[str, Any]] = []
    try:
        conv_url = f"https://api.transferegov.gestao.gov.br/convenio?nome_municipio=ilike.*{quote_plus(municipio)}*&limit=10&order=valor_global.desc"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(conv_url, headers={"Accept": "application/json"})
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, list):
                    for item in data[:10]:
                        convenios.append({
                            "proponente": item.get("nome_proponente", ""),
                            "valor_global": item.get("valor_global", 0),
                            "objeto": item.get("objeto_proposta", "")[:200],
                            "situacao": item.get("situacao_proposta", ""),
                            "orgao": item.get("nome_orgao_concedente", ""),
                        })
    except Exception as e:
        logger.warning("TransfereGov convenios failed: %s", e)

    return {
        "municipio": municipio,
        "convenios": convenios,
        "web_references": web_results,
        "fonte": "TransfereGov API + Tesouro Transparente",
    }


async def tool_search_ceap(parlamentar: str = "", uf: str = "", ano: int = 2024) -> dict[str, Any]:
    """Search CEAP (Cota para Exercício da Atividade Parlamentar) expenses.
    Uses Dados Abertos da Câmara API."""
    results: list[dict[str, Any]] = []
    try:
        # Câmara dos Deputados API - public, no key needed
        params = {"ano": ano, "itens": 10, "ordem": "DESC", "ordenarPor": "dataDocumento"}
        if uf:
            params["siglaUf"] = uf.upper()

        # First find the deputado by name
        if parlamentar:
            dep_url = f"https://dadosabertos.camara.leg.br/api/v2/deputados?nome={quote_plus(parlamentar)}&ordem=ASC&ordenarPor=nome"
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(dep_url, headers={"Accept": "application/json"})
                if resp.status_code == 200:
                    deps = resp.json().get("dados", [])
                    for dep in deps[:3]:
                        dep_id = dep.get("id")
                        dep_name = dep.get("nome", "")
                        dep_party = dep.get("siglaPartido", "")
                        dep_uf = dep.get("siglaUf", "")

                        # Get expenses for this deputado
                        exp_url = f"https://dadosabertos.camara.leg.br/api/v2/deputados/{dep_id}/despesas?ano={ano}&itens=15&ordem=DESC&ordenarPor=dataDocumento"
                        exp_resp = await client.get(exp_url, headers={"Accept": "application/json"})
                        if exp_resp.status_code == 200:
                            expenses = exp_resp.json().get("dados", [])
                            total = sum(float(e.get("valorDocumento", 0)) for e in expenses)
                            top_categories: dict[str, float] = {}
                            for e in expenses:
                                cat = e.get("tipoDespesa", "Outros")
                                top_categories[cat] = top_categories.get(cat, 0) + float(e.get("valorDocumento", 0))

                            results.append({
                                "deputado": dep_name,
                                "partido": dep_party,
                                "uf": dep_uf,
                                "total_amostra": round(total, 2),
                                "num_despesas": len(expenses),
                                "top_categorias": dict(sorted(top_categories.items(), key=lambda x: -x[1])[:5]),
                                "despesas_recentes": [
                                    {
                                        "tipo": e.get("tipoDespesa", ""),
                                        "fornecedor": e.get("nomeFornecedor", ""),
                                        "cnpj_fornecedor": e.get("cnpjCpfFornecedor", ""),
                                        "valor": float(e.get("valorDocumento", 0)),
                                        "data": e.get("dataDocumento", ""),
                                    }
                                    for e in expenses[:5]
                                ],
                            })
        else:
            # No specific parlamentar - search by UF
            query = f"CEAP despesas parlamentares {uf} {ano}"
            web_results = await tool_web_search(query, max_results=3)
            return {"uf": uf, "ano": ano, "web_references": web_results, "fonte": "Dados Abertos da Câmara"}

    except Exception as e:
        logger.warning("CEAP search failed: %s", e)

    return {
        "parlamentar": parlamentar,
        "uf": uf,
        "ano": ano,
        "resultados": results,
        "fonte": "Dados Abertos da Câmara dos Deputados (dadosabertos.camara.leg.br)",
    }


async def tool_search_pep_city(cidade: str, uf: str = "") -> dict[str, Any]:
    """Search politically exposed persons (PEPs) and public figures for a city.
    Combines Neo4j graph data with web search."""
    # Search for politicians, judges, prosecutors in this city
    queries = [
        f"prefeito vereador {cidade} {uf} 2024",
        f"politicos investigados {cidade} {uf}",
        f"deputado federal {uf} emendas {cidade}",
    ]

    all_results: list[dict[str, str]] = []
    for q in queries:
        results = await tool_web_search(q, max_results=2)
        all_results.extend(results)

    # Search Câmara API for deputies from this state
    deputados: list[dict[str, str]] = []
    if uf:
        try:
            dep_url = f"https://dadosabertos.camara.leg.br/api/v2/deputados?siglaUf={uf.upper()}&ordem=ASC&ordenarPor=nome&itens=50"
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(dep_url, headers={"Accept": "application/json"})
                if resp.status_code == 200:
                    deps = resp.json().get("dados", [])
                    for dep in deps:
                        deputados.append({
                            "nome": dep.get("nome", ""),
                            "partido": dep.get("siglaPartido", ""),
                            "uf": dep.get("siglaUf", ""),
                            "email": dep.get("email", ""),
                            "id_camara": str(dep.get("id", "")),
                        })
        except Exception as e:
            logger.warning("Deputados API failed: %s", e)

    return {
        "cidade": cidade,
        "uf": uf,
        "deputados_federais": deputados,
        "web_references": all_results,
        "dica": f"Use search_ceap com o nome do deputado para ver gastos. Use search_emendas com '{cidade}' para ver emendas direcionadas.",
        "fonte": "Dados Abertos da Câmara + Web Search",
    }
