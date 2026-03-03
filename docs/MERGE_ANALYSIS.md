# Análise Comparativa: Intelink vs EGOS Inteligência
## Proposta de Reformulação — Março 2026

---

## 1. INVENTÁRIO DE FEATURES (Frame-by-Frame)

### INTELINK (intelink.ia.br) — 63 frames analisados

| Feature | Status | Qualidade |
|---------|--------|-----------|
| **Busca Global (header)** | ✅ Funcional | ⭐⭐⭐⭐⭐ Excelente — Ctrl+K, últimos acessos, busca avançada |
| **Busca → Preview de Conexões** | ✅ Funcional | ⭐⭐⭐⭐⭐ Mostra conexões diretas NO DROPDOWN antes de abrir |
| **Entity Card (modal)** | ✅ Funcional | ⭐⭐⭐⭐⭐ Nome, vulgo, tags (Líder), dados pessoais colapsáveis |
| **Síntese da Entidade (AI)** | ✅ Funcional | ⭐⭐⭐⭐⭐ Texto corrido com destaque: "reside/frequenta X, veículo Y, comanda Z" |
| **Pessoas Relacionadas** | ✅ Funcional | ⭐⭐⭐⭐ Lista com tipo de relação (Comanda, Relacionamento amoroso) |
| **Locais** | ✅ Funcional | ⭐⭐⭐⭐ "Bar da Esquina" — Frequenta |
| **Veículos** | ✅ Funcional | ⭐⭐⭐⭐ "VW Gol G6 Preto" — Proprietário |
| **Conexões Indiretas (2º grau)** | ✅ Funcional | ⭐⭐⭐⭐⭐ Modal separado: "via Bar da Esquina → Pistola Glock, Endereço" |
| **Operações (cases)** | ✅ Funcional | ⭐⭐⭐⭐ Lista com entidades/vínculos/evidências/data. Status: Ativo |
| **Síntese da Investigação (AI)** | ✅ Funcional | ⭐⭐⭐⭐⭐ "4 pessoas, 11 vínculos, VITOR MENDES concentra 6 conexões" |
| **Análise Cross-Case** | ✅ Funcional | ⭐⭐⭐⭐ "Sem conflitos" ou "Aparece em 3 outras operações" |
| **Links Previstos (AI)** | ✅ Funcional | ⭐⭐⭐⭐⭐ "VW Gol → VITOR MENDES 93%", "AMANDA → Hospital 82%" (Adamic-Adar) |
| **Envolvidos** | ✅ Funcional | ⭐⭐⭐⭐ 4 Pessoas, 3 Veículos, 2 Armas, 1 Telefone categorizado |
| **Rede de Vínculos (mini-grafo)** | ✅ Funcional | ⭐⭐⭐ Pequeno, interativo, "Tela Cheia" disponível |
| **Índice Rho** | ✅ Funcional | ⭐⭐⭐⭐ Distribuído ↔ Centralizado, 10 entidades / 11 vínculos |
| **Evidências (upload)** | ✅ Funcional | ⭐⭐⭐ Upload de vídeo, fotos |
| **Linha do Tempo** | ✅ Funcional | ⭐⭐⭐ Histórico de eventos |
| **Relatórios (page)** | ✅ Funcional | ⭐⭐⭐⭐ Jornadas de Investigação + Documentos Extraídos + Gerar Relatório IA |
| **Chat IA** | ✅ Funcional | ⭐⭐⭐⭐ Floating widget, chat contextual |
| **Gestão (admin)** | ✅ Funcional | ⭐⭐⭐ Menu de gestão, perfil de usuário |
| **+ Adicionar (entidades)** | ✅ Funcional | ⭐⭐⭐⭐ Dropdown para adicionar pessoa, veículo, arma, etc |
| **Grafo (full page)** | ✅ Funcional | ⭐⭐⭐ Botão "Grafo" no header — visual mas não prioritário |

### EGOS INTELIGÊNCIA (inteligencia.egos.ia.br) — 27 frames analisados

