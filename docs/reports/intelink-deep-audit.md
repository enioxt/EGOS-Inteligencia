# Auditoria Profunda: Intelink vs EGOS Inteligência

> **Data:** 02/03/2026 | **Objetivo:** Mapear TODAS as features do Intelink e identificar o que falta no EGOS Intel

---

## System Map — Intelink (44 páginas + 135 API routes)

### Páginas (Frontend)

| # | Página | Função | EGOS Intel? | Prioridade |
|---|--------|--------|-------------|-----------|
| 1 | `/` (Landing) | Landing page | ✅ Tem | — |
| 2 | `/login` | Autenticação | ✅ Tem | — |
| 3 | `/auth` | Auth callback | ✅ Tem | — |
| 4 | `/dashboard` | Painel principal | ✅ Tem | — |
| 5 | `/chat` | Chat AI investigativo | ✅ Tem (18 tools) | — |
| 6 | `/chat/[sessionId]` | Chat com histórico | ⚠️ Parcial (localStorage) | P1 |
| 7 | `/graph/[id]` | Visualização de grafo | ✅ Tem | — |
| 8 | `/graph/[id]/3d` | **Grafo 3D** | ❌ NÃO TEM | P2 |
| 9 | `/analytics` | Dashboard analytics | ✅ Tem (recém-criado) | — |
| 10 | `/activity` | **Feed de atividades** | ❌ NÃO TEM | P1 |
| 11 | `/reports` | **Geração de relatórios** | ❌ NÃO TEM (apenas markdown) | P1 |
| 12 | `/investigation/new` | Nova investigação | ✅ Tem | — |
| 13 | `/investigation/[id]` | Investigação detalhada | ✅ Tem | — |
| 14 | `/investigation/[id]/history` | **Histórico de investigação** | ❌ NÃO TEM | P2 |
| 15 | `/investigation/[id]/reports` | **Relatórios de investigação** | ❌ NÃO TEM | P1 |
| 16 | `/profile` | Perfil do usuário | ❌ NÃO TEM | P2 |
| 17 | `/demo` | Demonstração | ❌ N/A (nosso é público) | — |
| 18 | `/offline` | Modo offline | ❌ NÃO TEM | P3 |
| 19 | `/jobs` | **Fila de processamento** | ❌ NÃO TEM | P2 |
| 20 | `/equipe` | Gestão de equipe | ❌ N/A (policial) | — |
| 21 | `/central` | Central de inteligência | ✅ Parcial (Dashboard) | — |
| 22 | `/central/alertas` | **Sistema de alertas** | ⚠️ Tem API, falta frontend | P1 |
| 23 | `/central/analise-vinculos` | **Análise de vínculos** | ✅ Tem (graph explorer) | — |
| 24 | `/central/auditoria` | **Auditoria de ações** | ❌ NÃO TEM | P2 |
| 25 | `/central/capabilities` | Capacidades do sistema | ❌ NÃO TEM | P3 |
| 26 | `/central/configuracoes` | Configurações | ❌ NÃO TEM | P3 |
| 27 | `/central/delegacias` | Delegacias | ❌ N/A (policial) | — |
| 28 | `/central/documentos` | **Gestão de documentos** | ❌ NÃO TEM | P2 |
| 29 | `/central/entidades` | Lista de entidades | ✅ Tem (Search) | — |
| 30 | `/central/equipe` | Equipe policial | ❌ N/A (policial) | — |
| 31 | `/central/evidencias` | **Cadeia de evidências** | ❌ NÃO TEM | P1 |
| 32 | `/central/graph` | Grafo central | ✅ Tem | — |
| 33 | `/central/intelligence-lab` | **Lab de inteligência** | ❌ NÃO TEM | P2 |
| 34 | `/central/membros` | Membros | ❌ N/A (policial) | — |
| 35 | `/central/operacoes` | Operações | ❌ N/A (policial) | — |
| 36 | `/central/permissoes` | Permissões | ❌ N/A (policial) | — |
| 37 | `/central/qualidade` | Qualidade de dados | ❌ NÃO TEM | P2 |
| 38 | `/central/saude` | **Saúde do sistema** | ⚠️ Tem API /meta/stats | P2 |
| 39 | `/central/vinculos` | Vínculos | ✅ Tem (Graph) | — |
| 40 | `/central/unit/[id]/graph` | Grafo por unidade | ❌ N/A (policial) | — |
| 41 | `/admin/audit` | Auditoria admin | ❌ NÃO TEM | P3 |
| 42 | `/admin/sessions` | Sessões ativas | ❌ NÃO TEM | P3 |
| 43 | `/admin/telemetry` | Telemetria | ❌ NÃO TEM | P2 |

