# EGOS Inteligência — Plataforma Aberta de Cruzamento de Dados Públicos

> **Versão:** 0.8.0 | **Atualizado:** 2026-05-01 | **Status:** PAUSA
> **Parte do ecossistema [EGOS](https://github.com/enioxt/egos)**

Plataforma open-source para cruzamento de dados públicos brasileiros em grafo — 83M+ nós Neo4j, ETL pipeline, FastAPI, chatbot AI com 26 ferramentas OSINT.

**Live:** [inteligencia.egos.ia.br](https://inteligencia.egos.ia.br) · **API:** [health check](http://204.168.217.125/health)

---

## Para que serve

Conecta dados públicos do Brasil (empresas, políticos, contratos, sanções, doações eleitorais) em um grafo interativo que mostra quem se relaciona com quem.

```text
[79 Fontes Planejadas] → [ETL Python] → [Neo4j Grafo] → [FastAPI + Redis] → [React + Bots AI]
```

---

## Estado atual do banco

| Entidade | Quantidade |
|----------|-----------|
| Nós Neo4j | 83.773.683 |
| Labels | 32 |
| Relações | 26.808.540 |

---

## O que está dentro

| Dados | Fonte | Volume |
|-------|-------|--------|
| Empresas e sócios | CNPJ (Receita Federal) | 53,6M empresas |
| Doações eleitorais | TSE | 7,1M registros (2002-2024) |
| Contratos federais | Portal da Transparência | 1,1M contratos |
| Empresas punidas | CEIS, TCU, IBAMA, CVM | 150k sanções |
| Dívidas com a União | PGFN | 24M débitos |
| Diário Oficial | DOU | 3,98M atos |
| Gastos de deputados | Câmara (CEAP) | 4,6M despesas |
| Offshores | ICIJ (Panama/Paradise/Pandora Papers) | 4,8k entidades |
| Processos no STF | STF | 2,38M casos |

---

## Stack

| Componente | Tecnologia |
|-----------|-----------|
| Banco de Dados | Neo4j 5 Community (grafo) |
| Cache | Redis 7 (512MB LRU) |
| Backend | FastAPI (Python 3.12, assíncrono) |
| Frontend | React 19 + Vite (mobile-first) |
| ETL | Python com pandas (45 pipelines) |
| Bots | Discord.js + Telegraf + AI Router (OpenRouter) |
| Infra | Docker Compose + Caddy + Hetzner VPS |

---

## Quick Start

```bash
git clone https://github.com/enioxt/EGOS-Inteligencia.git
cd EGOS-Inteligencia
cp .env.example infra/.env  # NEO4J_PASSWORD + API keys
cd infra && docker compose up -d
bash scripts/seed-dev.sh    # ~1000 entidades demo
```

---

## Compliance LGPD

- **CPF bloqueado em todo o sistema** — busca, exibição, exportação
- Middleware de masking intercepta qualquer CPF nas respostas JSON
- Apenas CNPJ e dados públicos por lei são exibidos

---

## Ecossistema EGOS — Dependências

| Repo | Relação | Status |
|------|---------|--------|
| [egos](https://github.com/enioxt/egos) | Kernel upstream — Guard Brasil LGPD, governança, 24 agents AI | PROD |

**Upstream (o que este repo usa):** Guard Brasil (CPF masking + LGPD compliance), padrões de governança `.guarani/`, event bus types.

**Downstream (quem usa este repo):** produto independente — nenhum repo depende dele.

---

## Licença

[GNU Affero General Public License v3.0](LICENSE) — código aberto, copyleft.

*"Dados públicos são sinais, não prova jurídica. Nossa missão é torná-los acessíveis a todos."*
