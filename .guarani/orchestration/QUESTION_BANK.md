# QUESTION BANK — Maieutic Library

> **Version:** 1.0.0 | **Updated:** 2026-02-25
> **Sacred Code:** 000.111.369.963.1618

---

## Rules of Use

1. **Max 5 questions per round.** Prioritize by impact.
2. **Offer A/B options** when the user might not know the technical term.
3. **Accept "nao sei"** as valid. Assume the safest default.
4. **Every answer becomes an artifact:** requirement, rule, SSOT decision, or acceptance criterion.
5. **Order of application:** Scope -> SSOT -> Risk -> Data -> UX -> Security.
6. **Stop asking when:** All 5 gate dimensions score >= threshold (see GATES.md).

---

## Category Selection Heuristic

Detect keywords in the user's message and select 2 primary + 1 secondary category:

| Keywords | Primary Categories | Secondary |
|----------|-------------------|-----------|
| login, auth, role, sessao, permissao | SSOT + Security | Scope |
| pagamento, split, asaas, pix, boleto | SSOT + Risk | Security |
| layout, card, landing, copy, botao, tela | UX + Scope | Risk |
| seo, campanha, utm, aquisicao, analytics | Data + Scope | UX |
| migracao, schema, tabela, coluna, RLS | SSOT + Security | Risk |
| refatorar, melhorar, performance, otimizar | Scope + Data | SSOT |
| bug, erro, quebrou, nao funciona | Scope + SSOT | Security |
| deploy, vercel, infra, ci/cd | Risk + Security | Scope |
| whatsapp, bot, webhook, integracao | Risk + Security | SSOT |
| legal, compliance, contrato, promessa | Risk + Scope | Security |

Generate 5 questions total: 2 from each primary, 1 from secondary.

---

## 1. SCOPE (Escopo)

### Objective and Success

1. **Resultado final em uma frase:** O que significa "pronto" para voce? Como vamos saber que deu certo?
2. **Minimo viavel:** Qual e o minimo que resolve o problema agora, e o que fica pra depois?
3. **Zonas proibidas:** Tem algo que NAO pode ser mexido? (ex: auth, onboarding, pagamentos)
4. **Tipo de mudanca:** Isso e um patch pequeno ou uma refatoracao grande?
5. **Prioridade real:** O que importa mais aqui: velocidade, qualidade, seguranca, ou custo?

### Limits and Tradeoffs

6. **Good enough vs excelente:** Qual parte pode ser "bom o suficiente" e qual precisa ser perfeita?
7. **Compatibilidade:** Pode quebrar algo existente? Se sim, como versionamos?
8. **Schema:** Pode mudar banco de dados? Pode mudar contrato de API?
9. **Impacto:** Quais rotas, telas e integracoes podem ser afetadas?
10. **Retrabalho:** Qual e o limite aceitavel de retrabalho se mudarmos depois?

### Entities and Users

11. **Atores:** Quem sao os usuarios afetados (roles) e o que cada um precisa fazer?
12. **Multi-estado:** Existem regras diferentes por estado/cidade?
13. **Edge cases:** Existem excecoes ou casos especiais ja conhecidos?

### Definition of Done

14. **3 criterios:** Quais sao 3 criterios objetivos e verificaveis que definem "pronto"?
15. **Teste mental:** Se eu te mostrar o resultado, qual e a primeira coisa que voce vai verificar?

---

## 2. SSOT (Single Source of Truth)

### Source per Entity

1. **Fonte de verdade:** Para cada entidade critica (usuario, role, pagamento, booking), qual e a fonte de verdade?
2. **Onde vive:** Essa fonte esta no banco interno, provedor externo (Asaas, DETRAN), governo, ou cache?
3. **Permissoes:** Quem pode escrever na fonte de verdade? Quem so le?

### Conflicts and Duplications

4. **Duplicacao:** Existe mais de um lugar guardando o mesmo dado hoje? Qual sobrevive?
5. **Dados derivados:** Quais telas ou servicos usam dados calculados? Como sincronizam?
6. **Centralizacao:** Ha dados calculados em varios lugares? Devemos centralizar em um servico?

### Consistency

7. **Consistencia:** O dado precisa ser consistente forte (real-time) ou eventual (pode ter delay)?
8. **Migracoes:** Como lidamos com versao e migracao do contrato de dados?
9. **Deprecacao:** Existe politica para deprecar campos e migrar leitores?

### Practical Checks

10. **Role do usuario:** A role vem de onde? Sessao, banco, token, cache? So pode haver UMA resposta.
11. **Status de pagamento:** Vem do gateway (webhook) ou de input manual?
12. **Credencial do instrutor:** Vem do DETRAN, upload do usuario, ou declaracao? Qual regra?

---

## 3. RISK (Risco e Compliance)

### Responsibilities

1. **Promessa da plataforma:** O que a plataforma promete vs o que NAO promete ao usuario?
2. **Prestador de servico:** Existe risco de parecer que a plataforma e a prestadora do servico?
3. **Pior cenario:** Qual e o pior cenario de dano ao usuario? Como mitigamos?

