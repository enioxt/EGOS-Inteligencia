#!/bin/bash
# ╔═══════════════════════════════════════════════════════════════╗
# ║  EGOS Inteligência — Pre-commit v2.0                         ║
# ║  Combined from: br-acc v1, egos-lab, carteira-livre v3       ║
# ║  NEW: Fork sync, PR awareness, issue sync, data accuracy     ║
# ║                                                               ║
# ║  Install: cp scripts/pre-commit-v2.sh .git/hooks/pre-commit  ║
# ║           chmod +x .git/hooks/pre-commit                      ║
# ╚═══════════════════════════════════════════════════════════════╝

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

echo -e "${CYAN}🔍 EGOS Pre-commit v2.0 — Running checks...${NC}"
echo "═══════════════════════════════════════════════════════════"

STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null)
if [ -z "$STAGED_FILES" ]; then
  echo -e "${GREEN}✅ No staged files. Skipping.${NC}"
  exit 0
fi

# ─── SECTION 1: SECURITY (BLOCKING) ──────────────────────────

echo -e "\n${CYAN}🔐 [1/8] Security Scan${NC}"

# 1a. Hardcoded secrets (from egos-lab patterns)
PATTERNS=(
  "sk-or-v1-"
  "ghp_[A-Za-z0-9]{36}"
  "github_pat_"
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
  "SUPABASE_DB_PASSWORD="
  "BEGIN RSA PRIVATE KEY"
  "BEGIN OPENSSH PRIVATE KEY"
)

for pattern in "${PATTERNS[@]}"; do
  MATCHES=$(echo "$STAGED_FILES" | xargs grep -lEn "$pattern" 2>/dev/null | grep -v "\.env\.example\|pre-commit\|SECURITY\.md\|\.gitignore" || true)
  if [ -n "$MATCHES" ]; then
    echo -e "${RED}   ❌ BLOCKED: Secret pattern found: ${pattern}${NC}"
    echo "   $MATCHES"
    ERRORS=$((ERRORS + 1))
  fi
done

# 1b. .env files staged
ENV_FILES=$(echo "$STAGED_FILES" | grep -E '^\.env$|^\.env\.local|^\.env\.development|^\.env\.production' || true)
if [ -n "$ENV_FILES" ]; then
  echo -e "${RED}   ❌ BLOCKED: .env file(s) staged!${NC}"
  ERRORS=$((ERRORS + 1))
fi

# 1c. Large files (>5MB)
for f in $STAGED_FILES; do
  if [ -f "$f" ]; then
    SIZE=$(stat -c%s "$f" 2>/dev/null || echo 0)
    if [ "$SIZE" -gt 5242880 ]; then
      echo -e "${RED}   ❌ BLOCKED: $f is $(($SIZE / 1048576))MB (>5MB)${NC}"
      ERRORS=$((ERRORS + 1))
    fi
  fi
done

# 1d. Personal data files (CV, resume, curriculum — NEVER in public repo)
PERSONAL_FILES=$(echo "$STAGED_FILES" | grep -iE 'cv|resume|curriculum|amplify|cover.letter|salary' || true)
if [ -n "$PERSONAL_FILES" ]; then
  echo -e "${RED}   ❌ BLOCKED: Personal file(s) detected — do NOT commit to public repo!${NC}"
  echo -e "${RED}   Move to ~/personal/ instead: $PERSONAL_FILES${NC}"
  ERRORS=$((ERRORS + 1))
fi

# 1e. Personal data in staged content (phone, CPF patterns)
for f in $STAGED_FILES; do
  if [ -f "$f" ]; then
    PII=$(grep -nE '\+55\s?[0-9]{2}\s?[0-9]{4,5}|[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}|enioxt@gmail' "$f" 2>/dev/null | head -3 || true)
    if [ -n "$PII" ]; then
      echo -e "${RED}   ❌ BLOCKED: PII found in $f — remove before committing${NC}"
      echo "   $PII"
      ERRORS=$((ERRORS + 1))
    fi
  fi
