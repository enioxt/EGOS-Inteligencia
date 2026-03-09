# EGOS Inteligência — System Capabilities Report

> **Generated:** 2026-03-03 | **Version:** 1.0
> **Environment:** VPS Contabo (12 CPU, 48GB RAM) | Neo4j 5 Community + Redis 7 + FastAPI
> **Domain:** inteligencia.egos.ia.br

---

## 1. Graph Database (Neo4j)

| Metric | Value |
|--------|-------|
| **Total Nodes** | 9.166.587 |
| **Total Relationships** | 34.507 |
| **Companies** | 8.860.601 |
| **PEP Records** | 133.859 |
| **Global PEPs** | 117.901 |
| **Sanctions (CEIS/CNEP)** | 23.848 |
| **Gov Travels** | 13.184 |
| **Persons** | 7.074 |
| **Gov Card Expenses** | 6.483 |
| **Barred NGOs** | 3.590 |
| **Contracts** | 10 |
| **Investigations** | 3 |
| **Users** | 18 |
| **Database Size** | 6.7 GB (1.5 GB compressed backup) |

### Data Sources Registry

| Metric | Count |
|--------|-------|
| **Total registered sources** | 108 |
| **Implemented pipelines** | 45 |
| **Loaded & healthy** | 36 |
| **Stale (need refresh)** | 3 |
| **Blocked external** | 1 |
| **Discovered, not ingested** | 63 |

---

## 2. API Endpoints (42 routes)

### Core Endpoints — ✅ All Operational

| Category | Prefix | Routes | Status |
|----------|--------|--------|--------|
| **Meta/Health** | `/api/v1/meta/` | health, stats, sources, cache-stats, etl-progress | ✅ |
| **Search** | `/api/v1/search` | fulltext search (Neo4j) | ✅ |
| **Chat (AI Agent)** | `/api/v1/chat` | LLM + 26 tool calling | ✅ |
| **Conversations** | `/api/v1/conversations` | CRUD + Redis persistence | ✅ |
| **Entity** | `/api/v1/entity/` | by-id, by-cpf/cnpj, exposure, timeline, connections | ✅ |
| **Graph** | `/api/v1/graph/` | entity graph visualization | ✅ |
| **Investigation** | `/api/v1/investigation/` | CRUD, nodes, edges, export, PDF | ✅ |
| **Activity** | `/api/v1/activity/` | feed, stats | ✅ |
| **Analytics** | `/api/v1/analytics/` | pageview, summary | ✅ |
| **Monitor** | `/api/v1/monitor/` | sanctions/recent, report/{municipio} | ✅ |
| **Gazette Monitor** | `/api/v1/monitor/gazettes/` | scan, patterns | ✅ |
| **Baseline** | `/api/v1/baseline/` | entity baseline comparison | ✅ |
| **Public** | `/api/v1/public/` | meta, patterns, graph (no auth) | ✅ |
| **Auth** | `/api/v1/auth/` | register, login, me | ✅ |
| **Patterns** | `/api/v1/patterns/` | risk pattern detection | ✅ Enabled (10 detectors) |

### Patterns Engine — Enabled (Session 17)

The pattern detection engine (`PATTERNS_ENABLED=true`) has 10 risk detectors live in production. Detectors include:
- Contract splitting
- Shell company detection
- Single-source procurement
- Unusual growth patterns
- Cross-entity connections

---

## 3. Chat Agent — 26 AI Tools

### LLM Configuration

| Parameter | Value |
|-----------|-------|
| **Provider** | OpenRouter |
| **Model (all tiers)** | `google/gemini-2.0-flash-001` |
| **Cost per query** | ~$0.001 (R$ 0,006) |
| **Premium tier** | 30 msgs/day |
| **Free tier** | 50 msgs/day |
| **Rate tracking** | Redis INCR (24h TTL, in-memory fallback) |
| **BYOK** | Supported (user provides own OpenRouter key) |

### Tool-by-Tool Test Results (2026-03-03)

