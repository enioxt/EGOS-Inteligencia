# Plano inicial de Persistência & Interoperabilidade

## Objetivo

Garantir que os três repositórios compartilhem estado e conhecimento sem perda de contexto:

- EGOS Inteligência
- egos-lab
- Carteira Livre

## Princípios

1. **Source of truth explícito por domínio**
2. **Schemas versionados**
3. **Eventos imutáveis + projeções derivadas**
4. **Idempotência na ingestão**
5. **Compatibilidade progressiva entre versões**

## Proposta de modelo

## A) Contrato canônico de entidades

Cada módulo deve mapear para um contrato canônico mínimo:

- `entity_type` (company, person, contract, sanction, transfer, asset, process)
- `entity_key` (identificador estável interno)
- `source_system` (repo/módulo de origem)
- `source_reference` (id original)
- `valid_from` / `valid_to`
- `sensitivity_level` (public, restricted)
- `lgpd_policy` (mask, deny, allow)

## B) Trilha de eventos de integração

Formato sugerido (JSON):

- `event_id`
- `event_type` (created, updated, merged, linked)
- `occurred_at`
- `producer` (repo + módulo)
- `entity_type`
- `entity_key`
- `payload`
- `schema_version`

## C) Persistência

- Grafo (Neo4j) para relacionamento e exploração
- Store analítica/tabular para métricas e histórico bruto (a definir com os demais repos)
- Cache (Redis) para aceleração de leitura

## D) Governança mínima

- Catálogo de fontes por módulo
- Política de retenção por tipo de dado
- Observabilidade de sync (latência, erro, duplicidade)
- Checklist LGPD por fluxo

---

## Backlog de integração quando os outros repositórios estiverem conectados

1. Inventário de módulos do `egos-lab`.
2. Inventário de módulos do `Carteira Livre`.
3. Matriz de overlap (o que já existe duplicado).
4. Definição de domínio líder por tema.
5. Contrato canônico v0.1 com validação cruzada.
6. Pipeline de sync inicial (pull + reconciliação).
7. Testes de consistência entre bases.