### Resumo de Páginas

| Status | Count | % |
|--------|-------|---|
| ✅ Já temos | 14 | 33% |
| ⚠️ Parcial | 3 | 7% |
| ❌ Falta (relevante) | 15 | 35% |
| ❌ N/A (policial) | 11 | 25% |

---

### API Routes Mais Importantes (135 total)

| Categoria | Routes | EGOS Intel? | Destaques |
|-----------|--------|-------------|-----------|
| **Analysis** | 6 | ⚠️ Parcial | anchoring, CRIT, diligences, MO, risk, summary |
| **Chat** | 8 | ✅ Tem | conversations, history, PDF export, vision, share |
| **Documents** | 7 | ❌ NÃO TEM | upload, extract, OCR, embeddings, guardian, batch |
| **Entities** | 8 | ✅ Tem | merge, cleanup-duplicates, generate-relationships |
| **Reports** | 4 | ❌ NÃO TEM | generate, entity report, unified report |
| **Link Prediction** | 2 | ❌ NÃO TEM | accuracy, predict |
| **Legal** | 2 | ❌ NÃO TEM | detect, sync (legislação) |
| **OCR** | 1 | ❌ NÃO TEM | Extração de texto de imagens |
| **Audio/Transcribe** | 2 | ❌ NÃO TEM | Transcrição de áudio (Whisper?) |
| **Gamification** | 1 | ❌ NÃO TEM | Stats, leaderboard |
| **Findings** | 1 | ❌ NÃO TEM | Achados de investigação |
| **Debate** | 1 | ❌ NÃO TEM | Debate AI (análise contraditória) |
| **Rho** | 6 | ❌ NÃO TEM | Health score, alerts, history |
| **Notifications** | 1 | ❌ NÃO TEM | Push notifications |
| **Compliance** | 1 | ❌ NÃO TEM | Justificação de compliance |
| **Journeys** | 3 | ✅ Tem | compare, share |
| **Telemetry** | 3 | ⚠️ Parcial | ingestion, export |
| **Members/Auth** | 15+ | ❌ N/A | OTP, roles, permissions |

---

## Top 10 Features Para Adotar (Prioridade)

### P0 — Impacto Máximo, Esforço Médio

1. **Report Generation** (`/reports` + `/api/reports/generate`)
   - Gera relatório completo de uma entidade automaticamente
   - PDF export com timeline, conexões, análise de risco
   - **Esforço:** 4h | **Impacto:** Alto (showcase para divulgação)

2. **Activity Feed** (`/activity` + `/api/activities`)
   - Timeline de ações: buscas, análises, relatórios gerados
   - Transparência do uso do sistema
   - **Esforço:** 3h | **Impacto:** Médio (engagement)

3. **Evidence Chain** (`/central/evidencias`)
   - Cadeia de custódia de evidências
   - Rastreabilidade de cada dado (de onde veio, quando)
   - **Esforço:** 4h | **Impacto:** Alto (credibilidade)

### P1 — Importante, Esforço Maior

4. **Chat Vision** (`/api/chat/vision`)
   - Upload de imagem no chat → AI analisa (OCR, extração de dados)
   - Útil para analisar documentos, notas fiscais, contratos
   - **Esforço:** 6h | **Impacto:** Alto

5. **Alert System Frontend** (`/central/alertas`)
   - Já temos a API `/monitor/sanctions/recent`
   - Falta: frontend com notificações, filtros, histórico
   - **Esforço:** 3h | **Impacto:** Médio