| # | Tool | API Source | Status | Rate Limits | Notes |
|---|------|-----------|--------|-------------|-------|
| 1 | `search_entities` | Neo4j Graph | ✅ | Unlimited (local) | Fulltext + CNPJ search across 9M nodes |
| 2 | `get_graph_stats` | Neo4j Graph | ✅ | Unlimited | Node/relationship counts by type |
| 3 | `get_entity_connections` | Neo4j Graph | ✅ | Unlimited | Entity relationship traversal |
| 4 | `cypher_query` | Neo4j Graph | ✅ | Unlimited | Whitelisted read-only Cypher (TASK-106) |
| 5 | `data_summary` | Internal | ✅ | Unlimited | System metadata + source count |
| 6 | `web_search` | **Brave Search API** | ✅ | 2000/month (free tier) | Fallback: DuckDuckGo HTML scraping |
| 7 | `search_emendas` | **TransfereGov API** | ✅ | Unknown (public API) | Parliamentary amendments by city |
| 8 | `search_transferencias` | **TransfereGov API** | ✅ | Unknown | Federal transfers to municipalities |
| 9 | `search_ceap` | **Câmara dos Deputados** | ✅ | Generous (public) | CEAP parliamentary expenses |
| 10 | `search_votacoes` | **Câmara dos Deputados** | ✅ | Generous | Roll-call votes, per-deputy breakdown |
| 11 | `search_pep_city` | Brave + Câmara | ✅ | Composite | PEPs by city (deputies + news) |
| 12 | `search_gazettes` | **Querido Diário (OKBR)** | ✅ | Generous (public) | Municipal official gazettes |
| 13 | `cnpj_info` | **Portal Transparência** | ✅ | 30 req/min (API key) | Company info by CNPJ |
| 14 | `opencnpj` | **OpenCNPJ** | ✅ | 3 req/min (free) | Alternative CNPJ lookup (Receita Federal) |
| 15 | `search_servidores` | **Portal Transparência** | ✅ | 30 req/min | Federal public servants salary/position |
| 16 | `search_licitacoes` | **Portal Transparência** | ✅ | 30 req/min | Federal procurement bids |
| 17 | `search_cpgf` | **Portal Transparência** | ✅ | 30 req/min | Government corporate card expenses |
| 18 | `search_viagens` | **Portal Transparência** | ✅ | 30 req/min | Government travel expenses |
| 19 | `search_contratos` | **Portal Transparência** | ✅ | 30 req/min | Federal government contracts |
| 20 | `search_sancoes` | **Portal Transparência** | ✅ | 30 req/min | CEIS/CNEP sanctioned entities |
| 21 | `search_processos` | **DataJud (CNJ)** | ✅ | Public API | Judicial cases across all courts |
| 22 | `bnmp_mandados` | **BNMP (CNJ)** | ✅ | Public API | Active arrest warrants |
| 23 | `procurados_lookup` | **PF/Interpol** | ✅ | Public (scraping) | Wanted persons (Federal Police) |
| 24 | `lista_suja_lookup` | **MTE Gov** | ✅ | Public (scraping) | Slave labor blacklist |
| 25 | `pncp_licitacoes` | **PNCP Gov** | ✅ | Public API | All-sphere procurement (fed/state/municipal) |
| 26 | `oab_advogado` | **CNA/OAB** | ✅ | Public (scraping) | Lawyer registration verification |

### External API Summary

| API Provider | Tools Using It | Auth Required | Rate Limit | Status |
|-------------|---------------|---------------|------------|--------|
| **Portal da Transparência** | 7 (servidores, licitações, cpgf, viagens, contratos, sanções, cnpj_info) | API Key ✅ | 30 req/min | ✅ Operational |
| **Câmara dos Deputados** | 2 (ceap, votações) | None | Generous | ✅ Operational |
| **TransfereGov** | 2 (emendas, transferências) | None | Unknown | ✅ Operational |
| **Brave Search** | 1 (web_search) | API Key ✅ | 2000/month | ✅ Operational (NEW KEY) |
| **DataJud (CNJ)** | 1 (processos) | Public Key | Public | ✅ Operational |
| **BNMP (CNJ)** | 1 (mandados) | None (scraping) | N/A | ✅ Operational |
| **Querido Diário (OKBR)** | 1 (gazettes) | None | Generous | ✅ Operational |
| **OpenCNPJ** | 1 (opencnpj) | None | 3 req/min | ✅ Operational |
| **PNCP** | 1 (licitações) | None | Public | ✅ Operational |
| **CNA/OAB** | 1 (advogado) | None (scraping) | N/A | ✅ Operational |
| **PF/Interpol** | 1 (procurados) | None (scraping) | N/A | ✅ Operational |
| **MTE Gov** | 1 (lista suja) | None (scraping) | N/A | ✅ Operational |
| **DuckDuckGo** | 1 (web_search fallback) | None | N/A | ✅ Fallback |
| **OpenRouter (LLM)** | 1 (chat) | API Key ✅ | Pay-per-use | ✅ Operational |

---

## 4. Infrastructure

### Containers (5, all healthy)