| Feature | Status | Qualidade |
|---------|--------|-----------|
| **Landing Page** | ✅ Funcional | ⭐⭐⭐⭐⭐ Hero com search bar, suggestions, chat embedded, stats |
| **Search Bar (hero)** | ✅ Funcional (recém-criado) | ⭐⭐⭐⭐ 6 suggestion chips, inline results, "Aprofundar com IA" |
| **Chat IA (embedded)** | ✅ Funcional | ⭐⭐⭐⭐ Conversation persistence, auto-title, Redis-backed |
| **Stats Bar** | ✅ Funcional | ⭐⭐⭐⭐ 9M entidades, 35K conexões, 108 fontes |
| **Entity Analysis Page** | ✅ Funcional | ⭐⭐⭐ Graph explorer + Analysis + Details tabs |
| **Graph Explorer** | ✅ Funcional | ⭐⭐⭐⭐ Full interactive graph with entity type filters (30+ types) |
| **Exposure Index** | ✅ Funcional | ⭐⭐⭐⭐ Score 20, radar chart: conexões, fontes cruzadas, volume, etc |
| **Pattern Detection** | ✅ Funcional | ⭐⭐⭐ "Nenhum padrão encontrado" — precisa de mais conexões |
| **Entity Type Filters** | ✅ Funcional | ⭐⭐⭐⭐⭐ 30+ tipos: Pessoa, Empresa, Eleição, Sanção, Emenda, PEP, etc |
| **Relationship Types** | ✅ Funcional | ⭐⭐⭐⭐ 30+ tipos: HOLDING_DE, GASTOU_CARTAO, LICITOU, ADMINISTRA, etc |
| **Search (dedicated page)** | ✅ Funcional | ⭐⭐⭐ /app/search — graph search |
| **Pesquisas (investigations)** | ✅ Funcional | ⭐⭐⭐ Auth-gated research notebook |
| **Reports Showcase** | ✅ Funcional | ⭐⭐⭐ Patense investigation case |
| **Journey System** | ✅ Funcional | ⭐⭐⭐⭐ localStorage tracking, export JSON/Markdown |
| **Sources Section** | ✅ Funcional | ⭐⭐⭐⭐ 108 fontes documentadas na landing |
| **ETL Progress Widget** | ✅ Funcional | ⭐⭐⭐ Shows ETL status |
| **i18n (PT-BR + EN)** | ✅ Funcional | ⭐⭐⭐⭐ Full internationalization |
| **Public Mode** | ✅ Funcional | ⭐⭐⭐⭐ VITE_PUBLIC_MODE=true, search accessible without auth |

---

## 2. ANÁLISE COMPARATIVA HONESTA

### O que o INTELINK faz MELHOR:

1. **Busca Global com Preview de Conexões** — O dropdown de busca mostra conexões diretas (Comanda → MARCOS, Relacionamento → JULIANA) ANTES de abrir a entidade. Isso é KILLER FEATURE. O EGOS não tem nada parecido.

2. **Síntese da Entidade (texto corrido)** — "CARLOS HENRIQUE DA SILVA, líder, reside/frequenta Bar da Esquina, veículo VW Gol G6 Preto, comanda MARCOS VINICIUS SOUZA, relacionamento_amoroso JULIANA REIS SANTOS, comanda FELIPE AUGUSTO GOMES. Aparece em 3 outras operações." — MUITO mais útil que um grafo.

3. **Conexões Indiretas (2º grau)** — Modal mostrando "via Bar da Esquina → Pistola Glock 19 Gen5 (apreendida_em), Rua das Mangabeiras 450 (localizado_em)" e "via MARCOS VINICIUS SOUZA → VITOR MENDES DE OLIVEIRA (devedor), telefone (31) 98765-1234, Honda Civic Prata (utiliza)". Isso é inteligência REAL.

4. **Links Previstos (ML)** — Sugestão de conexões com score de probabilidade: "VW Gol G6 Preto ↔ VITOR MENDES 93% (Adamic-Adar)". Machine learning aplicado.

5. **Análise Cross-Case** — Detecta quando entidades aparecem em MÚLTIPLAS operações. "Aparece em 3 outras operações" é alerta automático.

6. **Entity Card como Modal** — Abre sobre a página, sem navegar. Quick view. UX muito melhor para fluxo investigativo.

7. **Tipos de relação semânticos** — "Comanda", "Relacionamento amoroso", "Frequenta", "Proprietário" — muito mais rico que apenas "CONNECTED_TO".

### O que o EGOS INTELIGÊNCIA faz MELHOR:

1. **Volume de dados REAL** — 9M entidades, 35K conexões, 108 fontes. Intelink tem dados de teste/demo com ~2000 entidades.

2. **Landing page pública** — Search-first, chat embedded, stats, open to anyone. Intelink é login-only.

3. **30+ tipos de entidade** — Pessoa, Empresa, Eleição, Contrato, Sanção, Emenda, Saúde, Financeiro, Embargo, Educação, Convênio, PEP, Offshore, CVM, etc. Intelink foca em policial (pessoa, veículo, arma, local, telefone).

4. **30+ tipos de relacionamento** — HOLDING_DE, GASTOU_CARTAO, VIAJOU, LICITOU, ADMINISTRA, GERE, PUBLICOU, MENCIONOU, DECLAROU_FINANCA, FORNECEU_LICITACAO, etc. Muito mais rico para investigação financeira/política.

5. **Chat com persistence** — Conversas salvas no Redis, histórico, multi-conversation.

6. **ETL pipeline real** — 9.1M nodes loaded, systemd service, production.

7. **Índice de Exposição (radar)** — Score visual multi-dimensional: conexões, fontes cruzadas, volume, financeiro, padrões, desvio da linha base.