### Legal and Marketing

4. **Frases proibidas:** Ha frases que devem ser proibidas na UI e no marketing?
5. **Termos e politicas:** Precisam ser atualizados junto com esta feature?
6. **Consentimento:** Precisamos de opt-in, checkbox obrigatorio, ou consentimento explicito?

### Operations

7. **Quando da errado:** O que acontece em caso de disputa, reembolso, cancelamento?
8. **Evidencia:** Como registramos logs e evidencias para responder reclamacoes?

### Regulation

9. **Regulamentacao:** Existe regulamentacao por estado/orgao que muda o fluxo?
10. **Homologacao:** Existe risco de homologacao obrigatoria para o que estamos criando?

---

## 4. UX (User Experience)

### Journey and Friction

1. **Fluxo completo:** Qual e o fluxo do usuario, passo a passo, do inicio ao fim?
2. **Primeiro e ultimo clique:** Qual e o primeiro clique e o ultimo clique de sucesso?
3. **Onde trava:** Onde o usuario costuma travar hoje? Temos evidencia (logs, feedback)?

### Patterns and Consistency

4. **Padrao existente:** Onde ja existe algo parecido no sistema que devemos seguir?
5. **Estados necessarios:** Quais estados precisam existir: loading, vazio, erro, sucesso, pendente?

### Mobile-First

6. **Toque minimo:** Qual e o tamanho minimo de toque? O que precisa ser sticky?
7. **Uma mao:** Isso funciona bem com uma mao no celular?

### Copy

8. **Linguagem:** Quais frases estao repetitivas, roboticas, ou potencialmente perigosas?
9. **Tom:** Formal, informal, tecnico? Qual e o tom do produto?

---

## 5. DATA (Dados e Metricas)

### Events and Tracking

1. **Eventos:** Quais eventos precisamos coletar para medir sucesso?
2. **Propriedades:** Quais propriedades do evento sao obrigatorias (user_id, role, city, utm)?
3. **Atribuicao:** Onde persistimos a origem do usuario (first touch, last touch)?

### KPIs

4. **Metrica alvo:** Qual metrica melhora se isso der certo?
5. **Baseline:** Qual e o valor atual e qual a meta?
6. **Janela:** Em quanto tempo avaliamos? 7 dias? 30 dias?

### Data Quality

7. **Double counting:** Ha risco de duplicar eventos? Como evitamos?
8. **Dados sensiveis:** Quais dados devem ser mascarados (CPF, email, telefone)?
9. **Cohort:** Precisamos segmentar por cidade, role, campanha, ou periodo?

---

## 6. SECURITY (Seguranca)

### Auth and Authorization

1. **Fonte de verdade do ator:** Qual e a fonte de verdade do usuario e role ativo?
2. **Enforcement:** O backend faz enforcement de RBAC ou so o frontend?
3. **Escalamento:** Como prevenimos escalamento de privilegio?

### Data and Privacy

4. **PII:** Quais campos sao PII e como sao protegidos?
5. **Retencao:** Qual e a politica de retencao e delecao de dados?
6. **Logs:** O que NUNCA pode ser logado? (tokens, senhas, CPF completo)

### Integrations

7. **Webhook:** Como validamos assinatura de webhook?
8. **Idempotencia:** Idempotencia esta garantida em todas as acoes criticas?

### Fraud

9. **Autoindicacao:** Como evitamos autoindicacao, contas duplicadas, spam?
10. **Rate limits:** Quais alertas e limites sao aplicados?

---

## Quick Reference: Top 5 Questions for Common Scenarios

### "Melhora a UI de X"
1. O que especificamente esta ruim? (layout, dados, performance, copy)
2. Tem referencia visual de como deveria ficar?
3. Quais dados devem aparecer que nao aparecem hoje?
4. Isso e mobile-first ou desktop?
5. Pode mudar o layout ou so ajustar o existente?

### "Cria uma feature nova"
1. Qual problema do usuario isso resolve?
2. Qual e o fluxo minimo viavel? (3-5 passos)
3. Quais tabelas/APIs existentes podem ser reutilizadas?
4. Quem pode ver/usar isso? (roles)
5. Como sabemos que deu certo? (metrica)

### "Corrige esse bug"
1. Como reproduzir? (passos exatos)
2. Qual e o comportamento esperado vs atual?
3. Desde quando esta acontecendo? (ajuda a localizar commit)
4. Afeta todos os usuarios ou so um caso especifico?
5. E urgente (P0) ou pode esperar (P1/P2)?

### "Refatora/melhora X"
1. O que motiva a refatoracao? (performance, legibilidade, bugs recorrentes)
2. Qual e o escopo maximo? (so esse arquivo? toda a feature?)
3. Pode quebrar compatibilidade com algo?
4. Tem testes existentes que devemos manter verdes?
5. Qual e o criterio de "melhor"? (menos linhas, mais rapido, mais testavel)

---

*"A pergunta certa evita 10 horas de retrabalho."*