| Container | Image | Status | Purpose |
|-----------|-------|--------|---------|
| `bracc-neo4j` | neo4j:5-community | ✅ Healthy | Graph database (9.1M nodes) |
| `infra-redis-1` | redis:7-alpine | ✅ Healthy | Cache + conversations + rate limiting |
| `infra-api-1` | Custom Python | ✅ Healthy | FastAPI backend (42 routes) |
| `infra-frontend-1` | Custom Vite | ✅ Healthy | React SPA |
| `infra-caddy-1` | caddy:2-alpine | ✅ Up | TLS reverse proxy |

### Backup System

| Item | Detail |
|------|--------|
| **Schedule** | Daily 3AM (cron) |
| **Method** | Hot tar of Neo4j Docker volume |
| **Compression** | 6.7 GB → 1.5 GB (gzip) |
| **Retention** | Last 5 backups |
| **Script** | `/opt/bracc/scripts/neo4j-backup.sh` |

### Resilience

| Feature | Status |
|---------|--------|
| **Circuit Breaker** | ✅ Per-host (5 failures/2min → 60s cooldown) |
| **Redis Fallback** | ✅ In-memory fallback for usage/conversations |
| **Cypher Injection** | ✅ Whitelist-only (TASK-106) |
| **Rate Limiting** | ✅ Redis INCR with 24h TTL |
| **CORS** | ⚠️ `allow_headers=["*"]` (TASK-115) |
| **JWT Validation** | ⚠️ No startup check (TASK-115) |

---

## 5. Gazette Monitor (Automated Civic Intelligence)

Live-tested scan returned **102 alerts** across 10 cities in 7 days. Pattern types:

| Pattern | Risk Level | Description |
|---------|-----------|-------------|
| Contratação Emergencial | 🔴 Critical | Emergency contracts (bypass procurement) |
| Dispensa de Licitação | 🟠 High | Procurement waivers |
| Nomeação/Exoneração | 🟡 Medium | Political appointments |
| Licitação | 🟢 Low | Standard procurement |

---

## 6. Codebase Architecture (after refactoring)

### API Module Structure

| File | Lines | Purpose |
|------|-------|---------|
| `chat.py` | 845 | Router + conversation + OpenRouter caller |
| `chat_tools.py` | 393 | 26 tool definitions (function calling) |
| `chat_models.py` | 38 | Pydantic models |
| `chat_prompt.py` | 67 | System prompt |
| `conversations.py` | 274 | Redis conversation CRUD |
| `transparency_tools.py` | ~1330 | 21 external API tool implementations |
| `circuit_breaker.py` | 150 | Per-host circuit breaker |
| `cache.py` | 124 | Redis cache service |
| `public_guard.py` | — | CPF masking, Person hiding, PEP exceptions |

### Services Layer (13 modules)

`auth_service`, `baseline_service`, `cache`, `circuit_breaker`, `intelligence_provider`, `investigation_service`, `neo4j_service`, `pdf_service`, `public_guard`, `score_service`, `source_registry`, `transparency_tools`

---

## 7. Intelink Migration Status

| Feature | Intelink | br-acc (EGOS) | Status |
|---------|----------|--------------|--------|
| Chat AI Agent | ✅ | ✅ | **Adopted** (superior: 26 tools vs 14) |
| Graph Explorer | ✅ | ✅ | **Adopted** |
| Entity Analysis | ✅ | ✅ | **Adopted** |
| Search | ✅ | ✅ | **Adopted** |
| Investigation Board | ✅ | ✅ | **Adopted** |
| Dashboard | ✅ | ✅ | **Adopted** |
| Journey Tracker | ✅ | ✅ | **Adopted** |
| Landing Page | ✅ | ✅ | **Adopted** |
| Pattern Detection | ✅ | ✅ | **Adopted** (enabled session 17) |
| Baseline | ✅ | ✅ | **Adopted** |
| CMD+K Search | ✅ | ❌ | P2 — port from Intelink |
| Share Journey | ✅ | ❌ | P2 — port from Intelink |
| Investigation Timeline | ✅ | ❌ | P2 — new design needed |
| Notification System | ✅ | ❌ | P2 |
| Admin Panel | ✅ | ❌ | P2 |
| Report Generator | ✅ | ❌ | P2 |
| Multi-workspace | ✅ | ❌ | P3 |

**Verdict:** 10/17 features adopted. No migration blocker — br-acc already surpasses Intelink in backend capabilities (26 tools vs 14, 9.1M nodes, circuit breaker, gazette monitor).

---

## 8. Limitations & Known Issues

### Critical

