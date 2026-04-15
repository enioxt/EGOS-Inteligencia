# EGOS-KERNEL-PROPAGATED: 2026-04-15
<!-- AUTO-INJECTED by disseminate-propagator.ts — DO NOT EDIT THIS BLOCK MANUALLY -->
<!-- Kernel commit: 432c04f | 1 rule section(s) changed -->
<!-- Kernel rules: ~/.claude/CLAUDE.md (always authoritative) -->
<!-- Re-run: bun ~/egos/scripts/disseminate-propagator.ts --all to update -->
<!-- + CAPABILITY_REGISTRY.md → ## By Repo Group (Quick Navigation) (18 lines) -->

> **EGOS Kernel rules apply to this repo.** See `~/.claude/CLAUDE.md` for full rules.
> Critical non-negotiables: no force-push main, no secret logging, no git add -A in agents.
> SSOT map: `~/.claude/egos-rules/ssot-map.md` | LLM routing: `~/.claude/egos-rules/llm-routing.md`

---

# CLAUDE.md — EGOS Inteligência (egos-inteligencia)

> Lido automaticamente pelo Claude Code CLI ao executar `claude` neste diretório.

## Projeto

**EGOS Inteligência** — Plataforma open-source de inteligência sobre dados públicos brasileiros. Grafo com 77M entidades (59.5M empresas + 17.5M sócios + 7K pessoas) e 25.1M relacionamentos. Deploy em produção: `https://inteligencia.egos.ia.br`.

Repositório público: `github.com/enioxt/EGOS-Inteligencia`

## Bloqueio Crítico Atual

**ETL CNPJ preso a 90%** — O serviço `egos-inteligencia-etl.service` está inativo. A Fase 3 carregou massa crítica, mas o pós-load falhou com `Neo.ClientError.Statement.ParameterMissing: Expected parameter(s): run_id`. Fix local já aplicado em `etl/src/egos_inteligencia_etl/linking_hooks.py` e `runner.py` — **falta redeploy/reexecução no VPS**.

## Arquitetura

```text
egos-inteligencia/
├── api/             # FastAPI backend (Python 3.12, uvicorn)
│   └── src/egos_inteligencia/   # routers (search, meta, entity), services (cache.py), config
├── etl/             # 46 pipelines ETL (Python, ingestão Neo4j)
│   └── src/egos_inteligencia_etl/
│       ├── linking_hooks.py   # FIX APLICADO (run_id bug)
│       └── runner.py          # FIX APLICADO (run_id bug)
├── frontend/        # React 18 + Vite + TypeScript
├── infra/           # Docker Compose, nginx, scripts VPS
│   └── scripts/     # neo4j-memory-upgrade.sh, post-etl-optimize.sh
├── scripts/         # Automação, segurança, auditoria
├── docs/            # Técnicos, análise, legal
│   └── showcase/    # patense-investigation.html
├── .guarani/        # Regras de código locais (framework EGOS)
└── .windsurf/       # Workflows + skills
```

## Stack

| Camada | Tecnologia |
|--------|-----------|
| **Backend** | Python 3.12, FastAPI, uvicorn |
| **Frontend** | React 18, Vite, TypeScript, CSS Modules |
| **Banco Principal** | Neo4j 5.x (grafo) |
| **Cache** | Redis (cache-aside, TTL configurável) |
| **AI** | OpenRouter (Gemini Flash / GPT-4o-mini) |
| **Deploy** | Docker Compose no Contabo VPS |
| **ETL** | Python ETL + tmux/systemd + monitor script |

## Comandos Principais

```bash
# Local
pip install -e etl/           # Instalar ETL em modo dev
pytest etl/tests/             # Rodar testes do ETL

# VPS (217.216.95.126, /opt/egos_inteligencia)
ssh root@217.216.95.126
cd /opt/egos_inteligencia
docker compose ps             # Estado dos 5 containers
docker compose logs api -f    # Logs da API
systemctl status egos-inteligencia-etl    # Status do ETL service (deve estar ativo)

# ETL (executar no VPS após fix de run_id)
# Ver README do ETL para comando exato de retomada da Fase 3

# API
curl https://inteligencia.egos.ia.br/api/v1/meta/etl-progress
curl https://inteligencia.egos.ia.br/api/v1/meta/cache-stats
```

## Regras

- Leia `.guarani/PREFERENCES.md` para padrões de código locais
- Commits convencionais: `feat:`, `fix:`, `chore:`, `docs:`
- Todo claim de capacidade deve ter evidência de runtime (sem "running" sem prova)
- LGPD/segurança: masking obrigatório em outputs públicos
- Novas features devem fortalecer o caso de referência para EGOS Guard Brasil
- Kernel SSOT: `/home/enio/egos/docs/SSOT_REGISTRY.md`

## Infraestrutura VPS

| Item | Valor |
|------|-------|
| **VPS Atual** | Contabo — 217.216.95.126 (`/opt/egos_inteligencia`) |
| **Migração planejada** | Hetzner |
| **Docker stack** | 5/5 containers saudáveis |
| **ETL service** | `egos-inteligencia-etl.service` — INATIVO (bloqueado) |
| **Grafo atual** | 77,035,803 entidades, 25,091,492 `SOCIO_DE` |

## Estado do ETL (2026-03-18)

- Fase 1 (estab_lookup): status desconhecido
- Fase 2 (Company nodes): 8,860,601 carregados
- Fase 3 (Person/Partner + SOCIO_DE): massa crítica carregada, pós-load falhou
- Fase 4 (post-load hooks): bloqueada aguardando Fase 3 completar
- Fix local (`run_id`): aplicado em `linking_hooks.py` e `runner.py` — aguarda redeploy

---

## Regra: Próxima Task

Quando iniciado neste repositório e perguntado "qual a próxima task?" ou "what's next?":
1. Leia este CLAUDE.md para contexto
2. Leia TASKS.md e identifique a task P0/P1 de maior prioridade incompleta
3. Leia PRs abertos: `gh pr list`
4. Responda com: task ID, descrição, arquivos envolvidos, e próximo passo concreto
Sem fricção. Direto ao ponto.

# INC-003 ANTI-HALLUCINATION (2026-04-08): Before adding task→verify artifact exists. After implement→mark [x] same commit. Checklist→spot-check top 5 P0/P1 tasks.
