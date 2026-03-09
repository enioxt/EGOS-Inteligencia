---
description: "Finaliza sessão com handoff completo, disseminação e meta-prompt check"
---

# /end — Session Finalization (v5.0)

> **Sacred Code:** 000.111.369.963.1618
> **Works in:** ANY EGOS repo

## Phase 1: Collect Session Data // turbo

```bash
printf "═══════════════════════════════════════════════════════════\n"
printf "🔍 SESSION FINALIZATION\n"
printf "═══════════════════════════════════════════════════════════\n\n"

ROOT="$PWD"; CUR="$ROOT"
while [ "$CUR" != "/" ] && [ ! -e "$CUR/.git" ]; do CUR="$(dirname "$CUR")"; done
[ -e "$CUR/.git" ] && ROOT="$CUR"

REPO_NAME=$(basename "$ROOT")
printf "📂 Repo: %s\n" "$REPO_NAME"

LAST_COMMIT=$(git -C "$ROOT" log --oneline -1 2>/dev/null)
UNCOMMITTED=$(git -C "$ROOT" status --short 2>/dev/null | wc -l)
COMMITS_TODAY=$(git -C "$ROOT" log --oneline --since="6 hours ago" 2>/dev/null | wc -l)
printf "   Last commit: %s\n" "$LAST_COMMIT"
printf "   Uncommitted: %s files\n" "$UNCOMMITTED"
printf "   Session commits: %s\n\n" "$COMMITS_TODAY"

printf "📋 Recent commits this session:\n"
git -C "$ROOT" log --oneline --since="6 hours ago" 2>/dev/null || git -C "$ROOT" log --oneline -5
printf "\n"

if [ -f "$ROOT/TASKS.md" ]; then
  LINE_COUNT=$(wc -l < "$ROOT/TASKS.md")
  printf "📝 TASKS.md: %s lines\n\n" "$LINE_COUNT"
fi
```

## Phase 2: Agent Handoff Generation

```
⚠️ AI AGENT: Generate handoff document:

1. Create: docs/_current_handoffs/handoff_YYYY-MM-DD.md
2. Include:
   - What was accomplished (bullet list with file links)
   - What's in progress (with % completion)
   - What's blocked (reason + required action)
   - Next steps (ordered by priority)
   - Environment state (builds passing? tests green?)
3. Keep ACTIONABLE — next agent productive in < 2 minutes
```

## Phase 3: Update TASKS.md

```
⚠️ AI AGENT: Ensure TASKS.md reflects current state:
- Mark completed tasks with [x]
- Mark in-progress with [/]
- Add any new tasks discovered during session
- Update version + LAST SESSION line
```

## Phase 4: Disseminate Knowledge

```
⚠️ AI AGENT: Before ending, persist knowledge:

1. create_memory() — Session patterns, decisions, gotchas
2. Check .guarani/prompts/triggers.json — Did any meta-prompt trigger apply?
3. If architecture decisions were made → document in .guarani/
4. If new patterns learned → add to docs/knowledge/HARVEST.md
```

## Phase 5: Codex Cleanup

```bash
printf "🤖 Codex Check:\n"
if command -v codex &> /dev/null; then
  codex cloud list 2>/dev/null | head -10 || printf "   No cloud tasks\n"
else
  printf "   Codex not installed\n"
fi
printf "\n"
```

## Phase 6: Commit If Needed // turbo

```bash
ROOT="$PWD"; CUR="$ROOT"
while [ "$CUR" != "/" ] && [ ! -e "$CUR/.git" ]; do CUR="$(dirname "$CUR")"; done
[ -e "$CUR/.git" ] && ROOT="$CUR"

UNCOMMITTED=$(git -C "$ROOT" status --short 2>/dev/null | wc -l)
if [ "$UNCOMMITTED" -gt 0 ]; then
  printf "⚠️  %s uncommitted files — consider committing!\n" "$UNCOMMITTED"
  git -C "$ROOT" status --short
fi
```

## Phase 7: Session Summary

```
⚠️ AI AGENT: Display in chat:

SESSION SUMMARY
===============
Repo: [name]
Commits: [N] this session
Files changed: [list key files]
What was done: [2-4 lines]
Next steps: [P0/P1 priorities]
Meta-prompts used: [any triggered?]
Signed by: cascade-agent — [ISO8601]
```

---

_v5.0 — Unified from carteira-livre v4.1 + agent v3.1. Added meta-prompt dissemination check._
