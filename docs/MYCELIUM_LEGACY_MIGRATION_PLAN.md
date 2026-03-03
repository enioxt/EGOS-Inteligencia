# Mycelium — Plano de Migração de Legado (Corte de Veracidade)

## Resposta curta
Sim — **já analisamos e documentamos** a estratégia de transição suave para o legado, sem retrabalho total.

Este documento formaliza o plano de **"Corte de Veracidade"** para evoluir do estado atual para auditoria forte por hash/proveniência.

## Objetivo
Migrar para trilha auditável (hash + proveniência) em um grafo já populado, sem paralisar operação e sem reprocessar tudo de uma vez.

## Estratégia aprovada

### 1) Legacy Tagging (Selo Cinza)
- Marcar nós sem hash com `audit_status: "legacy"`.
- Comunicar que o dado é útil, porém anterior ao protocolo de não repúdio.

Implementação pronta em:
- `scripts/legacy_tagging_backfill.cypher`

### 2) Backfill de Proveniência Genérica
- Criar um único nó `DataSource` legado (`legacy-pre-mycelium-audit`).
- Vincular nós legados via `(:Entity)-[:PROVENANCE {trust_level: "low"}]->(:DataSource)`.
- Evita órfãos de proveniência no histórico pré-auditoria.

### 3) Lazy Update (cura orgânica)
- ETLs novos/atualizados passam a escrever `audit_hash` + `PROVENANCE` de origem real.
- No `MERGE` de entidade existente:
  - quando houver hash novo, remover condição de legado (`audit_status`).
  - registrar metadados de atualização (`audit_upgraded_at`, versão de protocolo).
- Resultado: o banco vai migrando de forma incremental, com custo previsível.

### 4) Prioridade de reingestão (quando vale refazer)
Reprocessar primeiro os domínios de maior risco/valor investigativo:
1. **Sanções (CEIS/CEPIM etc.)** — maior criticidade jurídica.
2. **Sócios/CNPJ** — altíssimo impacto no cruzamento de vínculos.

## Execução recomendada

### Passo A — rodar backfill legado
```bash
cypher-shell -a bolt://localhost:7687 -u neo4j -p "$NEO4J_PASSWORD" -f scripts/legacy_tagging_backfill.cypher
```

### Passo B — validar cobertura
Critérios mínimos após backfill:
- todo nó sem `audit_hash` deve estar com `audit_status = "legacy"`.
- todo nó sem `audit_hash` deve ter uma aresta `PROVENANCE` para o nó legado.

### Passo C — habilitar upgrade no ETL
No ponto comum de escrita (base ETL / writer compartilhado):
- gerar `audit_hash` para carga nova;
- manter proveniência específica da fonte;
- ao atualizar entidade legada, limpar `audit_status = "legacy"` e marcar upgrade.

## Exemplo lógico de upgrade no merge
```python
if incoming.audit_hash:
    entity["audit_hash"] = incoming.audit_hash
    entity["audit_protocol"] = "v2"
    entity["audit_upgraded_at"] = now_iso
    entity.pop("audit_status", None)  # remove legado quando auditado
```

## Guardrails
- **Não apagar dados legados.**
- **Não prometer não repúdio retroativo** quando a evidência original não existir.
- **Versionar protocolo** (`audit_protocol`) para distinguir legado, fallback e auditado forte.

## Decisão prática
- **Não refazer tudo do zero.**
- **Aplicar corte de veracidade agora.**
- **Migrar incrementalmente por atualização real de fontes.**
