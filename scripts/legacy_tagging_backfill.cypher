// Legacy tagging + provenance backfill for Mycelium audit migration
// Safe to run multiple times (idempotent where possible).

// 1) Create/refresh one generic legacy data source node.
MERGE (s:DataSource {slug: "legacy-pre-mycelium-audit"})
ON CREATE SET
  s.name = "Carga Legada Pre-Mycelium-Audit",
  s.description = "Dados ingeridos antes do protocolo de hash e não repúdio",
  s.created_at = datetime(),
  s.trust_level = "low"
SET s.last_migration_at = datetime();

// 2) Tag legacy records that do not yet have audit_hash.
// Uses transactional batching for large graphs.
CALL {
  MATCH (n)
  WHERE n.audit_hash IS NULL
    AND coalesce(n.audit_status, "") <> "legacy"
  SET n.audit_status = "legacy",
      n.audit_tagged_at = datetime(),
      n.audit_protocol = "v1_migration"
  RETURN count(n) AS updated_nodes
} IN TRANSACTIONS OF 10000 ROWS;

// 3) Link legacy records to the generic provenance source.
CALL {
  MATCH (s:DataSource {slug: "legacy-pre-mycelium-audit"})
  MATCH (n)
  WHERE n.audit_hash IS NULL
  MERGE (n)-[r:PROVENANCE]->(s)
  ON CREATE SET
    r.trust_level = "low",
    r.created_at = datetime(),
    r.reason = "legacy_backfill"
  RETURN count(r) AS relationships_linked
} IN TRANSACTIONS OF 10000 ROWS;

// 4) Validation snapshot.
MATCH (n)
WITH
  count(n) AS total_nodes,
  count(CASE WHEN n.audit_status = "legacy" THEN 1 END) AS legacy_nodes,
  count(CASE WHEN n.audit_hash IS NOT NULL THEN 1 END) AS audited_nodes
RETURN total_nodes, legacy_nodes, audited_nodes;