done

[ $ERRORS -eq 0 ] && echo -e "${GREEN}   ✅ No secrets, large files, or personal data${NC}"

# ─── SECTION 2: PYTHON CHECKS ────────────────────────────────

PY_FILES=$(echo "$STAGED_FILES" | grep '\.py$' || true)
if [ -n "$PY_FILES" ]; then
  echo -e "\n${CYAN}🐍 [2/8] Python Checks${NC}"
  
  for f in $PY_FILES; do
    python3 -c "import py_compile; py_compile.compile('$f', doraise=True)" 2>/dev/null || {
      echo -e "${RED}   ❌ Syntax error: $f${NC}"
      ERRORS=$((ERRORS + 1))
    }
  done
  
  # Ruff lint if available
  if command -v ruff &> /dev/null; then
    RUFF_OUT=$(ruff check $PY_FILES 2>/dev/null | head -5 || true)
    if [ -n "$RUFF_OUT" ]; then
      echo -e "${YELLOW}   ⚠️  Ruff warnings:${NC}"
      echo "$RUFF_OUT" | head -3
      WARNINGS=$((WARNINGS + 1))
    fi
  fi
  
  [ $ERRORS -eq 0 ] && echo -e "${GREEN}   ✅ Python OK${NC}"
else
  echo -e "\n${CYAN}🐍 [2/8] Python Checks — skipped (no .py files)${NC}"
fi

# ─── SECTION 3: FRONTEND CHECKS ──────────────────────────────

TSX_FILES=$(echo "$STAGED_FILES" | grep -E '\.(tsx?|jsx?)$' | grep -v 'node_modules\|\.d\.ts' || true)
if [ -n "$TSX_FILES" ]; then
  echo -e "\n${CYAN}⚛️  [3/8] Frontend Checks${NC}"
  
  # 3a. Unsafe array access on API data (from br-acc v1)
  UNSAFE=$(echo "$TSX_FILES" | xargs grep -nE '\.(entity_ids|sources|entities|annotations|tags|categories)\.(length|map|filter|forEach)' 2>/dev/null | grep -v '??' | grep -v '?\.' || true)
  if [ -n "$UNSAFE" ]; then
    echo -e "${YELLOW}   ⚠️  Unsafe array access (add ?? [] guard):${NC}"
    echo "$UNSAFE" | head -5
    WARNINGS=$((WARNINGS + 1))
  fi
  
  # 3b. console.log flood (from carteira-livre)
  for f in $TSX_FILES; do
    if [[ "$f" != *"test"* ]] && [[ "$f" != *"spec"* ]]; then
      COUNT=$(grep -c "console\.log" "$f" 2>/dev/null | tail -1 || echo "0")
      if [ "${COUNT:-0}" -gt 5 ] 2>/dev/null; then
        echo -e "${YELLOW}   ⚠️  $f: $COUNT console.log statements${NC}"
        WARNINGS=$((WARNINGS + 1))
      fi
    fi
  done
  
  # 3c. setInterval without cleanup (from carteira-livre)
  for f in $TSX_FILES; do
    if grep -q "setInterval" "$f" 2>/dev/null; then
      if ! grep -q "clearInterval" "$f" 2>/dev/null; then
        echo -e "${YELLOW}   ⚠️  $f: setInterval without clearInterval${NC}"
        WARNINGS=$((WARNINGS + 1))
      fi
    fi
  done
  
  [ $WARNINGS -eq 0 ] && echo -e "${GREEN}   ✅ Frontend OK${NC}"
else
  echo -e "\n${CYAN}⚛️  [3/8] Frontend Checks — skipped (no TSX/TS files)${NC}"
fi

# ─── SECTION 4: DATA ACCURACY CHECK (NEW) ────────────────────

echo -e "\n${CYAN}📊 [4/8] Data Accuracy Check${NC}"

