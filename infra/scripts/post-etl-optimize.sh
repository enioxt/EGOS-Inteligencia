#!/bin/bash
# Post-ETL Optimization — Create indexes + fulltext after ETL completes
# Run AFTER ETL Phase 3 finishes and entity linking hooks complete
set -euo pipefail

NEO4J_PASS='BrAcc2026EgosNeo4j!'
CYPHER="docker exec bracc-neo4j cypher-shell -u neo4j -p $NEO4J_PASS"

echo '=== Post-ETL Index Creation ==='
echo 'Creating B-Tree indexes...'

$CYPHER 'CREATE INDEX company_cnpj IF NOT EXISTS FOR (c:Company) ON (c.cnpj)'
$CYPHER 'CREATE INDEX company_cnpj_basico IF NOT EXISTS FOR (c:Company) ON (c.cnpj_basico)'
$CYPHER 'CREATE INDEX company_name IF NOT EXISTS FOR (c:Company) ON (c.name)'
$CYPHER 'CREATE INDEX company_uf IF NOT EXISTS FOR (c:Company) ON (c.uf)'
$CYPHER 'CREATE INDEX company_cnae IF NOT EXISTS FOR (c:Company) ON (c.cnae_principal)'
$CYPHER 'CREATE INDEX person_cpf IF NOT EXISTS FOR (p:Person) ON (p.cpf)'
$CYPHER 'CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.name)'
$CYPHER 'CREATE INDEX partner_doc IF NOT EXISTS FOR (p:Partner) ON (p.document)'
$CYPHER 'CREATE INDEX sanction_cnpj IF NOT EXISTS FOR (s:Sanction) ON (s.cnpj)'
$CYPHER 'CREATE INDEX person_cpf_middle6 IF NOT EXISTS FOR (p:Person) ON (p.cpf_middle6)'
$CYPHER 'CREATE INDEX partner_name_doc IF NOT EXISTS FOR (p:Partner) ON (p.name, p.doc_partial)'

echo 'Creating fulltext indexes...'
$CYPHER 'CREATE FULLTEXT INDEX company_name_ft IF NOT EXISTS FOR (n:Company) ON EACH [n.name, n.name_fantasy]'
$CYPHER 'CREATE FULLTEXT INDEX person_name_ft IF NOT EXISTS FOR (n:Person) ON EACH [n.name]'

echo ''
echo '=== Verifying indexes ==='
$CYPHER 'SHOW INDEXES YIELD name, state, type WHERE state <> "ONLINE" RETURN name, state, type'

echo ''
echo '=== Node counts ==='
$CYPHER 'MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count ORDER BY count DESC LIMIT 10'

echo ''
echo '=== Relationship counts ==='
$CYPHER 'MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count ORDER BY count DESC LIMIT 10'

echo ''
echo 'Done! Run neo4j-memory-upgrade.sh next for optimal query performance.'
