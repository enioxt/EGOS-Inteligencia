# EGOS Inteligência — Plataforma Aberta de Cruzamento de Dados Públicos

> **Status:** ⏸️ Ritmo reduzido — renomeando para EGOS Inteligência. 77M entidades, Neo4j graph, ETL pipeline.  
> Este projeto tem MVP funcional disponível. Interessados em contribuir ou co-fundar: entre em contato via [Issues](https://github.com/enioxt/br-acc/issues) ou enio@egos.ia.br

<!-- RHO_BADGE --> **Rho Score:** 🟡 0.30 (WARNING) | Contributors: 4 | Commits (30d): 94 | Updated: 2026-03-02 <!-- /RHO_BADGE -->

Idioma: **Português (Brasil)** | [English](#english)

[![Licença: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![API Status](https://img.shields.io/badge/API-ONLINE-brightgreen)](http://204.168.217.125/health)
[![Discord Bot](https://img.shields.io/badge/Discord-EGOS%20Intelig%C3%AAncia-7289da)](https://discord.gg/egos)
[![Telegram Bot](https://img.shields.io/badge/Telegram-@EGOSin__bot-26A5E4)](https://t.me/EGOSin_bot)

> **Em uma frase:** O EGOS Inteligência conecta dados públicos do Brasil (empresas, políticos, contratos, sanções, doações eleitorais) em um grafo interativo que mostra quem se relaciona com quem.

Site: [inteligencia.egos.ia.br](https://inteligencia.egos.ia.br) | Ecossistema: [EGOS](https://egos.ia.br) | Comunidade: [@ethikin](https://t.me/ethikin)

---

## Origem e Diferenças

Este projeto é um **fork** do [World-Open-Graph/egos-inteligencia](https://github.com/World-Open-Graph/egos-inteligencia), uma infraestrutura open-source para dados públicos brasileiros em grafo.

O EGOS Inteligência diverge significativamente do upstream:

| Aspecto | Upstream (egos-inteligencia) | EGOS Inteligência |
|---|---|---|
| **Idioma** | Inglês | Português-BR nativo |
| **Interface** | Desktop-only, requer login | Mobile-first, público, chatbot AI |
| **Dados carregados** | Demo/seed | **9,1M nós** (8,8M empresas + 133K PEPs + 23K sanções) |
| **Bots AI** | Nenhum | Discord + Telegram (14 ferramentas OSINT) |
| **Investigações** | Não | Upload, fork, compartilhamento público |
| **Relatórios** | Não | 11 relatórios publicados (ex: Patense R$217M BNDES) |
| **Infraestrutura** | Local/demo | Hetzner VPS (12 vCPU, 24GB RAM) + Redis |
| **LGPD** | Parcial | CPF bloqueado em todo o sistema, masking middleware |
| **Fontes planejadas** | 13 | 79 fontes no roadmap |
| **Algoritmos** | Básico | PageRank, Benford, HHI, Community Detection (roadmap) |
| **Ecossistema** | Standalone | Integrado ao [EGOS Framework](https://egos.ia.br) (24 agentes AI) |

Mantemos rastreamento do upstream e contribuímos PRs quando aplicável. Um job automatizado ([BR-ACC Monitor](scripts/README-egos_inteligencia-monitor.md)) roda 2x ao dia (GitHub Actions) para listar forks, PRs e issues do upstream, categorizar mudanças e sugerir alinhamento do TASKS.md com PRs mergeados; notificações opcionais no Discord/Telegram.

---

## Para Que Serve?

Imagine que você quer saber: **"A empresa que ganhou a licitação do hospital tem alguma ligação com o político que aprovou a verba?"**

Hoje, você precisaria acessar dezenas de portais diferentes (Receita Federal, TSE, Portal da Transparência...) e cruzar manualmente.

O EGOS Inteligência faz isso automaticamente:

1. **Coleta** dados de 38+ fontes oficiais do governo brasileiro
2. **Conecta** em um grafo de relacionamentos
3. **Revela** vínculos de forma visual, pesquisável e compartilhável

### O Que Já Está Dentro

| O Que | Fonte | Volume |
|---|---|---|
| Empresas e sócios | CNPJ (Receita Federal) | 53,6M empresas (ETL em andamento) |
| Doações eleitorais | TSE | 7,1M registros (2002-2024) |
| Contratos federais | Portal da Transparência + ComprasNet | 1,1M contratos |
| Empresas punidas | CEIS, TCU, IBAMA, CVM | 150k sanções |
| Dívidas com a União | PGFN | 24M débitos |
| Diário Oficial | DOU | 3,98M atos |
| Gastos de deputados | Câmara (CEAP) | 4,6M despesas |
| Offshores | ICIJ (Panama/Paradise/Pandora Papers) | 4,8k entidades |
| PEPs | CGU + OpenSanctions | 252k registros |
| Processos no STF | STF | 2,38M casos |
| Patrimônio de candidatos | TSE Bens | 14,3M bens declarados |

**Status atual: 9.166.587 nós carregados.** Meta: 141M nós e 92M conexões. CNPJ ETL concluído para 8,8M empresas.

> **Importante:** Padrões encontrados são **sinais**, não prova jurídica. Toda conclusão requer revisão humana.

---

## Quero Usar!

### Opção 1: Chatbot AI (Sem Instalar Nada)

O assistente EGOS Inteligência está disponível 24/7 via:

- **Website:** [inteligencia.egos.ia.br](https://inteligencia.egos.ia.br) — chatbot direto na página inicial
- **Discord:** [Servidor EGOS](https://discord.gg/egos) → mencione `@EGOS Intelligence`
- **Telegram:** [@EGOSin_bot](https://t.me/EGOSin_bot)

Exemplos de perguntas:
```
Quais os vínculos da empresa CNPJ 11.222.333/0001-81?
Quanto a empresa X recebeu do BNDES?
Busque licitações de saúde em São Paulo
Quem são os maiores supersalários do TJSP?
```

**26 ferramentas OSINT integradas** (testadas em 2026-03-03 — [relatório completo](docs/SYSTEM_CAPABILITIES_2026-03.md)):

| Categoria | Ferramentas | Fonte |
|---|---|---|
| **Grafo Neo4j** | search_entities, graph_stats, connections, cypher_query, data_summary | Neo4j (9,1M nós) |
| **Portal Transparência** | servidores, licitações, CPGF, viagens, contratos, sanções, CNPJ | gov.br (API key) |
| **Câmara dos Deputados** | CEAP (gastos), votações nominais | dadosabertos.camara.leg.br |
| **Judiciário** | processos (DataJud), mandados de prisão (BNMP) | CNJ |
| **Diários Oficiais** | search_gazettes (5.570+ municípios) | Querido Diário (OKBR) |
| **Empresas** | cnpj_info, opencnpj, sanções CEIS/CNEP | Portal Transparência + OpenCNPJ |
| **Licitações** | PNCP (federal/estadual/municipal) | pncp.gov.br |
| **Segurança** | procurados (PF/Interpol), lista suja (trabalho escravo) | gov.br |
| **Jurídico** | OAB (verificação de advogado) | cna.oab.org.br |
| **Web** | Brave Search + DuckDuckGo fallback | brave.com/search/api |
| **Municipal** | emendas, transferências federais, PEPs por cidade | TransfereGov API |

### Opção 2: API Pública

```bash
# Estatísticas gerais
curl http://204.168.217.125/api/v1/public/meta

# Grafo de vínculos de uma empresa
curl http://204.168.217.125/api/v1/public/graph/company/11222333000181
```

| Método | Rota | O Que Faz |
|---|---|---|
| GET | `/health` | Verifica se o servidor está online |
| GET | `/api/v1/public/meta` | Estatísticas do grafo |
| GET | `/api/v1/public/graph/company/{cnpj}` | Grafo de vínculos por CNPJ |
| POST | `/api/v1/chat` | Chat conversacional (em desenvolvimento) |

### Opção 3: Rodar Localmente

#### Pré-requisitos
- **Docker** e **Docker Compose** instalados ([guia de instalação](https://docs.docker.com/get-docker/))
- **8GB RAM** mínimo (16GB recomendado)
- **10GB disco** livre

#### Passo 1: Clonar e configurar
```bash
git clone https://github.com/enioxt/EGOS-Inteligencia.git
cd EGOS-Inteligencia
cp .env.example infra/.env
```

#### Passo 2: Obter API keys (gratuitas)

Edite `infra/.env` e adicione suas keys:

| Key | Onde obter | Custo |
|-----|-----------|-------|
| `NEO4J_PASSWORD` | Escolha uma senha forte | Grátis |
| `OPENROUTER_API_KEY` | [openrouter.ai/keys](https://openrouter.ai/keys) (login com Google) | Grátis (Gemini Flash) |
| `PORTAL_TRANSPARENCIA_API_KEY` | [portaldatransparencia.gov.br/api-de-dados](https://portaldatransparencia.gov.br/api-de-dados/cadastrar-email) | Grátis |
| `BRAVE_API_KEY` | [brave.com/search/api](https://brave.com/search/api/) (2000 buscas/mês grátis) | Grátis |
| `DATAJUD_API_KEY` | [datajud-wiki.cnj.jus.br](https://datajud-wiki.cnj.jus.br/api-publica/acesso) | Grátis (API pública) |

> **Segurança:** Nunca commite o arquivo `.env`. Ele já está no `.gitignore`.

#### Passo 3: Subir os containers
```bash
cd infra && docker compose up -d
# Aguarde Neo4j ficar healthy (~30-60s)
docker compose ps  # Verifique: neo4j, redis, api, frontend devem estar 'healthy'
```

#### Passo 4: Carregar dados demo
```bash
export NEO4J_PASSWORD=sua_senha
bash scripts/seed-dev.sh  # Carrega ~1000 entidades demo
```

- **Frontend:** http://localhost:3000
- **API:** http://localhost:8000/health
- **Neo4j Browser:** http://localhost:7474
- **Chat AI:** http://localhost:3000 (precisa de OPENROUTER_API_KEY)

#### Usando com Windsurf IDE
1. Abra a pasta do projeto no Windsurf
2. O Windsurf detectará automaticamente o Docker Compose
3. Use o terminal integrado para rodar `cd infra && docker compose up -d`
4. O Cascade (AI assistant) pode ajudar com queries Cypher e debugging
5. Veja os workflows disponíveis em `.windsurf/workflows/`

#### Usando com Antigravity IDE
1. Abra a pasta do projeto no Antigravity
2. Configure o terminal para usar o Docker Compose
3. Use o painel de AI para explorar o código e a documentação
4. As API keys devem ser configuradas no `infra/.env` (não no IDE)

---

## Arquitetura

```
[79 Fontes Planejadas] → [ETL Python] → [Neo4j Grafo] → [FastAPI + Redis] → [React + Bots AI]
```

| Componente | Tecnologia |
|---|---|
| **Banco de Dados** | Neo4j 5 Community (grafo) |
| **Cache** | Redis 7 (512MB LRU, cache-aside) |
| **Backend** | FastAPI (Python 3.12, assíncrono) |
| **Frontend** | React 19 + Vite (mobile-first) |
| **ETL** | Python com pandas (45 pipelines) |
| **Bots** | Discord.js + Telegraf + AI Router (OpenRouter) |
| **Infra** | Docker Compose + Caddy + Hetzner VPS |

---

## Modos de Operação

| Variável | Padrão | O Que Controla |
|---|---|---|
| `PUBLIC_MODE` | `true` | Modo público ativado |
| `PUBLIC_ALLOW_PERSON` | `false` | Bloqueia entidades de pessoa física |
| `PATTERNS_ENABLED` | `false` | Desabilita detecção de padrões |

### Conformidade LGPD

- **CPF é bloqueado em TODO o sistema** — busca, exibição, exportação
- Middleware de masking intercepta qualquer CPF que escape para respostas JSON
- Apenas dados de pessoa jurídica (CNPJ) e dados já públicos por lei são exibidos
- Pessoa física aparece apenas por nome (sem documento), quando vinculada a cargo público (PEP)

---

## Roadmap

Veja [ROADMAP.md](ROADMAP.md) para o plano completo. Destaques:

| Fase | Status | O Que |
|---|---|---|
| **CNPJ ETL** | 🔵 Em andamento | 53.6M empresas da Receita Federal |
| **Chatbot AI** | ✅ Operacional | 26 ferramentas OSINT, Gemini 2.0 Flash, R$0,006/consulta |
| **Redis Cache** | ✅ Pronto | Cache-aside para queries frequentes |
| **GDS Algoritmos** | 🟡 Planejado | PageRank, Community Detection, Shortest Path |
| **Investigações** | ✅ Operacional | CRUD, export JSON/PDF, grafo visual |
| **Journey Tracker** | ✅ Operacional | localStorage, export JSON/MD, Web Share API |
| **79 Fontes** | 🟡 Gradual | DataJud, IBGE, DENATRAN, reguladoras... |

---

## Quero Contribuir!

| Nível | O Que Fazer | Precisa Programar? |
|---|---|---|
| **Iniciante** | Tradução, documentação, reportar bugs | Não |
| **Intermediário** | Pipelines ETL para novas fontes | Sim (Python) |
| **Avançado** | Algoritmos de anomalia, queries Cypher | Sim (Python + Neo4j) |

**Issues abertas:** [github.com/enioxt/egos-inteligencia/issues](https://github.com/enioxt/egos-inteligencia/issues) — várias marcadas como `good first issue` e `help wanted`

---

## Infraestrutura & Custos (Transparência Total)

| Serviço | O Quê | Custo (USD/mês) |
|---|---|---|
| **Hetzner VPS** | 12 vCPU, 24GB RAM, 500GB SSD — Neo4j, Redis, API, bots, frontend | $35 |
| **Vercel** | egos.ia.br, inteligencia.egos.ia.br | Free |
| **Supabase** | PostgreSQL (conversas, relatórios, custos) | Free |
| **OpenRouter** | Gemini 2.0 Flash para IA dos bots | Free |
| **Domínio** | egos.ia.br | ~$0.60 |
| **Total** | Plataforma OSINT completa + 2 bots AI + website | **~$36/mo** |

> 100% autofinanciado. Se achar útil, considere apoiar: [egos.ia.br](https://egos.ia.br)

---

## Legal & Ethics

- [Política de Ética](ETHICS.md) — usos proibidos, linguagem neutra
- [LGPD](LGPD.md) — tratamento de dados pessoais
- [Termos de Uso](TERMS.md)
- [Aviso Legal](DISCLAIMER.md) — sinais ≠ prova jurídica
- [Privacidade](PRIVACY.md)
- [Segurança](SECURITY.md) — reportar vulnerabilidades
- [Resposta a Abuso](ABUSE_RESPONSE.md)

## Licença

[GNU Affero General Public License v3.0](LICENSE) — código aberto, copyleft.

---

<a name="english"></a>

# English

EGOS Inteligência is an open-source platform for cross-referencing Brazilian public data, built on a graph database connecting companies, politicians, contracts, sanctions, and electoral donations.

**Forked from** [World-Open-Graph/egos-inteligencia](https://github.com/World-Open-Graph/egos-inteligencia) with significant divergence: mobile-first UI, AI chatbot, LGPD-compliant CPF blocking, 14 OSINT tools via Discord/Telegram bots, 79 planned data sources, and integration with the [EGOS Framework](https://egos.ia.br) (24 AI agents). An automated [BR-ACC Monitor](scripts/README-egos_inteligencia-monitor.md) runs twice daily (GitHub Actions) to track upstream forks, PRs, issues, and roadmap suggestions.

## Live Infrastructure

| Service | Status | URL |
|---|---|---|
| **Public API** | ✅ Online | http://204.168.217.125/health |
| **Frontend** | ✅ Online | [inteligencia.egos.ia.br](https://inteligencia.egos.ia.br) |
| **Discord Bot** | ✅ Online (14 OSINT tools) | `@EGOS Intelligence` |
| **Telegram Bot** | ✅ Online (14 OSINT tools) | [@EGOSin_bot](https://t.me/EGOSin_bot) |

## Quick Start

```bash
git clone https://github.com/enioxt/egos-inteligencia.git && cd egos-inteligencia
cp .env.example infra/.env  # Edit: NEO4J_PASSWORD + API keys (see docs)
cd infra && docker compose up -d
# See full setup guide: docs/SYSTEM_CAPABILITIES_2026-03.md
```

## Key Differences from Upstream

- LGPD-compliant: CPF search/display blocked system-wide
- Mobile-first responsive design with bottom navigation
- AI chatbot as primary interface (not just search)
- 26 OSINT tools via website chat + Discord + Telegram bots
- 9.1M nodes loaded (8.8M companies, 133K PEPs, 23K sanctions)
- Redis cache layer for performance
- 11 real investigation reports published
- Investigation upload, fork, and sharing (planned)
- 79 data sources on roadmap (vs 13 upstream)
- Integrated with EGOS ecosystem (24 AI agents, MCP tools)
- Automated upstream monitor (forks, PRs, issues; TASK↔PR suggestions in JSON only, no automatic update to TASKS.md) 2x/day via GitHub Actions

## LGPD Compliance

CPF (Brazilian personal tax ID) is **never** searchable, displayable, or exportable. Only CNPJ (company ID) and publicly mandated data are exposed. All JSON responses pass through a CPF masking middleware as a safety net.

## Documentação Técnica

| Documento | O que contém |
|-----------|-------------|
| **[Dossiê Técnico](docs/TECHNICAL_DOSSIE_2026-03.md)** | Audit completo: arquitetura, 23 features, 10 pontos fortes, 10 fracos, 8 riscos, 16 recomendações |
| **[Capacidades do Sistema](docs/SYSTEM_CAPABILITIES_2026-03.md)** | 26 tools testadas, 42 endpoints, 14 APIs externas, comparação competitiva |
| **[Análise Intelink vs EGOS](docs/MERGE_ANALYSIS.md)** | Comparação frame-by-frame, 3 alternativas de merge |
| [Stack Decision](docs/analysis/STACK_SCALING_DECISION_2026-03.md) | Python vs Go — decisão de manter Python |
| [Fontes de Dados](docs/data-sources.md) | 108 fontes documentadas |
| [Compliance Legal](docs/legal/legal-index.md) | LGPD, ETHICS, PRIVACY, TERMS |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) · [ROADMAP.md](ROADMAP.md) · [Issues](https://github.com/enioxt/egos-inteligencia/issues)

## License

[GNU Affero General Public License v3.0](LICENSE)

---

*"Dados públicos são sinais, não prova jurídica. Nossa missão é torná-los acessíveis a todos."*
