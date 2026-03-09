# AGENTS.md — EGOS Inteligência (BR/ACC)

> **VERSION:** 1.1.0 | **UPDATED:** 2026-03-06
> **TYPE:** Intelligence Platform

---

## Project Overview

| Item | Value |
|------|-------|
| **Projeto** | EGOS Inteligência (BR/ACC) |
| **Descrição** | Plataforma open-source de inteligência sobre dados públicos brasileiros |
| **Path** | /home/enio/br-acc |
| **VPS** | 217.216.95.126 (Contabo, /opt/bracc) |
| **Repo** | github.com/enioxt/EGOS-Inteligencia |
| **Deploy** | Docker Compose no VPS (API + Frontend + Neo4j + Redis) |
| **URL** | inteligencia.egos.ia.br |
| **Framework** | EGOS (egos-lab) — regras compartilhadas |

## Architecture

```
br-acc/
├── api/             # FastAPI backend (Python 3.12, uvicorn)
│   └── src/bracc/   # Core: routers, services, config
├── etl/             # 46 ETL pipelines (Python, Neo4j ingestion)
├── frontend/        # React 18 + Vite + TypeScript
├── infra/           # Docker Compose, nginx, scripts VPS
├── scripts/         # Automation, security, audit
├── docs/            # Technical docs, analysis, legal
├── .guarani/        # LOCAL coding rules (from EGOS framework)
└── .windsurf/       # Workflows + skills
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.12, FastAPI, uvicorn |
| **Frontend** | React 18, Vite, TypeScript, CSS Modules |
| **Database** | Neo4j 5.x (graph), Redis (cache) |
| **AI** | OpenRouter (Gemini Flash / GPT-4o-mini) |
| **Deploy** | Docker Compose on Contabo VPS |
| **ETL** | Python ETL + tmux/manual orchestration + monitor script |

## Commands

```bash
# Development
cd api && uv run uvicorn src.bracc.main:app --reload --port 8000
cd frontend && npm run dev

# Testing
cd api && uv run pytest -x --tb=short     # 235+ tests
cd frontend && npm test                     # Frontend tests

# VPS Operations
ssh root@217.216.95.126
cd /opt/bracc/infra && docker compose restart api
cd /opt/bracc/infra && docker compose build frontend && docker compose up -d frontend
docker compose logs -f api --tail 50

# Quick checks
cd api && uv run ruff check src/           # Python lint (~5s)
cd frontend && npx tsc --noEmit --pretty false 2>&1 | grep "error TS" | head -20

# Deploy
git push origin main                        # Then VPS: git pull + docker compose restart
```

## SSOT Files (5 govern everything)

| File | Purpose |
|------|---------|
| `AGENTS.md` | Project config (this file) |
| `TASKS.md` | All tasks (SSOT) |
| `.windsurfrules` | Agent rules |
| `.guarani/PREFERENCES.md` | Coding standards |
| `.guarani/IDENTITY.md` | Agent identity |

## Frozen Zones

> **DO NOT EDIT** without explicit user request:
> - **Auth/JWT:** `api/src/bracc/auth.py`, JWT secret config
> - **Docker Compose:** `infra/docker-compose.yml` (production topology)
> - **ETL in progress:** Any ETL pipeline currently running (TASK-001)
> - **Neo4j schema:** Node labels and relationship types in production

## Key Metrics

| Metric | Value |
|--------|-------|
| Neo4j Entities | 77,035,803 |
| Neo4j Relationships | 25,091,492 `SOCIO_DE` |
| Data Sources Loaded | 36 |
| Data Sources Mapped | 108 |
| AI Chat Tools | 26 |
| Pattern Detectors | 10 |
| ETL Pipelines | 46 |
| Production Containers | 5/5 healthy |
| ETL Reality Check | Phase 3 interrompida em 17,454,980 / 24.6M Partner (~70%) |
| ETL Control Plane | `bracc-etl.service` inactive; `/api/v1/meta/etl-progress` stale em 90% |
| Monthly Cost | ~$36 |

## Sibling Projects

| Project | Path | Relationship |
|---------|------|-------------|
| egos-lab | /home/enio/egos-lab | Framework (shared rules canonical here) |
| carteira-livre | /home/enio/carteira-livre | Separate product (DO NOT MIX) |

## Legal & Ethics Docs (root level)

| File | Purpose |
|------|---------|
| `ETHICS.md` | Prohibited uses, non-accusatory language |
| `LGPD.md` | Data protection baseline |
| `PRIVACY.md` | Privacy policy |
| `TERMS.md` | Terms of service |
| `DISCLAIMER.md` | Legal disclaimer |
| `SECURITY.md` | Security policy |
| `ABUSE_RESPONSE.md` | Abuse handling |

---

*"Dados públicos, código aberto, transparência real."*
