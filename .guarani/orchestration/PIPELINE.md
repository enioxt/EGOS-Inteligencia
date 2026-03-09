# ORCHESTRATION PIPELINE — Agent Cognitive Protocol

> **Version:** 1.0.0 | **Updated:** 2026-02-25
> **Sacred Code:** 000.111.369.963.1618

---

## Purpose

This is the **master protocol** for how the agent processes every user message.
It chains together existing tools (NEXUS_ZERO, Evaluator, Sequential Thinking, MCPs)
into a single, enforceable pipeline that prevents premature execution.

**Core principle:** The quality of output is directly proportional to the quality of input processing.

---

## The 7 Phases

```
USER MESSAGE
     |
     v
[1. INTAKE] -----> Parse intent, classify, identify entities
     |
     v
[2. CHALLENGE] --> Maieutic questioning, detect contradictions, translate vague terms
     |
     v
[3. PLAN] -------> Structure phases, estimate risk, define acceptance criteria
     |
     v
[4. GATE] -------> Score readiness. BLOCK if score < threshold
     |              |
     |         (loop back to 2 or 3 if gate fails)
     v
[5. EXECUTE] ----> Incremental patches, document changes
     |
     v
[6. VERIFY] -----> Tests, evidence, checklist
     |
     v
[7. LEARN] ------> Update knowledge, disseminate, improve meta-prompts
```

---

## Phase 1: INTAKE (Every Message)

**Time:** 10-30 seconds | **Tools:** Refinery Classifier (`.guarani/refinery/classifier.md`)

Parse the user's message and produce a structured understanding.
For MODERATE+ tasks, use the **Refinery Classifier** to detect intent type with confidence scoring.

```markdown
INTAKE:
- Intent: [What the user wants in one sentence]
- Type: [FEATURE | BUG | REFACTOR | QUESTION | CONFIG | DEPLOY]
- Confidence: [0.0-1.0 — how certain are we about the type]
- Complexity: [TRIVIAL | SIMPLE | MODERATE | COMPLEX | CRITICAL]
- Entities: [Which tables, APIs, pages, services are affected]
- Constraints: [What must NOT change, frozen zones, deadlines]
- Risks: [What could go wrong]
```

### Intent Classification (Refinery)

The Refinery Classifier uses heuristics to detect intent type:
- **FEATURE:** "criar", "fazer", "adicionar", "quero" → load `interrogators/feature.md`
- **BUG:** "não funciona", "erro", "quebrou" → load `interrogators/bug.md`
- **REFACTOR:** "melhorar", "otimizar", "limpar" → load `interrogators/refactor.md`
- **QUESTION:** "como funciona", "o que é", "explica" → load `interrogators/knowledge.md`

If confidence < 0.7, ask the user: "Você quer criar algo novo, corrigir algo, melhorar algo, ou entender algo?"

### Complexity Classification

| Level | Examples | Pipeline Depth |
|-------|----------|----------------|
| **TRIVIAL** | Fix typo, adjust spacing, add import | Skip to Phase 5 |
| **SIMPLE** | Add field to display, fix known bug | Phases 1,3,5,6 |
| **MODERATE** | New component, API route, refactor section | Phases 1-6 |
| **COMPLEX** | New feature, payment flow, auth change | ALL phases, Sequential Thinking |
| **CRITICAL** | Schema migration, security fix, legal change | ALL phases, min 7 thoughts, explicit approval |

### When to Skip Phases

- **TRIVIAL:** Go straight to execute. No questions needed.
- **SIMPLE:** Quick plan, execute, verify. No maieutic needed.
- **MODERATE+:** Full pipeline. Questions mandatory.

---

## Phase 2: CHALLENGE (Maieutic Questioning)

**Time:** 1-5 minutes | **Tools:** Refinery Interrogators + Question Bank + Preprocessor

The agent MUST NOT simply accept what the user says. Instead:

### Step 1: Activate the right Interrogator (by intent type from Phase 1)