# Check if any staged file contains potentially wrong numbers
DATA_FILES=$(echo "$STAGED_FILES" | grep -E '\.(html|md|tsx|ts|json)$' || true)
if [ -n "$DATA_FILES" ]; then
  # Check for 141M or 92M as current values (they are targets, not current)
  WRONG_NODES=$(echo "$DATA_FILES" | xargs grep -ln '141M.*no\|141M.*node\|141M.*nós' 2>/dev/null | grep -v 'meta\|target\|META\|TARGET\|goal\|GOAL' || true)
  if [ -n "$WRONG_NODES" ]; then
    echo -e "${YELLOW}   ⚠️  Files may claim 141M nodes as current (it's a target):${NC}"
    echo "   $WRONG_NODES"
    WARNINGS=$((WARNINGS + 1))
  fi
  
  # Check for MIT License (should be AGPL-3.0)
  WRONG_LICENSE=$(echo "$DATA_FILES" | xargs grep -ln 'MIT License\|Open Source (MIT)\|open source (MIT)' 2>/dev/null | grep -v 'node_modules\|package' || true)
  if [ -n "$WRONG_LICENSE" ]; then
    echo -e "${RED}   ❌ BLOCKED: Files reference MIT License (should be AGPL-3.0):${NC}"
    echo "   $WRONG_LICENSE"
    ERRORS=$((ERRORS + 1))
  fi
  
  [ $ERRORS -eq 0 ] && [ -z "$WRONG_NODES" ] && echo -e "${GREEN}   ✅ Data accuracy OK${NC}"
fi

# ─── SECTION 5: FORK & UPSTREAM SYNC (NEW) ───────────────────

echo -e "\n${CYAN}🔄 [5/8] Fork & Upstream Awareness${NC}"

# Check if upstream remote exists
if git remote get-url upstream &>/dev/null; then
  # Fetch upstream silently (non-blocking, best-effort)
  git fetch upstream --quiet 2>/dev/null || true
  
  BEHIND=$(git rev-list HEAD..upstream/main --count 2>/dev/null || echo "?")
  if [ "$BEHIND" != "?" ] && [ "$BEHIND" -gt 0 ]; then
    echo -e "${YELLOW}   ⚠️  Upstream (Bruno) has $BEHIND new commit(s). Consider: git merge upstream/main${NC}"
    WARNINGS=$((WARNINGS + 1))
  else
    echo -e "${GREEN}   ✅ Up to date with upstream${NC}"
  fi
else
  echo -e "${YELLOW}   ℹ️  No 'upstream' remote. Add with: git remote add upstream https://github.com/World-Open-Graph/br-acc.git${NC}"
fi

# ─── SECTION 6: PR & ISSUE AWARENESS (NEW) ───────────────────

echo -e "\n${CYAN}📋 [6/8] GitHub PR & Issue Sync${NC}"

