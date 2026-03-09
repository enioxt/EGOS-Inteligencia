# EGOS Meta-Prompt System v1.0

> **Centralizado em:** `.guarani/prompts/`
> **Filosofia:** Prompts são organismos vivos — evoluem com o projeto.
> **Atualizado:** 2026-03-06

---

## Arquitetura

```text
.guarani/prompts/
├── PROMPT_SYSTEM.md        # Este arquivo (índice + filosofia)
├── triggers.json           # Mapeamento máquina: situação → prompt
├── atoms/                  # Componentes atômicos reutilizáveis
│   └── personas.md         # Personas reutilizáveis
├── meta/                   # Meta-prompts completos (compostos de átomos)
│   ├── universal-strategist.md
│   ├── brainet-collective.md
│   └── ecosystem-audit.md
└── (philosophy/)           # Referência: ../.guarani/philosophy/
```

Domínio-específico (Intelink): `apps/intelink/lib/prompts/` — mantém registry.ts próprio.

---

## Catálogo de Meta-Prompts

| ID | Nome | Arquivo | Triggers | Apps |
|----|------|---------|----------|------|
| `strategy.universal` | Universal Strategist v4 | `meta/universal-strategist.md` | Decisão estratégica, negociação, conflito, investimento | Todos |
| `intelligence.brainet` | Brainet Collective | `meta/brainet-collective.md` | Brainstorm coletivo, dissolução de ego, inteligência de rede | Todos |
| `audit.ecosystem` | Ecosystem Audit | `docs/META_PROMPT_ECOSYSTEM_AUDIT.md` | Auditoria de repo, onboarding, análise cross-repo | egos-lab |
| `debate.tsun-cha` | Tsun-Cha Protocol | `philosophy/TSUN_CHA_PROTOCOL.md` | Questionar hipótese, verificar lógica, confronto dialético | Intelink, Agents |
| `extraction.police` | Document Extractor | `apps/intelink/lib/intelink/meta-prompts.ts` | Extração de BO, depoimento, CS | Intelink |
| `engineering.prompt` | Prompt Pipeline | `.agent/workflows/prompt.md` | Criando novos prompts | Todos |

---

## Anatomia de um Meta-Prompt (Padrão Atômico)

Todo meta-prompt EGOS é composto de 7 átomos:

1. **Persona** — Quem o AI é (backstory + credibilidade)
2. **Missão** — O que faz em 1 frase
3. **Regras** — Restrições absolutas (nunca quebre)
4. **Fases** — Estrutura interativa (cada fase com: objetivo + ações + critério de sucesso + gate)
5. **Matemática** — Fórmulas/frameworks quando aplicável (KaTeX, matrizes, etc.)
6. **Output** — Formato exato de saída
7. **Filosofia** — Lente filosófica (Oriental + Ocidental, sempre universal)

---

## Sistema de Triggers

Triggers automáticos ativam o prompt certo no contexto certo:

| Situação | Prompt Ativado | Gate |
|----------|----------------|------|
| "decisão estratégica", "negociação", "conflito" | `strategy.universal` | Perguntas Fase 1 |
| "brainstorm", "inteligência coletiva", "rede" | `intelligence.brainet` | Mapeamento de nós |
| "auditoria", "análise de repo", "diagnóstico" | `audit.ecosystem` | System Map |
| "questionar", "verificar", "debate", "lógica" | `debate.tsun-cha` | Afirmação + Evidência |
| "extrair", "BO", "ocorrência", "depoimento" | `extraction.police` | Documento anexado |
| "criar prompt", "system prompt", "instrução AI" | `engineering.prompt` | Architect phase |

---

## Princípios de Evolução

1. **Prompts evoluem com projetos** — a cada milestone, revise os prompts afetados
2. **Versione sempre** — YAML frontmatter com version semântica
3. **Átomos > Monólitos** — componentes pequenos compostos em prompts maiores
4. **Universal > Local** — priorize neutralidade cultural (Leste + Oeste)
5. **Teste antes de promover** — rode com adversarial input antes de marcar como stable
6. **Documente o porquê** — cada regra deve ter justificativa

---

## Referências Cruzadas

- **Intelink Prompt Registry:** `apps/intelink/lib/prompts/PROMPT_REGISTRY.md`
- **Intelink registry.ts:** `apps/intelink/lib/prompts/registry.ts`
- **Tsun-Cha Protocol:** `.guarani/philosophy/TSUN_CHA_PROTOCOL.md`
- **Prompt Workflow:** `.agent/workflows/prompt.md`

---

*"Prompts are the DNA of AI agents. Evolve them deliberately."*
