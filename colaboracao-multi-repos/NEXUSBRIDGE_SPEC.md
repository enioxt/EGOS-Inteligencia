# NexusBridge — Camada de Interoperabilidade Cross-Repo

> **Codename:** NexusBridge
> **Versão:** 0.1.0-spec | **Data:** 2026-03-05
> **Origem:** PR #56 (`colaboracao-multi-repos/`) + arquitetura atual

---

## 1) Visão

**NexusBridge** é a camada de integração que permite que os 3 repositórios do ecossistema EGOS compartilhem dados de forma segura, sem duplicação:

- **EGOS Inteligência (br-acc):** Provedor de dados (Neo4j 59M+ empresas, PEPs, sanções)
- **egos-lab:** Orquestrador de agentes + bots (Telegram, Discord)
- **Carteira Livre:** Produto final B2C (marketplace de instrutores)
- **Forja (futuro):** ERP chat-first que consumirá dados públicos para enriquecer cadastros

---

## 2) Princípios

1. **SSOT:** Neo4j na VPS Contabo é a única fonte de verdade para dados públicos brasileiros
2. **Sem duplicação:** Nenhum outro repo clona o banco. Todos consultam via API
3. **Segurança:** Endpoints protegidos por SERVICE_KEY (não expostos publicamente)
4. **Semântico:** Nunca expor Cypher cru para a internet. Endpoints semânticos
5. **Auditoria:** Toda consulta cross-repo é logada

---

## 3) Arquitetura

```
┌──────────────────────────────────────────────────────────┐
│              VPS Contabo (217.216.95.126)                  │
│  ┌──────────────────────────────────────────────────┐    │
│  │  EGOS Inteligência (br-acc)                       │    │
│  │  FastAPI + Neo4j (59M empresas, 133K PEPs)        │    │
│  │                                                    │    │
│  │  /api/v1/interop/entity/{cnpj}   ← busca empresa │    │
│  │  /api/v1/interop/network/{cnpj}  ← grafo de rede │    │
│  │  /api/v1/interop/pep/{cpf}       ← check PEP     │    │
│  │  /api/v1/interop/sanctions/{id}  ← sanções        │    │
│  │  /api/v1/interop/health          ← status         │    │
│  │                                                    │    │
│  │  Auth: X-Service-Key header (não JWT público)      │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
         ▲              ▲              ▲
         │              │              │
    SERVICE_KEY    SERVICE_KEY    SERVICE_KEY
         │              │              │
    ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
    │egos-lab │   │carteira │   │  Forja  │
    │(agentes)│   │ livre   │   │(futuro) │
    │Railway/ │   │ Vercel  │   │         │
    │local    │   │         │   │         │
    └─────────┘   └─────────┘   └─────────┘
```

---

## 4) Módulos Reaproveitáveis

### No `br-acc` (Provedor — criar endpoints interop)

| Existente | Como reaproveitar |
|-----------|-------------------|
| `routers/chat.py` (26 tools) | Extrair lógica de busca para serviços reutilizáveis por interop |
| `services/neo4j_service.py` | Base para queries interop (execute_query, sanitize_props) |
| `services/public_guard.py` | Masking LGPD obrigatório em respostas interop |
| `services/cache.py` | Cache Redis para queries frequentes cross-repo |
| `middleware/rate_limit.py` | Rate limit por SERVICE_KEY |

### No `egos-lab` (Consumidor — criar cliente)

| Existente | Como reaproveitar |
|-----------|-------------------|
| `packages/shared/src/ai-client.ts` | Modelo de como criar um HTTP client com retry/pricing |
| `packages/shared/src/rate-limiter.ts` | Rate limit do lado cliente |
| `packages/mcp/src/index.ts` | Tool Runner pattern — criar tool `bracc.query-entity` |
| `apps/telegram-bot/src/index.ts` | Integração bot + Supabase + AI. Adicionar tool de consulta br-acc |

### No `carteira-livre` (Consumidor — KYC enrichment)

| Existente | Como reaproveitar |
|-----------|-------------------|
| `services/api-utils.ts` | Padrão de auth + error handling |
| `services/api-usage-logger.ts` | Log de cada consulta cross-repo |
| Fluxo de onboarding | Enriquecer KYC: "este CNPJ tem sanções? É PEP?" |

---

## 5) Contratos de Eventos (Canônicos)

Definidos no PR #56 (`PERSISTENCIA_E_INTEROP.md`):

```typescript
// Evento canônico cross-repo
interface EgosEvent {
  event_id: string;          // UUID
  event_type: string;        // "entity.queried" | "sanction.found" | "pep.matched"
  source_repo: string;       // "br-acc" | "egos-lab" | "carteira-livre"
  timestamp: string;         // ISO 8601
  payload: Record<string, unknown>;
  actor?: string;            // service key identifier
}
```

---

## 6) Tasks (Roadmap NexusBridge)

### Fase 0 — Fundação
- [ ] TASK-NB-001: Criar SERVICE_KEY no .env da VPS + middleware de validação
- [ ] TASK-NB-002: Criar router `/api/v1/interop/` no br-acc (FastAPI)
- [ ] TASK-NB-003: Endpoint `GET /interop/entity/{cnpj}` — busca empresa + sócios
- [ ] TASK-NB-004: Endpoint `GET /interop/network/{cnpj}` — grafo de rede (1 hop)
- [ ] TASK-NB-005: Endpoint `GET /interop/pep/{cpf_or_name}` — check PEP
- [ ] TASK-NB-006: Endpoint `GET /interop/sanctions/{cnpj}` — sanções CEIS/CNEP
- [ ] TASK-NB-007: Endpoint `GET /interop/health` — status do Neo4j + contagens

### Fase 1 — Clientes
- [ ] TASK-NB-008: Criar `bracc-client.ts` no egos-lab (`packages/shared/src/`)
- [ ] TASK-NB-009: Criar tool `bracc.query-entity` no MCP do egos-lab
- [ ] TASK-NB-010: Integrar no Telegram bot — quando user perguntar sobre empresa, consultar VPS
- [ ] TASK-NB-011: Criar client no carteira-livre para KYC enrichment

### Fase 2 — Governança
- [ ] TASK-NB-012: Audit log de todas as queries interop (quem, quando, o quê)
- [ ] TASK-NB-013: Rate limit por SERVICE_KEY (ex: 100 req/min por repo)
- [ ] TASK-NB-014: Dashboard de uso interop no br-acc frontend
- [ ] TASK-NB-015: Alertas Telegram quando limite de uso é alto

---

## 7) Segurança

- SERVICE_KEY em `.env` (nunca hardcoded, nunca em git)
- Endpoints interop NÃO são públicos (não aparecem no frontend)
- LGPD: masking de CPFs em todas as respostas
- Rate limit por chave
- Queries Cypher parametrizadas (sem injeção)
- CORS restrito a IPs/domínios conhecidos

---

*"Um grafo. Múltiplos produtos. Zero duplicação."*
