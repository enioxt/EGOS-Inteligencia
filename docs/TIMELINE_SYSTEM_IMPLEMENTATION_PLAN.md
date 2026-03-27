# Timeline System — Implementação Completa (EGOS Ecosystem)

> **Objetivo:** Linha do tempo unificada em todo o ecossistema EGOS
> **Status:** Planejamento → Implementação
> **Prioridade:** P0 (TRANSPARENCY_RADICAL)
> **Estimativa Total:** 40 horas

---

## 📊 Visão Geral

### Princípio
> *"Não seremos uma caixa preta. Iremos mostrando tudo que vamos fazendo."*

### O que é Timeline?
- **Cronologia completa** de todos os eventos do sistema (relatórios, agentes, deploys, testes)
- **Status visual** em tempo real: 🟡 Running / 🟢 Complete / 🔴 Failed
- **Filtros + Search** por agente, sistema, tipo, data
- **Auto-refresh** a cada 30s
- **Drill-down:** Timeline → Evento → Logs → Código

### Onde existe?
- ✅ **FORJA:** Planejado em `TRANSPARENCY_RADICAL_PRD.md`
- ✅ **852:** `/admin/telemetry` parcial (expandir)
- ✅ **Carteira Livre:** 36 páginas admin + telemetry.ts (padrão ouro)
- ❌ **egos:** Kernel (sem UI)
- ❌ **egos-lab:** Sem HARVEST.md documentado
- ❌ **br-acc:** Sem HARVEST.md documentado
- ❌ **smartbuscas:** Auditando
- ❌ **intelink:** Verificar existência

### Quão importante é?
- **CRÍTICA** para governança: ver tudo em tempo real
- Implementa "Transparência Radical" (visão do projeto)
- Base para Drift Sentinel (auto-cura)
- Observabilidade completa (compliance)

---

## 🏗️ Arquitetura Técnica

### Schema Supabase (Compartilhado)

```sql
-- Timeline de relatórios (central)
CREATE TABLE transparency_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT,
    system VARCHAR(50) NOT NULL,  -- 'forja', '852', 'carteira-livre', etc
    agent VARCHAR(100),
    status VARCHAR(20) NOT NULL,  -- 'running', 'completed', 'failed'
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,
    triggered_by VARCHAR(20) NOT NULL,  -- 'manual', 'scheduled', 'webhook'
    output_url TEXT,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Métricas (time-series)
CREATE TABLE transparency_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(100) NOT NULL,
    system VARCHAR(50) NOT NULL,
    value DECIMAL(15,4) NOT NULL,
    unit VARCHAR(20),
    dimensions JSONB,
    captured_at TIMESTAMPTZ DEFAULT NOW()
);

-- Logs de observabilidade
CREATE TABLE transparency_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trace_id VARCHAR(36) NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    level VARCHAR(10) NOT NULL,
    system VARCHAR(50) NOT NULL,
    agent VARCHAR(100),
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_reports_system_status ON transparency_reports(system, status);
CREATE INDEX idx_reports_started_at ON transparency_reports(started_at DESC);
CREATE INDEX idx_metrics_name_system_time ON transparency_metrics(metric_name, system, captured_at);
CREATE INDEX idx_logs_trace_id ON transparency_logs(trace_id);
```

### Stack Tecnológico
- **UI Framework:** Next.js 15 + App Router
- **Component Library:** React 19 + Tailwind CSS v4
- **Charts:** Recharts (já usado em 852)
- **Grafos:** Visx/D3.js (opcional para visualizar arquitetura)
- **Realtime:** SSE (Server-Sent Events)
- **Cache:** Redis
- **Database:** Supabase PostgreSQL (compartilhado)

### Componentes Reutilizáveis (shared)

```typescript
// @egos/shared/components/admin/TransparencyTimeline.tsx
export interface ReportTimelineItem {
  id: string;
  title: string;
  description: string;
  system: string;
  agent?: string;
  status: 'running' | 'completed' | 'failed';
  startedAt: Date;
  completedAt?: Date;
  durationMs?: number;
  metadata: {
    triggeredBy: 'manual' | 'scheduled' | 'webhook';
    outputUrl?: string;
    errorMessage?: string;
  };
}

export const TransparencyTimeline: React.FC<{
  reports: ReportTimelineItem[];
  loading?: boolean;
  onRefresh?: () => void;
}>;

export const TimelineFilterBar: React.FC<{
  onFilter: (filters) => void;
}>;

export const TimelineItemCard: React.FC<{
  item: ReportTimelineItem;
  onClick?: () => void;
}>;

export const TimelineStatusBadge: React.FC<{
  status: 'running' | 'completed' | 'failed';
}>;
```

### API Routes (Compartilhadas)

```typescript
// GET /api/admin/transparency/reports
// POST /api/admin/transparency/reports
// GET /api/admin/transparency/telemetry
// GET /api/admin/transparency/logs/stream  (SSE)
// GET /api/admin/transparency/graph
// GET /api/admin/transparency/alerts
```