8. **Graph Explorer avançado** — Interactive graph com filtros por tipo de entidade, profundidade, busca dentro do grafo.

9. **i18n** — PT-BR + EN. Intelink é PT-BR only.

### O que NENHUM dos dois faz bem:

1. **Onboarding para leigos** — Ambos assumem que o usuário sabe o que buscar
2. **Explicação dos dados** — De onde vem cada informação? Fonte? Data?
3. **Mobile** — Ambos são desktop-first
4. **Exportação** — Relatórios PDF/docx para compartilhar com não-usuários
5. **Alertas** — "Entidade X apareceu em nova fonte" — monitoramento contínuo

---

## 3. TRÊS ALTERNATIVAS DE MERGE

### ALTERNATIVA A: "Intelink como Base + Dados do EGOS"
**Conceito:** Usar a estrutura do Intelink (Next.js, Supabase) como base, migrar os dados do Neo4j do EGOS para o Supabase do Intelink.

| Prós | Contras |
|------|---------|
| UX do Intelink é superior para investigação | Perda do grafo Neo4j (30+ tipos de relação) |
| Entity card modal é excelente | Reescrever toda a API (FastAPI → Next.js API) |
| Conexões indiretas 2º grau prontas | Supabase não é ideal para graph traversal |
| Search com preview de conexões | Migração de 9M entidades é complexa |
| Cross-case analysis funcional | Perda do chat com persistence Redis |

**Esforço:** ~3-4 semanas. **Risco:** Alto (migração de dados).

### ALTERNATIVA B: "EGOS como Base + UX do Intelink"
**Conceito:** Manter o backend do EGOS (Neo4j + FastAPI + Redis) e reconstruir o frontend inspirado no Intelink: entity card modal, search com preview, síntese AI, conexões 2º grau.

| Prós | Contras |
|------|---------|
| Mantém Neo4j (ideal para grafos) | Frontend rewrite significativo |
| Mantém 9M entidades + 108 fontes | Intelink features como Links Previstos precisam ser reimplementados |
| Mantém ETL pipeline funcional | Sem operações/cases (precisa criar) |
| Mantém chat persistence Redis | Mais trabalho de frontend |
| Melhora UX sem perder dados | |
| API GraphQL do Neo4j é poderosa para conexões indiretas | |

**Esforço:** ~2-3 semanas. **Risco:** Médio (frontend work, mas backend estável).

### ALTERNATIVA C: "Nova Página Unificada — Best of Both"
**Conceito:** Criar uma TERCEIRA página (ou usar intelink.ia.br) como novo frontend unificado que consome AMBOS os backends: Neo4j/FastAPI do EGOS para dados públicos massivos + features UX do Intelink para investigação.

| Prós | Contras |
|------|---------|
| Best of both worlds | Mais complexo de manter (2 backends) |
| Não quebra nada existente | API gateway / proxy necessário |
| Pode testar com comunidade A/B | Duplicação potencial |
| Landing pública do EGOS + Operações do Intelink | |
| Grafo Neo4j para dados públicos + Supabase para operações | |
| Progressivo — pode migrar features incrementalmente | |

**Esforço:** ~1-2 semanas (v1 mínimo). **Risco:** Baixo (incremental).

---

## 4. MINHA RECOMENDAÇÃO (OPINIÃO HONESTA)

**Alternativa B é a melhor**, por estas razões:

1. **Neo4j é o ativo mais valioso** — 9M entidades, 108 fontes, ETL pipeline. Migrar isso para Supabase seria perder a maior vantagem do projeto.

2. **Conexões indiretas são CONSULTAS no Neo4j** — Um `MATCH (a)-[*2..3]-(b)` resolve em milissegundos o que levaria queries recursivas complexas no Supabase.

3. **O frontend é a parte mais fácil de mudar** — React components são substituíveis. O backend/dados NÃO.

4. **As killer features do Intelink são de FRONTEND** — Search preview, entity card modal, síntese AI, conexões 2º grau — tudo isso é UI + API calls. Não precisa do Supabase do Intelink.

5. **A landing page do EGOS já está melhor** — Search-first, pública, stats. O Intelink é login-only.

### Plano de execução sugerido (Alternativa B):

1. **Semana 1:** Entity Card Modal + Síntese AI (API endpoint `/api/v1/entity/:id/synthesis`)
2. **Semana 2:** Search com preview de conexões diretas (enriquecer resposta do search)
3. **Semana 3:** Conexões Indiretas 2º/3º grau (Neo4j query + UI modal)
4. **Semana 4:** Links Previstos (Adamic-Adar no Neo4j) + Cross-Case

Mas a decisão é sua e da comunidade. Sugiro criar um issue no GitHub com essas 3 opções e pedir feedback.

---

*Análise gerada em 03/03/2026 a partir de screencasts do Intelink (61s) e EGOS Inteligência (26s).*