| Issue | Impact | Task |
|-------|--------|------|
| API keys in git history | Security | TASK-113 (BFG Repo Cleaner) |
| ~~Pattern engine disabled~~ | ~~No risk detection~~ | ✅ Enabled session 17 |
| ~~CORS `allow_headers=["*"]`~~ | ~~Security surface~~ | ✅ TASK-115 (explicit headers, session 18) |

### Moderate

| Issue | Impact |
|-------|--------|
| OpenCNPJ rate limit (3/min) | Slow for batch CNPJ lookups |
| Brave Search (2000/month) | ~66 searches/day max |
| Portal Transparência (30/min) | Adequate for chat, too slow for bulk |
| Neo4j Community (no hot backup) | Hot tar = possible inconsistency |
| ~~No integration tests~~ | ✅ 232 API tests (219 unit + 13 sanitizer), 18 live integration |
| ETL not running locally | 8.8M companies only on VPS |

### Low

| Issue | Impact |
|-------|--------|
| 63 data sources not yet ingested | Incomplete coverage |
| Relationship count low (34K vs 9M nodes) | Most companies isolated |
| Gazette monitor scan is synchronous | Slow for many cities |

---

## 9. Cost Analysis

| Resource | Monthly Cost |
|----------|-------------|
| **VPS (Contabo)** | ~€35/month |
| **OpenRouter (Gemini Flash)** | ~$3-5/month (at 1000 queries) |
| **Brave Search** | Free tier (2000/month) |
| **All other APIs** | Free (public government APIs) |
| **Total** | ~**$40/month** |

---

## 10. What Can We Do RIGHT NOW

### With 9.1M nodes + 26 tools + 14 external APIs:

1. **Investigate any Brazilian company** — CNPJ lookup, sanctions check, contracts, partner network
2. **Monitor any city** — gazette scan, emendas, transfers, PEPs, procurement
3. **Track any politician** — CEAP expenses, votes, travel, card expenses
4. **Search judicial records** — DataJud across all courts, arrest warrants (BNMP)
5. **Web intelligence** — Brave Search for news, investigations, whistleblower reports
6. **Cross-reference** — Neo4j graph connects companies↔people↔sanctions↔contracts
7. **Generate reports** — per-municipality sanction reports, PDF export
8. **Chat interface** — Natural language queries calling 26 tools automatically
9. **Real-time gazette monitoring** — 102 alerts found in 7-day scan across 10 cities
10. **Lawyer verification** — OAB registration check
11. **Slave labor blacklist** — MTE lista suja lookup
12. **Wanted persons** — PF/Interpol procurados

### What We CANNOT Do Yet

1. **Run locally** — Neo4j data (6.7GB) only on VPS. ETL ingestion takes days for 8.8M companies
2. **Bulk analysis** — API rate limits prevent mass scanning (Portal: 30/min, OpenCNPJ: 3/min)
3. ~~**Pattern detection** — Engine exists but disabled pending validation~~ ✅ Enabled
4. **Historical analysis** — Low relationship count (34K) means most companies are isolated nodes
5. **Real-time alerts** — Gazette monitor is on-demand, not continuous
6. **Multi-user** — Auth exists but no multi-tenant workspace separation

---

## 11. Brutal Competitive Comparison

### vs. Best-in-Class Tools (Honest Assessment)

| Dimension | **EGOS Inteligência** | **Palantir Gotham** | **Maltego** | **OCCRP Aleph** | **OpenSanctions** |
|-----------|----------------------|--------------------|-----------|-----------------|--------------------|
| **Nodes** | 9.1M | Billions | N/A (user-built) | 270M+ | 2.1M entities |
| **Sources** | 36 loaded / 108 registered | 1000+ | 100+ transforms | 600+ datasets | 297 sources |
| **Graph Traversal** | Basic (1-hop, no GDS) | Advanced (multi-hop, ML) | Advanced (transforms) | Advanced (cross-ref) | Advanced (matching) |
| **Pattern Detection** | ✅ 10 rule-based detectors | ✅ ML-powered | ✅ Manual + transforms | ✅ Rule-based | ✅ Dedup + matching |
| **Entity Resolution** | ⏳ Built, pending ETL Phase 3 | ✅ Probabilistic | ✅ Manual | ✅ followthemoney | ✅ OpenSanctions |
| **Real-time Alerts** | ❌ On-demand only | ✅ Continuous | ❌ | ✅ | ✅ |
| **Multi-user** | ❌ Single-tenant | ✅ Enterprise | ✅ Teams | ✅ | ✅ API |
| **Price** | **$25/month** | **$10M+/year** | **$5K+/year** | **Free (restricted)** | **Free (API)** |
| **Open Source** | ✅ AGPL | ❌ Proprietary | ❌ Proprietary | ✅ MIT | ✅ MIT |
| **Brazil Focus** | ✅ 100% BR data | ❌ Generic | ❌ Generic | ⚠️ Some BR | ⚠️ Some BR |
| **Accessibility** | ✅ Chat in Portuguese | ❌ Analyst-only | ⚠️ Technical | ⚠️ Technical | ⚠️ API-only |

