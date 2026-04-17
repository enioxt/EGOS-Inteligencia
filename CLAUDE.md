# EGOS-KERNEL-PROPAGATED: 2026-04-17
<!-- AUTO-INJECTED by disseminate-propagator.ts — DO NOT EDIT THIS BLOCK MANUALLY -->
<!-- Kernel commit: dd6e593 | 0 rule section(s) changed -->
<!-- Source of rules: egos/AGENTS.md (canonical). Kernel-only authoritative copy: ~/.claude/CLAUDE.md -->
<!-- Re-run: bun ~/egos/scripts/disseminate-propagator.ts --all to update -->

> ⚠️ **PROPAGATED FROM KERNEL** — Edits to this block are overwritten by next `bun governance:sync:exec`.
> Edit kernel `egos/AGENTS.md` section between `<!-- PROPAGATE-RULES-BEGIN -->` and `<!-- PROPAGATE-RULES-END -->` instead.

<!-- === BEGIN KERNEL RULES BODY (auto-injected from egos/AGENTS.md) === -->

## 📋 Canonical Rules (authoritative across ALL IDEs)

This section is the single source of truth for agent rules. Claude Code reads this. Windsurf reads this. Cursor reads this. Codex reads this. GitHub Copilot reads this. When `~/.claude/CLAUDE.md`, `.windsurfrules`, or repo-level `CLAUDE.md` diverge from this file, **AGENTS.md wins**.

### R0 — Critical non-negotiables (irreversible damage prevention)
1. **NEVER `git push --force` to main/master/production** — use `bash scripts/safe-push.sh` (INC-001)
2. **NEVER log/echo/commit secrets** — no `.env`, no hardcoded keys
3. **NEVER publish externally without human approval** — articles, X posts, outreach
4. **NEVER `git add -A` in background agents** — always `git add <specific-file>` (INC-002)
5. **COMMIT TASKS.md immediately** after edit (parallel agents lose uncommitted state)

### R1 — Verification before assertion
1. **Code claims** (function exists, caller count, import usage, dead code, route mapping) → `codebase-memory-mcp` is PRIMARY. Read/Grep is fallback for docs/config/markdown only. If `cbm-code-discovery-gate` hook fires, load MCP tools via ToolSearch; never bypass.
2. **External LLM paste** (ChatGPT/Gemini/Grok/Kimi/Perplexity output) → every named feature, commit, file, version = UNVERIFIED CLAIM. Classify REAL/CONCEPT/PHANTOM via `git log --grep` + `Glob`. High-density buzzword lists (8+ capitalized "systems") = phantom signal (INC-005).
3. **Subagent audits** (Agent/Explore/Plan outputs) = SYNTHESIS, not evidence. Before citing in commit/SSOT edit: re-verify top 3 structural claims via `codebase-memory-mcp`. Absolute audit claims ("X doesn't exist", "Y is skeleton") without file:line anchor = PHANTOM until verified (INC-006).
4. **When spawning Agent/Explore/Plan** → prompt MUST include: "return evidence tuples `{claim, evidence_path, evidence_line}`; prefix unanchored with `UNVERIFIED:`".

### R2 — SSOT integrity
1. **Scored SSOT tables** (columns: `Compliance`/`Score`/`%`/`Coverage`/`Maturity`/`Readiness`/`Grade`) MUST be wrapped in `<!-- AUTO-GEN-BEGIN:<agent> -->` / `<!-- AUTO-GEN-END -->` populated by a compliance agent, OR every row MUST carry `VERIFIED_AT` + `method` + `evidence` (file:line or cmd output SHA). Handwritten scored tables are PHANTOM VECTORS. Pre-commit blocks after MSSOT-002 ships (INC-006).
2. **Use-case scoped scoring** — before applying a uniform rubric across products, declare each product's primary use case. Mark rubric rows REQUIRED/OPTIONAL/N/A per use case. `N/A (use case: X)` is valid, not a fail. Cannot use single score column across heterogeneous use cases (INC-006).
3. **ONE SSOT per domain** — see "SSOT Map" section below. New content goes to existing SSOT, never new file. Prohibited: `docs/business/`, `docs/sales/`, `docs/notes/`, `docs/tmp/`, timestamped docs, `AUDIT*.md`, `REPORT*.md`, `DIAGNOSTIC*.md` (except in `_archived/`).
4. **Evidence-first** — every claim in durable docs (README, SSOT, article) needs: automated test exercising it, metric confirming the number, entry in manifest (`.egos-manifest.yaml` or `CAPABILITY_REGISTRY.md`), or dashboard tile. Unproven claims marked `unverified:`.

### R3 — Edit safety
1. Read before Edit (at least the relevant section). Confirm exact string. Re-read after edit.
2. Max 3 edits per file before verification read.
3. Rename/signature change → grep all callers first.
4. Large files (>300 LOC): remove dead code first (separate commit), break into phases (max 5 files).
5. **Simplicity First (Karpathy):** minimum code that solves. No speculative abstractions. Wait for 3rd repetition before extracting. Test: "Would a senior engineer call this overcomplicated?"

### R4 — Git safety
1. Force-push forbidden on main/master/production/prod/release/hotfix. Exception: `EGOS_ALLOW_FORCE_PUSH=1` in shell only.
2. Always `bash scripts/safe-push.sh <branch>` (fetch+rebase+retry).
3. `.husky/pre-push` blocks non-FF. Answer = `git fetch && git rebase`, never `--no-verify`.

### R5 — Context & swarm
1. Use Agent tool when: 5+ files to read, >3 Glob/Grep rounds expected, research+implement needed. Don't spawn for single-file edits, git ops, known answers.
2. Independent tasks → all agents in ONE message. Dependent → sequential.
3. After 10+ turns or compaction: re-read TASKS.md + current file.
4. Cost control: 3 retries fail on same error → STOP, flag `[BLOCKER]`.

### R6 — Incident-driven (always load when relevant)
| Incident | Rule |
|---|---|
| INC-001 | Force-push protocol — `bash scripts/safe-push.sh` |
| INC-002 | Git swarm — `git add <specific>`, commit TASKS.md first |
| INC-003 | TASKS.md — verify artifact before adding, mark `[x]` same commit |
| INC-004 | Supabase Realtime quota — rate limiter + retention |
| INC-005 | External LLM narrative — classify REAL/CONCEPT/PHANTOM |
| INC-006 | Subagent phantoms + scored SSOT tables — see R1.3, R2.1-2 |

Full postmortems: `docs/INCIDENTS/INC-XXX-*.md`. Index: `docs/INCIDENTS/INDEX.md`.

<!-- === END KERNEL RULES BODY === -->

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