| Intent Type | Interrogator | Key Questions |
|-------------|-------------|---------------|
| FEATURE | `.guarani/refinery/interrogators/feature.md` | Core Entity → Success Metric → First User |
| BUG | `.guarani/refinery/interrogators/bug.md` | Symptom → Reproduction → Context → Diagnosis |
| REFACTOR | `.guarani/refinery/interrogators/refactor.md` | Target → Objective → Constraints (validate it's not a bug!) |
| QUESTION | `.guarani/refinery/interrogators/knowledge.md` | Domain → Depth → Context (may skip to answer directly) |

### Step 2: Apply domain-specific questions (from Question Bank)

Select 2 primary + 1 secondary category from `.guarani/orchestration/QUESTION_BANK.md`:
- Keywords "login, auth, role" -> SSOT + Security questions
- Keywords "pagamento, split, asaas" -> SSOT + Risk + Security questions
- Keywords "layout, card, landing" -> UX + Risk questions
- Keywords "migração, schema" -> SSOT + Security + Risk questions

### Step 3: Detect vague terms (Preprocessor)

If input is vague (< 50 chars, contains "rapidinho", "simples", "você acha"):
- Load `.guarani/preprocessor.md`
- Simulate perspectives (Engineer, Security, PM, UX, QA)
- Translate vague → explicit before proceeding

### Step 4: Detect contradictions (Tsun-Cha)

For COMPLEX/CRITICAL tasks, apply debate posture (`.guarani/philosophy/TSUN_CHA_PROTOCOL.md`):
- Does this conflict with frozen zones?
- Does this duplicate something that exists?
- Does this break an existing flow?
- If the user proposes something risky, **defend the system logic** — don't just agree

### Rules

- **Max 5 questions per round**, prioritized by impact
- Use A/B options when possible (reduces friction)
- Accept "nao sei" as valid answer (assume safest default)
- Every answer must become a requirement or decision

### When to Challenge vs Accept

| Signal | Action |
|--------|--------|
| User gives specific file paths and clear criteria | Accept, move to Plan |
| User gives vague direction ("melhora isso") | Challenge with questions |
| User references a task from TASKS.md | Accept scope, verify details |
| User asks for something in a frozen zone | STOP, confirm explicitly |
| User asks for something that contradicts rules | Challenge, explain the conflict |

---

## Phase 3: PLAN

**Time:** 1-5 minutes | **Tools:** Sequential Thinking MCP, NEXUS_ZERO

### For MODERATE+ tasks, produce:

```markdown
PLAN:
## Objective
[One sentence]

## Phases
### Phase 1: [Minimum that resolves core risk]
- Task 1.1: [description] -> [file(s)]
- Task 1.2: [description] -> [file(s)]
- Acceptance: [measurable criterion]

### Phase 2: [Enhancement]
- Task 2.1: ...
- Acceptance: ...

## SSOT
- Source of truth for [entity]: [where it lives]

## Risks
- Risk 1: [description] -> Mitigation: [how]

## Out of Scope
- [What we are NOT doing]

## Tests
- [ ] [Test 1]
- [ ] [Test 2]
```

### Sequential Thinking Requirements

| Complexity | Min Thoughts |
|------------|-------------|
| MODERATE | 3 |
| COMPLEX | 5 |
| CRITICAL | 7 |

---

## Phase 4: GATE (Quality Score)

**Time:** 30 seconds | **Tools:** Gates spec (`.guarani/orchestration/GATES.md`)

Calculate readiness score across 5 dimensions:

| Dimension | Weight | Threshold |
|-----------|--------|-----------|
| **Clarity** | 25% | >= 80 |
| **SSOT** | 20% | >= 70 |
| **Risk Coverage** | 20% | >= 70 |
| **Scope Control** | 20% | >= 80 |
| **Testability** | 15% | >= 60 |

### Gate Decision

```
Weighted Score >= 75 -> PROCEED to Execute
Weighted Score 60-74 -> WARN, ask user to confirm
Weighted Score < 60  -> BLOCK, return to Challenge or Plan
```

### Gate Bypasses (Automatic)

- TRIVIAL tasks: Gate auto-passes
- SIMPLE tasks: Only Clarity and Scope checked
- User explicitly says "just do it" after seeing the score: Proceed with warning logged

---

## Phase 5: EXECUTE

**Time:** Variable | **Tools:** Edit tools, MCP tools

Rules during execution:
1. **Incremental patches** — Small, reviewable changes
2. **No scope creep** — Only do what the plan says
3. **Document as you go** — Update TASKS.md, add comments where needed
4. **Ask before creating** new pages, features, or integrations
5. **Follow existing patterns** in the codebase

### MCP Usage Order
1. Check if an MCP tool can do it (MCP-FIRST principle)
2. If not, check if a workflow exists
3. If not, implement manually following project conventions

---

## Phase 6: VERIFY

**Time:** 1-3 minutes | **Tools:** tsc, tests, manual checklist

For every change:
1. **Type check:** `npx tsc --noEmit --pretty false 2>&1 | grep "error TS" | head -20`
2. **Visual check** (if UI changed): Describe what changed, ask user to verify
3. **Integration check** (if API/DB changed): Test the endpoint
4. **Regression check:** Did anything else break?

### Verification by Complexity

| Level | Verification Required |
|-------|----------------------|
| TRIVIAL | Type check only |
| SIMPLE | Type check + visual/functional |
| MODERATE | Type check + test + commit |
| COMPLEX | All above + manual QA checklist |
| CRITICAL | All above + user sign-off before push |

---

## Phase 7: LEARN

**Time:** 1-2 minutes | **Tools:** Memory MCP, Knowledge Base

After completing work:
1. **What went well?** Patterns to reuse
2. **What caused confusion?** Improve question bank or rules
3. **New knowledge?** Disseminate to Memory MCP
4. **Rules update needed?** Propose updates to `.windsurfrules` or domain rules

### Dissemination Triggers
- New architectural pattern discovered -> `mcp8_create_entities`
- New failure mode discovered -> Update DOMAIN_RULES.md
- User preference learned -> `create_memory`
- Reusable solution found -> `mcp2_save_web_knowledge`

---

## Agent Response Format

For MODERATE+ tasks, every first response MUST follow this structure:

```markdown
## Entendimento
[What I understood from your message]

## O que falta para executar
[Missing information, decisions needed]

## Perguntas (max 5)
1. [Question with A/B options if possible]
2. ...

## Plano Inicial
[Tasks in order]

## Score: X/100
[Which dimensions are low and why]

## Proximo Passo
[What happens next]
```

For TRIVIAL/SIMPLE tasks, skip the format and just do the work.

---

## Integration Map

| Phase | Tool | How It's Used |
|-------|------|---------------|
| Intake | Refinery Classifier (`.guarani/refinery/classifier.md`) | Classify intent type with confidence |
| Intake | Preprocessor (`.guarani/preprocessor.md`) | Translate vague input to explicit specs |
| Challenge | Refinery Interrogators (`.guarani/refinery/interrogators/`) | Type-specific questions (bug/feature/refactor/knowledge) |
| Challenge | Question Bank (`.guarani/orchestration/QUESTION_BANK.md`) | Domain-specific questions (SSOT/Risk/UX/Security) |
| Challenge | Tsun-Cha Protocol (`.guarani/philosophy/TSUN_CHA_PROTOCOL.md`) | Logical debate for COMPLEX/CRITICAL tasks |
| Plan | Sequential Thinking MCP | Structure thoughts |
| Plan | NEXUS_ZERO | Compile precise instructions |
| Gate | `GATES.md` | Score and decide |
| Gate | Evaluator Nexus Skill | 10-dimension QA if needed |
| Execute | Edit tools, MCP tools | Implement changes |
| Verify | tsc, tests | Validate |
| Learn | Memory MCP, Knowledge Base | Persist knowledge |

---

*"Slow is smooth, smooth is fast. Process before code."*