### Where We WIN (honestly)

1. **Only open-source OSINT platform 100% focused on Brazil** — no competitor offers this
2. **Natural language chat** in Portuguese calling 26 tools — Palantir/Maltego require trained analysts
3. **Cost:** $25/month vs $10M+/year (Palantir) or $5K/year (Maltego)
4. **8.8M Brazilian companies** loaded — more BR data than OCCRP Aleph
5. **Free for citizens** — no paywall, no registration required for chat
6. **14 government APIs integrated** in one interface — nobody else does this

### Where We LOSE (brutally honest)

1. **Entity resolution = ZERO** — We have 9.1M nodes but only 34K relationships. Most companies are **isolated dots with no connections**. This is our #1 problem. Without entity resolution, our "graph" is really just a search engine with extra steps.
2. ~~**Pattern detection disabled**~~ — ✅ **Enabled session 17** with 10 rule-based detectors (Benford, HHI, sanction co-occurrence, etc.). No ML yet, but rule-based patterns are live.
3. **No ML/AI analysis** — Palantir uses machine learning for anomaly detection. We use an LLM to format search results. There's no intelligence in "Inteligência" yet.
4. **Relationship building not automated** — We loaded 8.8M companies but didn't build SOCIO_DE relationships from QSA data. The ETL created nodes but skipped the most important part: connecting them.
5. **No entity resolution / deduplication** — The same person can appear as "JOÃO DA SILVA" in CEIS and "João da Silva" in PEP and we'd never know they're the same person.
6. **Single-tenant, single-server** — One VPS, one user at a time for investigations. No collaboration features.
7. **No historical tracking** — We can't show "this company was sanctioned in 2020, then won a contract in 2021" because we don't track temporal relationships.
8. **Chat is a wrapper** — The AI chat calls APIs and formats results. It doesn't reason, doesn't chain investigations, doesn't discover novel connections. It's a glorified search aggregator.
9. **Documentation says more than exists** — README mentions "79 fontes", "53.6M empresas", "141M nós" as targets, but the reality is 36 sources loaded and 9.1M nodes with almost no relationships.
10. **No tests** — Zero integration tests, zero unit tests. We can't guarantee anything works after a code change.

### Real Value Assessment

| What We Claim | Reality | Gap |
|---------------|---------|-----|
| "Grafo de vínculos" | 9.1M nodes, 34K edges = **0.004% connectivity** | 🔴 Critical — not a graph, it's a database |
| "26 ferramentas OSINT" | 26 API wrappers that format JSON | 🟡 True but oversold — these are API calls, not intelligence |
| "Detectar padrões de corrupção" | 10 pattern detectors enabled, no ML | � Rule-based detection works, ML not yet |
| "Cruzamento inteligente" | LLM calls tools sequentially | 🟡 It works, but "inteligente" is generous |
| "108 fontes de dados" | 36 loaded, 63 discovered but not ingested | 🟡 Aspirational, not current |
| "Open source OSINT for Brazil" | ✅ This is true and unique | 🟢 Real differentiator |
| "$25/month for everything" | ✅ This is true | 🟢 Real differentiator |
| "Chat em português 24/7" | ✅ Works, tested, ~R$0.006/query | 🟢 Real differentiator |

### Priority Actions to Close Gaps

1. **🔴 P0: Build relationships from QSA data** — Transform isolated company nodes into a connected graph. Without this, the project's core value proposition is hollow.
2. **🔴 P0: Entity resolution** — Implement fuzzy matching across datasets (name normalization + CPF/CNPJ linking)
3. **✅ P1: Enable pattern detection** — 10 risk detectors enabled in production (session 17)
4. **🟠 P1: Integration tests** — At least 20 tests covering critical paths
5. **🟡 P2: Temporal relationships** — Add date-aware edges to track when connections were active
6. **🟡 P2: Continuous gazette monitoring** — Cron-based scan with Telegram alerts

---

*"Siga o dinheiro público. 9.1 milhões de entidades. 26 ferramentas. 14 APIs. R$ 0,006 por consulta."*

*"Mas sejamos honestos: sem relações entre entidades, é um banco de dados com chatbot. O grafo é a promessa — que ainda precisa ser cumprida."*