---

## 📋 Implementação por Sistema (Faseada)

### FASE 1: Fundação (2h) — TODOS

- [ ] **SETUP-001:** Criar migration Supabase + RLS policies
  - Arquivo: `/home/enio/egos/migrations/transparency_tables.sql`
  - Status: Pendente
  - Estimativa: 1h

- [ ] **SETUP-002:** Criar shared components em `@egos/shared`
  - Arquivo: `packages/shared/src/components/admin/transparency/`
  - Components: TransparencyTimeline, FilterBar, ItemCard, StatusBadge
  - Estimativa: 1h

---

### FASE 2: Forja (P0 — Maior Gap) — 8-10h

- [ ] **FORJA-001:** Criar página `/app/admin/transparencia/page.tsx`
  - Integra: Timeline + Telemetry Dashboard + Logs
  - Estimativa: 3h

- [ ] **FORJA-002:** Implementar API routes `/api/admin/transparency/*`
  - GET /reports, POST /reports, GET /telemetry, SSE /logs
  - Estimativa: 3h

- [ ] **FORJA-003:** Integrar com sistema de telemetry existente
  - Hook: useRealtimeTelemetry()
  - Estimativa: 2h

---

### FASE 3: 852 (P1 — Refinamento) — 4-6h

- [ ] **852-001:** Expandir `/admin/telemetry` → `/admin/transparencia`
  - Adicionar Timeline de relatórios
  - Estimativa: 3h

- [ ] **852-002:** Integrar Architecture Graph
  - D3.js/Visx para visualizar dependências
  - Estimativa: 2h

---

### FASE 4: Carteira Livre (P1 — Padrão Ouro) — 6-8h

- [ ] **CARTEIRA-001:** Refatorar admin pages para padrão unificado
  - Migrar 36 páginas para novo pattern
  - Estimativa: 4h

- [ ] **CARTEIRA-002:** Criar `/admin/transparencia` reference implementation
  - Servir como modelo para outros sistemas
  - Estimativa: 3h

---

### FASE 5: Disseminação (P2) — 4h

- [ ] **DISSEMINATE-001:** egos-lab, br-acc, smartbuscas, intelink
  - Aplicar padrão descoberto em Forja/852/Carteira
  - Estimativa: 2h per system

---

## 🚀 Começar Agora: FASE 1 + FORJA

### Próximos 3 Passos:

1. **Criar migration Supabase**
   ```bash
   # Em /home/enio/egos
   supabase migration new transparency_tables
   ```

2. **Implementar shared components**
   ```bash
   # Em packages/shared/src/components/admin/transparency/
   mkdir -p packages/shared/src/components/admin/transparency
   touch TransparencyTimeline.tsx TimelineFilterBar.tsx TimelineItemCard.tsx TimelineStatusBadge.tsx
   ```

3. **Começar Forja `/admin/transparencia`**
   ```bash
   # Em /home/enio/forja
   mkdir -p src/app/admin/transparencia
   ```

---

## ✅ Critérios de Aceitação

### Funcional
- [ ] Timeline funcional com dados reais
- [ ] Auto-refresh 30s funcionando
- [ ] Filtros (sistema, agente, status, data)
- [ ] Search full-text
- [ ] Alertas em tempo real (Telegram)
- [ ] Drill-down: evento → logs → código

### Performance
- [ ] Página carrega < 2s
- [ ] Logs stream sem lag
- [ ] Queries < 500ms

### Documentação
- [ ] Este arquivo (TIMELINE_SYSTEM_IMPLEMENTATION_PLAN.md) ✅
- [ ] HARVEST.md Pattern #10: Admin Transparency
- [ ] TASKS.md com TIMELINE-001 a TIMELINE-012

---

## 🎯 Value Proposition

| Antes | Depois |
|-------|--------|
| ❌ Caixa preta — sem visibility | ✅ Transparência total em tempo real |
| ❌ Sem rastreamento de eventos | ✅ Timeline de tudo (reports, deploys, agentes, logs) |
| ❌ Debugging manual (logs espalhados) | ✅ Drill-down automático: evento → logs → código |
| ❌ Sem alertas de falhas | ✅ Alertas em tempo real via Telegram |
| ❌ Métricas fragmentadas | ✅ Dashboard unificado (Recharts + KPIs) |

---

## 📝 Referências

- FORJA: `/home/enio/forja/docs/TRANSPARENCY_RADICAL_PRD.md`
- 852: `/home/enio/852/src/app/admin/telemetry/`
- Carteira Livre: `/home/enio/carteira-livre/src/services/admin-events.ts`

---

## Estado do Projeto

- [x] Plano documentado (este arquivo)
- [ ] FASE 1: Fundação Supabase
- [ ] FASE 2: Forja implementação
- [ ] FASE 3: 852 refinamento
- [ ] FASE 4: Carteira Livre padrão
- [ ] FASE 5: Disseminação ecosystem
- [ ] `/disseminate` → sync todos repos

**Início: Agora! 🚀**
