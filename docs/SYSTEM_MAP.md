# SYSTEM MAP — EGOS Inteligência

> **Version:** 1.1.0 | **Updated:** 2026-03-06
> **Purpose:** Complete inventory of API routes, frontend pages, containers, and middleware.

---

## Infrastructure (Docker Compose)

| Container | Image | Port | Purpose |
|-----------|-------|------|---------|
| **bracc-neo4j** | neo4j:5-community | 7474, 7687 | Graph database (77.0M entities, 25.1M `SOCIO_DE`) |
| **redis** | redis:7-alpine | 6379 | Cache (512MB, allkeys-lru) |
| **api** | python:3.12-slim | 8000 | FastAPI backend |
| **frontend** | node:20-alpine | 5173 | React 18 + Vite |
| **caddy** | caddy:2 | 80, 443 | Reverse proxy + SSL |

**Network:** `bracc` (bridge)
**VPS:** 217.216.95.126 (Contabo, 12 vCPU, 48GB RAM, 500GB SSD)
**Domain:** inteligencia.egos.ia.br
**Reality check (2026-03-06):** 5/5 containers healthy, but `bracc-etl.service` inactive and `/api/v1/meta/etl-progress` stale em 90% após falha de pós-load do CNPJ.

---

## API Routes (13 routers, 55+ endpoints)

### `/api/v1/chat` — Chat (1 endpoint)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/chat` | No | AI chat with 26 tools, function calling |

### `/api/v1/conversations` — Conversations (5 endpoints)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | No | List conversations |
| POST | `/` | No | Create conversation |
| GET | `/{conv_id}` | No | Get conversation |
| DELETE | `/{conv_id}` | No | Delete conversation |
| PATCH | `/{conv_id}/title` | No | Update title |

### `/api/v1/search` — Search (1 endpoint)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/search` | No | Fuzzy + wildcard entity search (cached 2min) |

### `/api/v1/entity` — Entity (4 endpoints)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/{cpf_or_cnpj}` | No | Entity by CPF/CNPJ |
| GET | `/by-element-id/{id}` | No | Entity by Neo4j element ID |
| GET | `/{id}/exposure` | No | Risk exposure score |
| GET | `/{id}/timeline` | No | Temporal timeline |
| GET | `/{id}/connections` | No | Entity connections (1 hop) |

### `/api/v1/graph` — Graph (1 endpoint)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/{entity_id}` | No | Graph traversal for visualization |

### `/api/v1/patterns` — Patterns (3 endpoints)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | No | List all pattern detectors |
| GET | `/{entity_id}` | No | Run all patterns for entity |
| GET | `/{entity_id}/{pattern}` | No | Run specific pattern |

### `/api/v1/baseline` — Baseline (1 endpoint)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/{entity_id}` | No | Entity baseline profile |

### `/api/v1/investigation` — Investigations (14 endpoints)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/` | JWT | Create investigation |
| GET | `/` | JWT | List investigations |
| GET | `/{id}` | JWT | Get investigation |
| PATCH | `/{id}` | JWT | Update investigation |
| DELETE | `/{id}` | JWT | Delete investigation |
| POST | `/{id}/entries` | JWT | Add entry |
| POST | `/{id}/entries/batch` | JWT | Batch add entries |
| GET | `/{id}/entries` | JWT | List entries |
| POST | `/{id}/entities` | JWT | Add entity |
| GET | `/{id}/entities` | JWT | List entities |
| DELETE | `/{id}/entries/{eid}` | JWT | Delete entry |
| DELETE | `/{id}/entities/{eid}` | JWT | Delete entity |
| POST | `/{id}/share` | JWT | Share publicly |
| GET | `/{id}/export` | JWT | Export JSON |
| GET | `/{id}/export/md` | JWT | Export Markdown |
| GET | `/{id}/export/html` | JWT | Export HTML |
| GET | `/{id}/export/pdf` | JWT | Export PDF |

### `/api/v1/shared` — Shared Investigations (1 endpoint)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/{token}` | No | View shared investigation |

### `/api/v1/public` — Public API (3 endpoints)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/meta` | No | Public metadata |
| GET | `/patterns/company/{cnpj}` | No | Company patterns |
| GET | `/graph/company/{ref}` | No | Company graph |

### `/api/v1/meta` — Meta/Health (7 endpoints)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Neo4j connection check |
| GET | `/stats` | No | Graph statistics |
| GET | `/sources` | No | Data source list |
| GET | `/cache-stats` | No | Redis cache metrics |
| DELETE | `/cache` | No | Flush cache |
| GET | `/security` | No | Security config status |
| GET | `/etl-progress` | No | ETL pipeline progress |

### `/api/v1/monitor` — Monitor (2 endpoints)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/sanctions/recent` | No | Recent CEIS+CNEP sanctions |
| GET | `/report/{municipio}` | No | Auto-generate municipal report |

### `/api/v1/analytics` — Analytics (2 endpoints)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/pageview` | No | Track page view |
| GET | `/summary` | No | Analytics summary |

### `/api/v1/activity` — Activity Feed (2 endpoints)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/feed` | No | Activity feed |
| GET | `/stats` | No | Activity stats |

