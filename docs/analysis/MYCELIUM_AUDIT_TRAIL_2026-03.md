# Mycelium Audit Trail (Não Repúdio) — Plano de Evolução

## Problema

Hoje o Mycelium/ETL já registra linhagem operacional (`IngestionRun`), mas falta o nível de prova técnica de não repúdio para contestação futura (origem + integridade do dado bruto).

## Objetivo

Adicionar uma camada de auditoria que permita responder:
- de onde veio o dado (`source_url`),
- quando foi verificado (`verified_at`),
- qual o hash da linha bruta (`raw_line_hash`),
- e um fingerprint da fonte/coleta (`source_fingerprint`).

## Decisões de arquitetura

### 1) Metadados de auditoria por registro
No ETL, cada registro transformado passa a poder carregar:
- `raw_line_hash` (SHA-256 da linha canônica),
- `source_url`,
- `source_method` (api, bulk_download, scraping),
- `verified_at`,
- `audit_status` (`verified`),
- `source_fingerprint`.

### 2) Nó de proveniência no grafo (fase seguinte)
Para evitar redundância extrema em 141M nós, a próxima fase deve materializar `(:DataSource)` e relacionamentos de proveniência (`[:PROVENANCE]`) para entidades críticas.

### 3) Migração legada (sem retrabalho total)
- Marcar dados atuais como `audit_status = "legacy"` onde ainda não houver hash.
- Reprocessar com prioridade alta fontes críticas (sanções e CNPJ/sócios).
- Usar atualização incremental: conforme ETLs rodarem, os nós legados passam para `verified`.

## Entregas desta PR

- Base técnica adicionada no ETL para cálculo determinístico de hash e montagem de campos de auditoria (`bracc_etl.provenance`).
- Método utilitário no `Pipeline` base para padronizar uso em pipelines novos e antigos.
- Testes unitários de estabilidade do hash e dos campos de auditoria.

## Exemplo de payload

```json
{
  "name": "EMPRESA X",
  "audit": {
    "source_url": "https://dados.exemplo.gov.br/arquivo.csv",
    "raw_line_hash": "...",
    "source_method": "bulk_download",
    "verified_at": "2026-03-03T10:00:00Z",
    "audit_status": "verified"
  }
}
```

## Script de backfill sugerido (fase legada)

```cypher
MATCH (n)
WHERE n.audit_status IS NULL
SET n.audit_status = 'legacy';
```

> Observação: o relacionamento `[:PROVENANCE]` e `:DataSource` fica como próxima etapa de modelagem/rollout para não expandir escopo de forma arriscada.