6. **Analysis Suite** (`/api/analysis/*`)
   - Anchoring: análise de ancoragem (viés cognitivo)
   - CRIT: Critical thinking assessment
   - Risk: Score de risco da entidade
   - MO: Modus Operandi detection
   - **Esforço:** 8h | **Impacto:** Alto (diferencial)

### P2 — Nice to Have

7. **Grafo 3D** (`/graph/[id]/3d`)
8. **Document Management** (`/central/documentos`)
9. **Intelligence Lab** (`/central/intelligence-lab`)
10. **Link Prediction** (`/api/link-prediction`)

---

## Features do egos-lab Para Trazer

| Feature | Onde está | Aplicável? |
|---------|----------|-----------|
| **Agent Runtime** | `agents/runtime/runner.ts` | ❌ Não (egos-lab only) |
| **SSOT Auditor** | `agents/agents/ssot-auditor.ts` | ❌ Não |
| **UI Designer Agent** | `agents/agents/ui-designer.ts` | ❌ Não |
| **Rho Score** | `scripts/rho.ts` | ✅ **SIM** — health score do sistema |
| **Eagle Eye (OSINT)** | `apps/eagle-eye/` | ✅ **SIM** — monitor de diários oficiais |
| **Telegram Bot** | `apps/telegram-bot/` | ✅ Já existe para EGOS Intel |
| **AI Client** | `packages/shared/ai-client.ts` | ⚠️ Parcial (usamos OpenRouter direto) |
| **Cost Tracking** | `packages/shared/ai-client.ts` | ✅ **SIM** — track custo por query |
| **Stitch Designs** | `docs/stitch/` | ❌ Design system (não aplicável) |

### Top 3 do egos-lab Para Trazer:

1. **Rho Score** — Score de saúde do sistema (uptime, coverage, data freshness)
2. **Eagle Eye** — Monitor automático de diários oficiais (gazette watcher)
3. **Cost Tracking** — Rastrear custo de cada query LLM

---

## Comparação com Palantir/NSA/Melhores do Mundo

| Capacidade | EGOS Intel | Palantir Gotham | NSA XKeyscore | i2 Analyst |
|-----------|-----------|----------------|---------------|-----------|
| **Grafo de entidades** | 317K nós | Bilhões | Trilhões | Milhões |
| **Fontes de dados** | 18 APIs + Neo4j | 100+ conectores | Classificado | 50+ |
| **AI/NLP** | Gemini 2.0 Flash | AIP (GPT-4+) | Classificado | Limitado |
| **Cross-reference** | ✅ Automático | ✅ Automático | ✅ Automático | ✅ Manual |
| **Link prediction** | ❌ | ✅ ML-based | ✅ | ❌ |
| **OCR/Documentos** | ❌ | ✅ | ✅ | ✅ |
| **Geolocalização** | ❌ | ✅ (GPS, celular) | ✅ (global) | ✅ |
| **Interceptação** | ❌ | ❌ | ✅ (SIGINT) | ❌ |
| **Financial intel** | ⚠️ (CPGF, contratos) | ✅ (SWIFT, bancos) | ✅ | ✅ |
| **Real-time** | ❌ | ✅ | ✅ | ❌ |
| **Acesso** | **PÚBLICO** | Gov/Militar | Top Secret | Polícia |
| **Custo** | **R$120/mês** | ~US$10M/ano | Classificado | ~US$50K/lic |
| **Open source** | ✅ **SIM** | ❌ | ❌ | ❌ |

### O Que Nos Falta vs Palantir (Roadmap)

1. **Link Prediction (ML)** — prever conexões que ainda não existem
2. **OCR Pipeline** — extrair texto de PDFs, imagens, documentos
3. **Real-time Monitoring** — alertas quando novos dados surgem
4. **Financial Intelligence** — integrar dados bancários (quando disponíveis)
5. **Geospatial Analysis** — mapas com localização de entidades
6. **Temporal Analysis** — timeline visual de eventos
7. **Anomaly Detection** — detectar padrões anormais automaticamente
8. **Multi-language NLP** — análise de documentos em múltiplos idiomas

---

*"Não precisamos competir com Palantir em escala. Precisamos democratizar o acesso."*