### `/api/v1/auth` — Auth (3 endpoints)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/register` | No | Register user |
| POST | `/login` | No | Login (JWT) |
| GET | `/me` | JWT | Current user |

### `/api/v1/gazette-monitor` — Gazette Monitor (2 endpoints)
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/scan` | No | Scan gazette for patterns |
| GET | `/patterns` | No | List gazette patterns |

---

## Frontend Pages (14 pages)

| Route | Page | Auth | Description |
|-------|------|------|-------------|
| `/` | Landing.tsx | No | Hero search + live stats + reports + timeline |
| `/app` | Dashboard.tsx | No | Recent searches + quick search |
| `/app/search` | Search.tsx | No | Full entity search |
| `/app/analysis/:id` | EntityAnalysis.tsx | No | Deep entity analysis |
| `/app/graph/:id` | GraphExplorer.tsx | No | Interactive graph visualization |
| `/app/patterns` | Patterns.tsx | No | Pattern detection UI |
| `/app/baseline/:id` | Baseline.tsx | No | Entity baseline profile |
| `/app/investigations` | Investigations.tsx | JWT | Investigation notebook |
| `/app/shared/:token` | SharedInvestigation.tsx | No | Public shared investigation |
| `/app/analytics` | Analytics.tsx | No | Page view analytics |
| `/app/activity` | Activity.tsx | No | Activity feed |
| `/app/reports` | Reports.tsx | No | Published investigation reports |
| `/login` | Login.tsx | No | Auth login |
| `/register` | Register.tsx | No | Auth register |

---

## AI Chat Tools (26)

| # | Tool | Source | Description |
|---|------|--------|-------------|
| 1 | search_entities | Neo4j | Fuzzy + wildcard entity search |
| 2 | get_entity_connections | Neo4j | 1-hop connections |
| 3 | cypher_query | Neo4j | Direct Cypher query |
| 4 | web_search | Brave/DDG | Web search with fallback |
| 5 | search_emendas | TransfereGov | Parliamentary amendments |
| 6 | search_transferencias | TransfereGov | Federal transfers |
| 7 | search_ceap | Camara | Deputy expenses |
| 8 | search_votacoes | Camara | Roll call votes |
| 9 | search_gazettes | Querido Diario | Municipal gazettes |
| 10 | search_servidores | Portal Transparencia | Federal employees |
| 11 | search_licitacoes | Portal Transparencia | Federal procurements |
| 12 | search_contratos | Portal Transparencia | Federal contracts |
| 13 | search_sancoes | Portal Transparencia | Federal sanctions |
| 14 | search_cpgf | Portal Transparencia | Gov credit card |
| 15 | pncp_licitacoes | PNCP | National procurements |
| 16 | cnpj_info | Querido Diario | Company info |
| 17 | opencnpj | OpenCNPJ | Receita Federal data |
| 18 | oab_advogado | OAB/CNA | Lawyer registry |
| 19 | bnmp_mandados | BNMP/CNJ | Arrest warrants |
| 20 | procurados_lookup | Policia Federal | Wanted persons |
| 21 | lista_suja_lookup | MTE | Slave labor list |
| 22 | datajud_processos | DataJud/CNJ | Court proceedings |
| 23 | interpol_notices | Interpol | Red/yellow notices |
| 24 | search_pep_city | Camara + Web | PEPs by city |
| 25 | search_receita_cnpj | Receita Federal | Direct CNPJ lookup |
| 26 | get_graph_stats | Neo4j | Graph statistics |

---

## Pattern Detectors (10)

| Pattern | Description |
|---------|-------------|
| contract_splitting | Fractionated contracts to avoid bidding |
| hhi_concentration | Market concentration (HHI > 0.25) |
| benford_analysis | Benford's Law deviation in values |
| pep_company_ownership | PEP as company partner |
| revolving_door | Public→private employment pattern |
| amendment_beneficiary | Amendment benefits donor's company |
| single_bidder_repeat | Repeated sole-source contracts |
| same_day_contracts | Multiple same-day contracts |
| shared_address_network | Competing companies at same address |
| inexigibilidade_recurrence | Repeated bidding exemptions |

---

## Middleware & Services

| Component | File | Purpose |
|-----------|------|---------|
| Input Sanitizer | `middleware/input_sanitizer.py` | 10 prompt injection patterns |
| Public Guard | `services/public_guard.py` | CPF blocking, PII masking |
| Cache Service | `services/cache.py` | Redis cache-aside (TTL per endpoint) |
| Export Service | `services/export_service.py` | MD/HTML investigation renderers |
| CORS | `main.py` | Explicit origins (not wildcard) |
| JWT Auth | `auth.py` | JWT token auth for investigations |

---

## External Bots (PM2 on VPS)

| Bot | Platform | PM2 Name | Tools | Status |
|-----|----------|----------|-------|--------|
| Discord | discord.js | egos-discord | 14 OSINT | LIVE |
| Telegram | Telegraf | egos-telegram | 14 OSINT | LIVE |

**Location:** `/opt/egos-bot/`
**Healthcheck:** Cron 5min, auto-restart, Telegram alerts

---

*55+ API endpoints | 14 pages | 26 AI tools | 10 pattern detectors | 5 containers | 2 bots | ETL control-plane drift documented*
