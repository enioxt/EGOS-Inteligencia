# HARVEST.md — Pattern Library (EGOS Ecosystem)

> **Purpose:** Reusable patterns discovered and validated in EGOS
> **Updated:** 2026-03-27
> **Patterns:** 10 (Timeline system added)

---

## Pattern #1: Supabase RLS + JSONB for Extensibility

**Discovery:** Carteira Livre + br-acc
**Use:** All authentication + multi-tenant systems

When: You need row-level security + flexible metadata
How: RLS policies + JSONB columns for vendor-specific data
Example: `transparency_reports.metadata JSONB`

---

## Pattern #2: Event-Driven Telemetry (Event Bus)

**Discovery:** egos agents (event-bus.ts)
**Use:** Agent orchestration, cross-system messaging

When: Multiple agents need to coordinate
How: Pub/sub with structured events, telemetry logging
Example: `event-bus.ts` in egos/agents/runtime/

---

## Pattern #3: Drift Detection via SSOT Comparison

**Discovery:** AGENT-AUDIT-003 (agent consolidation)
**Use:** Governance, dependency management

When: Code diverges from documentation
How: Compare SSOT (AGENTS.md, TASKS.md) with implementation
Example: drift_sentinel agent (EGOS-106)

---

## Pattern #4: Multi-LLM Routing + Fallback

**Discovery:** llm-orchestrator.ts (shared package)
**Use:** All agents, API routes that call LLMs

When: Need resilience + cost optimization
How: Router selects Claude/Groq/Alibaba based on task + quota
Example: `packages/shared/src/llm-orchestrator.ts`

---

## Pattern #5: Execution Telemetry Logging

**Discovery:** agent-chain-runner.ts
**Use:** Track all agent executions

When: Need observability of long-running jobs
How: Log to events.jsonl with duration, findings, errors
Example: `docs/agent-tests/20260327_*.md`

---

## Pattern #6: Vault Pattern for Credentials

**Discovery:** CREDENTIALS_POLICY.md
**Use:** Never commit secrets

When: Storing API keys, tokens, passwords
How: `~/.egos/secrets.env` (gitignored) + systemd env + pre-commit gitleaks
Example: X.com OAuth keys, OpenRouter API keys

---

## Pattern #7: Git Hooks for Pre-commit Validation

**Discovery:** Pre-push hooks (br-acc, egos, egos-lab)
**Use:** Block bad code before it reaches main

When: Want guaranteed quality on main
How: Pre-commit: gitleaks, tsc, prettier | Pre-push: registry lint
Example: `.git/hooks/pre-push` (POSIX sh compat fixed)

---

## Pattern #8: Documentation-Driven Development

**Discovery:** PRD pattern (TRANSPARENCY_RADICAL_PRD.md)
**Use:** Large features with multiple phases

When: Need to coordinate work across teams/repos
How: Write PRD first, then implement by phases
Example: `TRANSPARENCY_RADICAL_PRD.md` (40h total, 5 phases)

---

## Pattern #9: Shared Types + Interfaces (API Contracts)

**Discovery:** packages/shared (mycelium, api-registry)
**Use:** Cross-repo API compatibility

When: Multiple services need same data structures
How: Export types from shared package
Example: `ReportTimelineItem`, `MetricSnapshot` interfaces

---

## Pattern #10: Admin Transparency Timeline ⭐ NEW

**Discovery:** TRANSPARENCY_RADICAL initiative
**Use:** Unified visibility of all system events

When: Need to see what your system is doing in real-time
How: Centralized Supabase tables + shared React components + auto-refresh

**Implementation:**
```
Supabase Schema:
- transparency_reports (events timeline)
- transparency_metrics (KPIs, time-series)
- transparency_logs (structured logging)
- transparency_alerts (real-time notifications)

React Components:
- <TransparencyTimeline /> — Event list with filters
- <TimelineFilterBar /> — System/agent/status filters
- <TimelineStatusBadge /> — Visual status indicators

Hook:
- useRealtimeTelemetry() — Auto-refresh, aggregation

API Routes:
- GET /api/admin/transparency/reports
- GET /api/admin/transparency/telemetry
- SSE /api/admin/transparency/logs/stream
- GET /api/admin/transparency/alerts
```

**Files Created (2026-03-27):**
- `/home/enio/forja/supabase/migrations/20260327120000_transparency_system.sql` (Forja-specific)
- `/home/enio/egos/apps/commons/supabase/migrations/20260327130000_transparency_system_shared.sql` (shared)
- `/home/enio/forja/src/components/admin/transparency/TransparencyTimeline.tsx`
- `/home/enio/forja/src/components/admin/transparency/TimelineFilterBar.tsx`
- `/home/enio/forja/src/hooks/useRealtimeTelemetry.ts`
- `/home/enio/egos/docs/TIMELINE_SYSTEM_IMPLEMENTATION_PLAN.md` (architecture)

**Phases:**
1. ✅ PHASE 1: Foundation (Supabase + Components)
2. ⏳ PHASE 2: Forja implementation (page + API routes)
3. ⏳ PHASE 3: 852 + Carteira Libre refinement
4. ⏳ PHASE 4: egos-lab, br-acc dissemination
5. ⏳ PHASE 5: Global `/disseminate`

**Value:** Transparent operations ("não seremos uma caixa preta")

---

## Future Patterns (TBD)

- Pattern #11: Chaos Engineering + Graceful Degradation
- Pattern #12: Cross-repo Dependency Graph Visualization
- Pattern #13: Autonomous Self-Healing via Drift Sentinel

