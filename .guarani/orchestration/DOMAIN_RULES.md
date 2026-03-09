# DOMAIN RULES — EGOS Inteligência

> **Version:** 1.0.0 | **Updated:** 2026-03-03

---

## Domain-Specific Checklists

### Before Adding a New Data Source
- [ ] Source is publicly available (government portal, open data)
- [ ] No PII beyond what's publicly disclosed
- [ ] ETL pipeline follows existing pattern in `etl/`
- [ ] Node labels and relationship types documented
- [ ] TASKS.md updated with new task
- [ ] `docs/data-sources.md` updated with source entry

### Before Adding a New Chat Tool
- [ ] Tool registered in `transparency_tools.py`
- [ ] Tool has rate limiting / timeout
- [ ] Tool has error handling with graceful fallback
- [ ] Tool returns structured data (not raw HTML)
- [ ] Tool documented in tools list

### Before Modifying Neo4j Schema
- [ ] New labels/types don't conflict with existing
- [ ] Indexes planned for new labels
- [ ] Migration path documented
- [ ] User approval obtained (FROZEN ZONE)

### Before Frontend Changes
- [ ] CSS Modules used (not inline styles)
- [ ] Responsive design verified
- [ ] Dark mode maintained
- [ ] No hardcoded strings (use i18n)

### Before Deploy to VPS
- [ ] `uv run ruff check src/` passes
- [ ] `uv run pytest -x` passes (or known failures documented)
- [ ] `npx tsc --noEmit` passes for frontend
- [ ] Git push → VPS git pull → docker compose restart/build

## Ethical Language Rules

> All AI outputs MUST use non-accusatory language.

| ❌ Forbidden | ✅ Required |
|-------------|------------|
| "is corrupt" | "has documented sanctions" |
| "stole money" | "received funds that show pattern X" |
| "criminal" | "subject of legal proceedings" |
| "guilty" | "sanctioned by [authority]" |
| "laundering" | "financial flow with characteristics of [pattern]" |

## Data Source Priority Matrix

When choosing which source to integrate next:
1. **Value for pattern detection** (cross-reference potential)
2. **Data quality** (structured > unstructured)
3. **Ingestion effort** (trivial CSV > complex API)
4. **Legal clarity** (explicitly public > ambiguous)