if command -v gh &> /dev/null && gh auth status &>/dev/null 2>&1; then
  # Check open PRs
  PR_COUNT=$(gh pr list --state open --limit 10 --json number 2>/dev/null | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "?")
  if [ "$PR_COUNT" != "?" ] && [ "$PR_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}   ⚠️  $PR_COUNT open PR(s) — review before committing conflicting changes${NC}"
    gh pr list --state open --limit 5 --json number,title --template '{{range .}}   #{{.number}}: {{.title}}{{"\n"}}{{end}}' 2>/dev/null || true
  else
    echo -e "${GREEN}   ✅ No open PRs${NC}"
  fi
  
  # Check recently created issues (last 7 days)
  NEW_ISSUES=$(gh issue list --state open --limit 5 --json number,title,createdAt --template '{{range .}}{{.createdAt}}|{{.number}}|{{.title}}{{"\n"}}{{end}}' 2>/dev/null | head -3 || true)
  if [ -n "$NEW_ISSUES" ]; then
    echo -e "${CYAN}   📌 Recent open issues:${NC}"
    echo "$NEW_ISSUES" | while IFS='|' read -r date num title; do
      echo "      #$num: $title"
    done
  fi
else
  echo -e "${YELLOW}   ℹ️  gh CLI not authenticated. Run: gh auth login${NC}"
fi

# ─── SECTION 7: TASKS.md SYNC CHECK (NEW) ────────────────────

echo -e "\n${CYAN}📝 [7/8] TASKS.md Sync${NC}"

if echo "$STAGED_FILES" | grep -q "TASKS.md"; then
  echo -e "${GREEN}   ✅ TASKS.md is being updated in this commit${NC}"
else
  # Check if any feature files are staged but TASKS.md is not
  FEATURE_FILES=$(echo "$STAGED_FILES" | grep -E '(pages|routers|components|services)/' || true)
  if [ -n "$FEATURE_FILES" ]; then
    echo -e "${YELLOW}   ⚠️  Feature files changed but TASKS.md not updated:${NC}"
    echo "$FEATURE_FILES" | head -3 | while read f; do echo "      $f"; done
    echo "      Consider updating TASKS.md to reflect changes."
    WARNINGS=$((WARNINGS + 1))
  else
    echo -e "${GREEN}   ✅ No feature changes requiring TASKS.md update${NC}"
  fi
fi

# ─── SECTION 8: BACKEND-FRONTEND SYNC CHECK (NEW) ────────────

echo -e "\n${CYAN}🔗 [8/9] Backend-Frontend Sync${NC}"

API_FILES=$(echo "$STAGED_FILES" | grep -E '^api/src/bracc/(routers|services)/' || true)
FE_FILES=$(echo "$STAGED_FILES" | grep -E '^frontend/src/' || true)

if [ -n "$API_FILES" ] && [ -z "$FE_FILES" ]; then
  echo -e "${YELLOW}   ⚠️  Backend API changed but NO frontend files staged:${NC}"
  echo "$API_FILES" | head -5 | while read f; do echo "      $f"; done
  echo "      Consider: does the frontend need updating for this API change?"
  WARNINGS=$((WARNINGS + 1))
elif [ -n "$FE_FILES" ] && [ -z "$API_FILES" ]; then
  # Frontend-only changes are normal (UI tweaks), just info
  :
else
  echo -e "${GREEN}   ✅ Backend-frontend in sync (or no cross-cutting changes)${NC}"
fi

# ─── SECTION 9: CODEX CLI REMINDER ───────────────────────────

echo -e "\n${CYAN}🤖 [9/10] Codex CLI${NC}"
if command -v codex &>/dev/null; then
  PENDING=$(codex cloud list 2>/dev/null | grep -c "pending\|completed" || true)
  if [ "$PENDING" -gt 0 ]; then
    echo -e "${YELLOW}   ⚠️  $PENDING pending Codex cloud task(s) — review with: codex cloud list${NC}"
    WARNINGS=$((WARNINGS + 1))
  else
    echo -e "${GREEN}   ✅ No pending Codex tasks${NC}"
  fi
else
  echo -e "${GREEN}   ✅ Codex CLI not installed — skipping${NC}"
fi

# ─── SECTION 10: COMMIT MESSAGE FORMAT ───────────────────────

echo -e "\n${CYAN}📎 [10/10] Commit Convention${NC}"
echo -e "${GREEN}   ✅ Remember: feat:/fix:/chore:/docs: prefix${NC}"

# ─── SUMMARY ─────────────────────────────────────────────────

echo ""
echo "═══════════════════════════════════════════════════════════"

if [ $ERRORS -gt 0 ]; then
  echo -e "${RED}❌ $ERRORS error(s) — COMMIT BLOCKED${NC}"
  echo -e "   Fix the issues above before committing."
  echo -e "   Bypass (NOT recommended): git commit --no-verify"
  exit 1
elif [ $WARNINGS -gt 0 ]; then
  echo -e "${YELLOW}⚠️  $WARNINGS warning(s) — commit allowed, review recommended${NC}"
  exit 0
else
  echo -e "${GREEN}✅ All checks passed!${NC}"
  exit 0
fi
