# Mapeamento do que já existe no EGOS Inteligência para a nova ferramenta

## 1) Reuso direto de módulos atuais

## APIs e capacidades já existentes
- Chat (`/api/v1/chat`)
- Conversas (`/api/v1/conversations`)
- Busca (`/api/v1/search`)
- Entidade/Conexões/Grafo (`/api/v1/entity`, `/api/v1/graph`)
- Padrões e baseline (`/api/v1/patterns`, `/api/v1/baseline`)
- Investigations e compartilhamento (`/api/v1/investigation`, `/api/v1/shared`)
- Meta/monitor/analytics/activity (`/api/v1/meta`, `/api/v1/monitor`, `/api/v1/analytics`, `/api/v1/activity`)

## Ferramentas de inteligência já presentes
- Tooling de busca em grafo + fontes públicas
- Estrutura de análise de vínculos/padrões
- Base de dados relacional em grafo + cache

## Regras de conformidade já presentes
- Controles de modo público
- Proteções LGPD/masking
- Guardas de exposição de dados

---

## 2) O que falta para o cenário pedido na conversa

1. Módulo formal de **email ingestion** com roteamento inteligente.
2. Módulo de **notificação omnichannel** (WhatsApp/e-mail/push) com templates.
3. Camada de **workflow de aprovação** centrada em operações ERP (N-de-M).
4. Contratos comuns para interoperar com egos-lab e Carteira Livre.
5. Dashboard operacional orientado ao público leigo com acessibilidade reforçada.

---

## 3) Estratégia de adaptação sem retrabalho

1. Preservar endpoints maduros e criar novos serviços por composição.
2. Evitar duplicar engine de chat; expandir tool runner com policies.
3. Introduzir eventos de domínio para sincronização cross-repo.
4. Reusar observabilidade e auditoria existentes como trilha única.

---

## 4) Backlog técnico priorizado

## Prioridade Alta
- `email-ingestion-service` (inbound + parsing + classificação + actions)
- `notification-service` (WhatsApp/e-mail, templates, retries)
- `approval-workflows` (2-de-2 e políticas configuráveis)
- `accessibility-pass` no front (tokens, componentes, testes)

## Prioridade Média
- `worker-spec` DSL + editor no dashboard
- catálogo de políticas por tenant
- cockpit de custo IA por tenant

## Prioridade Contínua
- hardening LGPD
- testes de segurança por endpoint
- rastreabilidade de decisões do agente
