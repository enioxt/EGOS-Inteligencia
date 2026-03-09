# EGOS Inteligência — Meta Prompt v2.0

> **O que é isso?** Um prompt poderoso que você copia e cola em qualquer IA capaz de ler repositórios GitHub. A IA fará uma análise completa do projeto e mostrará exatamente como você pode contribuir — mesmo sem saber programar.
>
> **Versão:** 2.0 | **Atualizado:** 2026-03-03

---

## 🛠 Onde Usar Este Prompt

### IAs com Acesso a Repositórios (Cole o prompt + o link do repo)

| Ferramenta | URL | Custo | Melhor Para |
|------------|-----|-------|-------------|
| **Google AI Studio** | [aistudio.google.com](https://aistudio.google.com/) | Grátis | Análise profunda com Gemini 2.5 Pro (melhor modelo grátis) |
| **ChatGPT + Codex** | [chatgpt.com/codex](https://chatgpt.com/codex) | Grátis/Pro | Leitura de repo + geração de código |
| **Grok** | [grok.com](https://grok.com/) | Grátis | Análise rápida, acesso real-time |
| **Gemini** | [gemini.google.com](https://gemini.google.com/app) | Grátis | Análise conversacional do repo |

### IDEs com IA Integrada (Clone o repo + abra na IDE)

| IDE | URL | Custo | Diferencial |
|-----|-----|-------|-------------|
| **Google Antigravity** | [idx.google.com](https://idx.google.com/) | **100% Grátis** | Melhores modelos (Gemini 2.5 Pro) sem pagar nada |
| **Windsurf IDE** | [windsurf.com](https://windsurf.com/) | Grátis/Pro | Cascade AI lê todo o projeto, executa comandos |
| **Cursor** | [cursor.com](https://cursor.com/) | Grátis/Pro | Chat com codebase, edição assistida |
| **Claude Code** | Terminal | Pro ($20/mês) | Agente autônomo que navega e edita o repo |

### Como Usar

1. **Copie o prompt completo** (seção abaixo)
2. **Cole na ferramenta escolhida**
3. **Adicione o link do repositório:** `https://github.com/enioxt/EGOS-Inteligencia`
4. **Envie e aguarde a análise** (~2-5 minutos)
5. **Explore as áreas que te interessam** e veja como contribuir

> **Dica:** No Google AI Studio, use o modelo **Gemini 2.5 Pro** e cole o link do GitHub diretamente. Ele lerá todos os arquivos automaticamente.

---

## 📋 O PROMPT (copie tudo abaixo)

---

```
Você é "EGOS Analyst Pro v2" — um Arquiteto de Software Senior especializado em Graph Databases (Neo4j), OSINT, Compliance LGPD, Python/FastAPI, React 18, e plataformas de transparência pública.

Sua missão é fazer uma ANÁLISE COMPLETA, exaustiva e DIDÁTICA do repositório abaixo, dividida em áreas claras para que qualquer pessoa — técnica ou não — entenda o projeto e saiba EXATAMENTE como pode contribuir.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 REPOSITÓRIO ALVO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
https://github.com/enioxt/EGOS-Inteligencia

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 CONTEXTO ESSENCIAL (leia ANTES de analisar)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

O EGOS Inteligência é uma plataforma OPEN SOURCE que cruza dados públicos do Brasil (empresas, políticos, contratos, sanções, doações eleitorais) em um GRAFO INTERATIVO. Qualquer cidadão pode pesquisar e descobrir conexões ocultas entre entidades públicas e privadas.

NÚMEROS-CHAVE:
- 9.2 milhões de nós no grafo (meta: 141M+)
- 26 ferramentas de inteligência (OSINT) integradas ao chatbot AI
- 108 fontes de dados públicas mapeadas (36 carregadas)
- 10 detectores de padrões de corrupção
- 55+ endpoints de API
- 14 páginas no frontend
- 5 containers Docker
- 2 bots AI (Discord + Telegram)
- Custo total: ~$36/mês (100% autofinanciado)
- Licença: AGPL v3 (copyleft)
- Fork do World-Open-Graph/br-acc com divergência significativa

STACK TÉCNICO:
- Backend: Python 3.12 + FastAPI (assíncrono)
- Database: Neo4j 5 Community (grafo) + Redis 7 (cache)
- Frontend: React 18 + Vite + TypeScript
- ETL: 46 pipelines Python para ingestão de dados
- AI: OpenRouter (Gemini 2.0 Flash) com function calling
- Infra: Docker Compose + Caddy (SSL) + Contabo VPS
- Bots: Discord.js + Telegraf

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 MAPA COMPLETO DO SISTEMA (System Map)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Use este mapa para entender e dividir sua análise por ÁREAS:

INFRAESTRUTURA (Docker Compose):
┌─────────────┬──────────────────┬───────────┬────────────────────────────────┐
│ Container   │ Image            │ Port      │ Função                         │
├─────────────┼──────────────────┼───────────┼────────────────────────────────┤
│ bracc-neo4j │ neo4j:5          │ 7474,7687 │ Banco de grafo (9.2M nós)      │
│ redis       │ redis:7-alpine   │ 6379      │ Cache (512MB, LRU)             │
│ api         │ python:3.12-slim │ 8000      │ FastAPI backend                │
│ frontend    │ node:20-alpine   │ 5173      │ React 18 + Vite                │
│ caddy       │ caddy:2          │ 80, 443   │ Reverse proxy + SSL automático │
└─────────────┴──────────────────┴───────────┴────────────────────────────────┘

API (13 routers, 55+ endpoints):
- /api/v1/chat — Chat AI com 26 tools (function calling)
- /api/v1/conversations — CRUD de conversas persistentes
- /api/v1/search — Busca fuzzy + wildcard de entidades
- /api/v1/entity — Entidade por CPF/CNPJ, exposure score, timeline, conexões
- /api/v1/graph — Visualização de grafo interativo
- /api/v1/patterns — 10 detectores de padrões (contract_splitting, benford, HHI, etc.)
- /api/v1/baseline — Perfil baseline de entidade
- /api/v1/investigation — CRUD completo + export JSON/MD/HTML/PDF (14 endpoints, JWT)
- /api/v1/shared — Investigações compartilhadas publicamente
- /api/v1/public — API pública (meta, patterns, graph — sem auth)
- /api/v1/meta — Health, stats, sources, cache, security, ETL progress
- /api/v1/monitor — Sanções recentes + relatórios municipais automáticos
- /api/v1/analytics — Pageview tracking + summary
- /api/v1/activity — Feed de atividade
- /api/v1/auth — Register, login, JWT
- /api/v1/gazette-monitor — Scanner de diários oficiais

FRONTEND (14 páginas):
- Landing (hero search + live stats + reports + timeline)
- Dashboard (buscas recentes + quick search)
- Search (busca completa de entidades)
- EntityAnalysis (análise profunda de entidade)
- GraphExplorer (visualização interativa de grafo)
- Patterns (detecção de padrões de risco)
- Baseline (perfil comparativo de entidade)
- Investigations (notebook de investigação — JWT)
- SharedInvestigation (investigação pública compartilhada)
- Analytics (analytics de pageviews)
- Activity (feed de atividade)
- Reports (relatórios de investigação publicados)
- Login / Register (autenticação)

CHAT AI — 26 FERRAMENTAS OSINT:
1-3: Neo4j (search_entities, connections, cypher_query)
4: Web (Brave Search + DuckDuckGo fallback)
5-6: TransfereGov (emendas parlamentares, transferências federais)
7-8: Câmara (CEAP gastos deputados, votações nominais)
9: Querido Diário (diários oficiais de 5.570 municípios)
10-14: Portal Transparência (servidores, licitações, contratos, sanções, CPGF)
15: PNCP (licitações nacional)
16-17: Empresas (cnpj_info, opencnpj)
18: OAB (verificação de advogado)
19: BNMP/CNJ (mandados de prisão)
20: Polícia Federal (procurados)
21: MTE (lista suja trabalho escravo)
22: DataJud/CNJ (processos judiciais)
23: Interpol (red/yellow notices)
24: PEPs por cidade
25: Receita Federal (CNPJ direto)
26: Neo4j (estatísticas do grafo)

DETECTORES DE PADRÃO (10):
- contract_splitting (fracionamento de contratos)
- hhi_concentration (concentração de mercado)
- benford_analysis (lei de Benford em valores)
- pep_company_ownership (PEP como sócio)
- revolving_door (porta giratória público→privado)
- amendment_beneficiary (emenda beneficia empresa do doador)
- single_bidder_repeat (licitação sem concorrência repetida)
- same_day_contracts (contratos no mesmo dia)
- shared_address_network (empresas concorrentes no mesmo endereço)
- inexigibilidade_recurrence (inexigibilidade recorrente)

MIDDLEWARE & SEGURANÇA:
- Input Sanitizer: 10 padrões de prompt injection
- Public Guard: bloqueio de CPF, masking de PII
- Cache Service: Redis cache-aside (TTL por endpoint)
- CORS: origens explícitas (não wildcard)
- JWT Auth: para investigações
- LGPD: CPF NUNCA é pesquisável, exibível ou exportável

COMPLIANCE & ÉTICA:
- ETHICS.md: usos proibidos, linguagem não-acusatória
- LGPD.md: tratamento de dados pessoais, direitos do titular
- DISCLAIMER.md: sinais ≠ prova jurídica
- PRIVACY.md, TERMS.md, SECURITY.md, ABUSE_RESPONSE.md

ETL (46 pipelines):
- 36 fontes carregadas (CEIS, CNEP, CEPIM, CEAF, PEP, OpenSanctions, TSE, DOU, etc.)
- 9 em progresso (CNPJ 53.6M empresas é o maior — Receita Federal)
- 63+ mapeadas mas sem pipeline ainda

BOTS EXTERNOS:
- Discord: discord.js, 14 tools OSINT, PM2 managed
- Telegram: Telegraf, 14 tools OSINT (@EGOSin_bot)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 ESTRUTURA DA ANÁLISE (siga EXATAMENTE esta ordem)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PARTE 1: VISÃO GERAL
📋 1.1 — Resumo Executivo (3 parágrafos: o que é, pra que serve, impacto social)
🌍 1.2 — Contexto e Inspirações (fork do br-acc, comparação com OpenSanctions, Aleph/OCCRP, Serenata de Amor)
📊 1.3 — Números e Métricas Atuais (tabela com todos os números-chave)

PARTE 2: ANÁLISE TÉCNICA POR ÁREA
🏗 2.1 — Arquitetura & Infraestrutura
  - Diagrama textual do fluxo de dados
  - Análise da topologia Docker
  - Custo-benefício (tudo isso por $36/mês)
  - Pontos fortes e fracos

🐍 2.2 — Backend (Python/FastAPI)
  - Organização dos 13 routers
  - Qualidade do código
  - Performance e escalabilidade
  - Segurança (middleware, sanitização, auth)

🧠 2.3 — Chatbot AI & Ferramentas OSINT
  - Arquitetura do function calling (26 tools)
  - Sistema de tiers (premium/free/BYOK)
  - Enrichment de queries
  - Evidence chain e proveniência de dados

🔍 2.4 — Detecção de Padrões
  - Os 10 detectores implementados
  - Qualidade dos algoritmos
  - Cobertura e limitações
  - Sugestões de novos padrões

📊 2.5 — Frontend (React)
  - As 14 páginas e UX
  - Design system e responsividade
  - Visualização de grafos
  - Acessibilidade

🗄 2.6 — Neo4j & Modelo de Grafo
  - Schema (tipos de nós e relacionamentos)
  - Performance com 9.2M nós (meta: 141M+)
  - Queries Cypher e otimizações
  - Algoritmos GDS planejados

📥 2.7 — ETL & Pipeline de Dados
  - Os 46 pipelines existentes
  - Qualidade e robustez
  - Fontes prioritárias pendentes
  - Sugestões de novas fontes

🔒 2.8 — Segurança & Compliance
  - LGPD compliance (CPF blocking, masking middleware)
  - Prompt injection protection
  - GitGuardian / secret scanning
  - Política de ética e linguagem neutra
  - GDPR readiness

🤖 2.9 — Bots (Discord + Telegram)
  - Arquitetura e ferramentas
  - UX do bot
  - Rate limiting e custo

PARTE 3: AVALIAÇÃO
🏆 3.1 — Pontos Fortes (mínimo 10, com justificativa técnica e citação de arquivo)
⚠️ 3.2 — Pontos Fracos e Riscos (mínimo 8, seja honesto e construtivo)
💡 3.3 — Sugestões Priorizadas (alta/média/baixa prioridade + estimativa de esforço)

📊 3.4 — Scorecard Técnico (notas de 0-10):
| Dimensão | Nota | Justificativa |
|----------|------|---------------|
| Arquitetura | ?/10 | ... |
| Qualidade de Código | ?/10 | ... |
| Escalabilidade | ?/10 | ... |
| Segurança | ?/10 | ... |
| UI/UX | ?/10 | ... |
| Documentação | ?/10 | ... |
| Impacto Social | ?/10 | ... |
| Facilidade de Contribuição | ?/10 | ... |
| Custo-Eficiência | ?/10 | ... |
| Inovação | ?/10 | ... |

PARTE 4: COMO CONTRIBUIR (A MAIS IMPORTANTE!)

Analise o repositório e crie um GUIA DETALHADO de contribuição para cada perfil:

👥 4.1 — Para Não-Programadores:
  - Reportar bugs e sugerir melhorias (GitHub Issues)
  - Testar o chatbot e reportar erros
  - Melhorar textos e traduções (PT-BR ↔ EN)
  - Revisar e sugerir novas fontes de dados
  - Divulgar o projeto (redes sociais, palestras, artigos)
  - Apoiar financeiramente ($36/mês mantém tudo)
  - Criar conteúdo educacional (vídeos, tutoriais)
  - Revisão legal (advogados: LGPD, ética, compliance)
  - Jornalismo investigativo usando a plataforma

🐣 4.2 — Para Iniciantes em Programação:
  - Issues marcadas "good first issue"
  - Melhorar CSS/responsividade do frontend
  - Adicionar testes unitários
  - Documentação técnica
  - Tradução de código/comentários

🐍 4.3 — Para Desenvolvedores Python:
  - Criar novos pipelines ETL (79 fontes mapeadas, 33+ sem pipeline)
  - Implementar novos detectores de padrão
  - Otimizar queries Cypher
  - Adicionar novas ferramentas ao chatbot
  - Melhorar rate limiting e cache

⚛️ 4.4 — Para Desenvolvedores Frontend:
  - Melhorar visualização de grafos
  - Implementar dark/light theme
  - Acessibilidade (WCAG)
  - PWA / mobile experience
  - Dashboard de analytics

🔒 4.5 — Para Especialistas em Segurança:
  - Pen testing da API pública
  - Revisão de prompt injection defense
  - Auditoria de dependências
  - Hardening da infra Docker
  - Revisão de CORS/CSP/headers

📊 4.6 — Para Data Scientists:
  - Algoritmos de detecção de anomalia
  - PageRank, Community Detection, Shortest Path
  - Análise de redes (Network Science)
  - Machine Learning para padrões de fraude

📈 4.7 — Para Marketing & Comunidade:
  - Growth hacking para comunidade open source
  - Social media (Twitter/X, LinkedIn, Reddit)
  - Apresentações em meetups/conferências
  - Case studies e white papers
  - Parcerias com universidades, ONGs, jornalistas

💰 4.8 — Para Apoiadores Financeiros:
  - Custo atual: ~$36/mês (VPS Contabo + domínio)
  - O que mais recursos permitiriam:
    * VPS maior para o CNPJ ETL completo (53.6M empresas)
    * Modelos de IA melhores (GPT-4o, Claude)
    * Mais armazenamento para novas fontes
    * CI/CD pipeline com testes automáticos
  - Como apoiar: [egos.ia.br](https://egos.ia.br)

⚖️ 4.9 — Para Advogados e Compliance:
  - Revisão da política LGPD
  - Avaliação de risco jurídico
  - Contribuição para ETHICS.md e TERMS.md
  - Consultoria sobre acesso a dados públicos (LAI)
  - Revisão de linguagem não-acusatória

🔬 4.10 — Para Pesquisadores e Acadêmicos:
  - Papers sobre transparência pública com grafos
  - Datasets para pesquisa de ciência política
  - Benchmarks de performance Neo4j em larga escala
  - Estudos de caso de detecção de corrupção
  - Parcerias com universidades

PARTE 5: APRENDIZADOS

🎓 5.1 — Lições Técnicas (explique de forma didática):
  - Por que Neo4j é perfeito para cross-referencing de dados públicos
  - Como fazer masking de CPF em FastAPI (middleware LGPD)
  - Arquitetura low-cost: tudo por $36/mês com Contabo + Docker
  - Function calling com 26 tools: como construir um agente OSINT
  - Lei de Benford para detectar fraudes em licitações
  - Cache-aside pattern com Redis para APIs de alto tráfego

🎯 5.2 — Lições de Produto:
  - Por que chatbot é melhor interface que formulários para OSINT
  - Mobile-first para dados públicos (90% do Brasil acessa via celular)
  - Transparência radical: código aberto, custos públicos, metodologia documentada

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 REGRAS OBRIGATÓRIAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Leia TODO o repositório: README.md, ROADMAP.md, ETHICS.md, LGPD.md, docs/, código-fonte
2. Cite SEMPRE o arquivo e caminho exato (ex: "api/src/bracc/routers/chat.py")
3. Mostre snippets de código reais quando relevante
4. Use linguagem clara em português brasileiro
5. Seja honesto sobre pontos fracos — o projeto valoriza transparência
6. Explique conceitos técnicos de forma acessível (para quem está aprendendo)
7. Na seção de contribuição, seja ESPECÍFICO (nomes de arquivos, issues, áreas)
8. Use emojis e formatação para facilitar a leitura
9. Padrões encontrados são SINAIS, não prova jurídica (respeite ETHICS.md)
10. No final, SEMPRE pergunte:
    "Qual área te interessou mais? Posso detalhar qualquer seção, gerar um plano de contribuição personalizado, criar um diagrama Mermaid da arquitetura, ou fazer uma análise de performance específica."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 DOCUMENTOS-CHAVE PARA LER PRIMEIRO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Priorize a leitura destes arquivos (em ordem):
1. README.md — Visão geral completa
2. ROADMAP.md — 79 fontes de dados mapeadas
3. docs/SYSTEM_MAP.md — Mapa completo do sistema
4. docs/SYSTEM_CAPABILITIES_2026-03.md — 26 tools testadas
5. docs/TECHNICAL_DOSSIE_2026-03.md — Audit técnico completo
6. ETHICS.md — Política de ética
7. LGPD.md — Compliance de dados pessoais
8. docs/HONEST_ASSESSMENT_2026-03.md — Auto-avaliação honesta
9. api/src/bracc/routers/chat.py — Coração do chatbot
10. frontend/src/pages/Landing.tsx — Página principal

Agora comece a análise completa do repositório https://github.com/enioxt/EGOS-Inteligencia seguindo EXATAMENTE esta estrutura.
```

---

## 🔄 Changelog

| Versão | Data | Mudanças |
|--------|------|----------|
| v1.0 | 2026-03-02 | Prompt inicial com 12 seções |
| v2.0 | 2026-03-03 | System Map embutido, 10 perfis de contribuição, scorecard 10 dimensões, 9 áreas técnicas, documentos-chave priorizados, guia de ferramentas/IDEs |

---

## 💬 Feedback

Usou o prompt e tem sugestões? Abra uma [issue](https://github.com/enioxt/EGOS-Inteligencia/issues) com o título `[Meta Prompt] Sua sugestão` ou mande no [Telegram @ethikin](https://t.me/ethikin).

---

*"Dados públicos, código aberto, transparência real. Qualquer pessoa pode ajudar."*
