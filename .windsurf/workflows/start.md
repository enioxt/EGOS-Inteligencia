# /start — Session Initialization (v5.1)

## 1. Load Core Context

Read these files in order (all paths relative to repo root):

- `AGENTS.md` — Project config, stack, commands, SSOT files list
- `TASKS.md` — Current priorities (P0 → P1 → P2)
- `.guarani/PREFERENCES.md` — Coding standards and rules
- `.guarani/IDENTITY.md` — Agent identity and mission

## 2. Load Orchestration System

Read the orchestration pipeline that governs ALL work:

- `.guarani/orchestration/PIPELINE.md` — 7-phase protocol (INTAKE → CHALLENGE → PLAN → GATE → EXECUTE → VERIFY → LEARN)
- `.guarani/orchestration/GATES.md` — 5-dimension quality scoring (score >= 75 to proceed)
- `.guarani/orchestration/QUESTION_BANK.md` — 70+ maieutic questions by domain
- `.guarani/orchestration/DOMAIN_RULES.md` — Project-specific checklists

Acknowledge: "Orchestration Protocol loaded. Pipeline: 7 phases. Gate threshold: 75."

## 3. Load Meta-Prompt System

Scan `.guarani/prompts/triggers.json` for active trigger mappings:

- `.guarani/prompts/PROMPT_SYSTEM.md` — Meta-prompt index (anatomy, triggers, catalog)
- `.guarani/prompts/triggers.json` — Machine-readable keyword→prompt mappings
- `.guarani/prompts/meta/universal-strategist.md` — Game Theory + Oriental philosophy
- `.guarani/prompts/meta/brainet-collective.md` — Collective intelligence lens
- `.guarani/philosophy/TSUN_CHA_PROTOCOL.md` — Dialectical debate protocol

Acknowledge: "Meta-prompt system loaded. [N] prompts, [N] triggers active."

## 4. Load Refinery (Intent Processing)

For MODERATE+ tasks, the Refinery activates automatically:

- `.guarani/refinery/classifier.md` — Intent classification (FEATURE/BUG/REFACTOR/KNOWLEDGE)
- `.guarani/refinery/interrogators/` — 4 specialized interrogators by type
- `.guarani/preprocessor.md` — Vague→explicit translation with persona simulation

These are loaded ON-DEMAND when the pipeline activates. No need to read all at start.

## 5. Rule Checksum Validation

> **CRITICAL:** LLMs suffer from probabilistic rule drift over long contexts.

Read `.windsurfrules` and confirm the active ruleset:
- Print: "Rules v[X.X.X] loaded. Mandamentos: [count]. Frozen zones: [count]."
- Verify `AGENTS.md` version matches `.windsurfrules` expectations.

## 6. System Map & Handoff

- Read `docs/SYSTEM_MAP.md` for full system overview
- Check latest handoff in `docs/_current_handoffs/` (most recent file)
- Recent commits: `git log --oneline -5`

## 7. Cost Monitor

| Resource | Warning | Critical |
|----------|---------|----------|
| Vercel usage | > 50% | > 75% (STOP) |
| Supabase DB | > 500 MB | > 2 GB (EMERGENCY) |

## 8. Codex Parallel Check (MANDATORY)

Before implementation work begins:

- Check `codex` availability and version
- Check pending cloud tasks with `codex cloud list`
- If `codex` is available, use it in a **parallel terminal/tab**, never in the main interactive chat terminal
- Preferred quick second opinion: `codex review --uncommitted`
- Preferred isolated analysis without writes: `codex exec -s read-only --output-last-message /tmp/codex-review.txt "review current diff"`
- Use `codex cloud exec` only when an environment is already configured, because current CLI requires `--env <ENV_ID>`

## 9. Output Briefing

Present to user:

- **Rules:** Version + mandamento count + orchestration status
- **Tasks:** P0 blockers → P1 sprint → P2 backlog (counts)
- **Handoff:** Last session summary (1-2 lines)
- **Recent commits:** Last 5 commits
- **Meta-prompts:** Count loaded + active triggers
- **Codex:** Availability + pending cloud tasks + chosen mode (cloud vs local read-only)
- **Orchestration:** "Pipeline active. Refinery ready. Gate threshold: 75."

---

## File Existence Checklist

All these MUST exist for the system to work:

| File | Purpose | Exists? |
|------|---------|---------|
| `AGENTS.md` | Project config | ✅ Required |
| `TASKS.md` | Task tracking | ✅ Required |
| `.windsurfrules` | Agent rules | ✅ Required |
| `.guarani/PREFERENCES.md` | Coding standards | ✅ Required |
| `.guarani/IDENTITY.md` | Agent identity | ✅ Required |
| `.guarani/orchestration/PIPELINE.md` | 7-phase protocol | ✅ Required |
| `.guarani/orchestration/GATES.md` | Quality gates | ✅ Required |
| `.guarani/orchestration/QUESTION_BANK.md` | Maieutic questions | ✅ Required |
| `.guarani/orchestration/DOMAIN_RULES.md` | Domain checklists | ✅ Required |
| `.guarani/refinery/classifier.md` | Intent classification | ✅ Required |
| `.guarani/refinery/interrogators/*.md` | Type-specific questions | ✅ Required |
| `.guarani/preprocessor.md` | Vague→explicit | ✅ Required |
| `.guarani/prompts/PROMPT_SYSTEM.md` | Meta-prompt index | ✅ Required |
| `.guarani/prompts/triggers.json` | Prompt trigger mappings | ✅ Required |
| `.guarani/philosophy/TSUN_CHA_PROTOCOL.md` | Debate protocol | ✅ Optional |
| `.guarani/MCP_ORCHESTRATION_GUIDE.md` | MCP decision tree | ✅ Optional |
| `.guarani/DESIGN_STANDARDS.md` | UI patterns | ✅ Optional |
| `docs/SYSTEM_MAP.md` | System overview | ✅ Required |

If any required file is missing, flag it immediately.

---

*v5.2 — Added meta-prompt system loading (step 3), prompt files to checklist, meta-prompt count in briefing*
