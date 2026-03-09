#!/bin/bash
# Neo4j Memory Upgrade — Apply after ETL completes
# Optimized for 48GB Contabo VPS with 55M+ nodes
set -euo pipefail

echo '=== Neo4j Memory Upgrade ==='
echo 'Current config:'
docker exec bracc-neo4j cat /var/lib/neo4j/conf/neo4j.conf 2>/dev/null | grep -E 'heap|pagecache' || echo '(defaults)'

cd /opt/bracc/infra

if grep -q 'NEO4J_server_memory' docker-compose.yml; then
  echo 'Memory already configured in docker-compose.yml'
  exit 0
fi

echo ''
echo 'To apply, add these to neo4j environment in docker-compose.yml:'
echo '  NEO4J_server_memory_heap_initial__size: 8g'
echo '  NEO4J_server_memory_heap_max__size: 16g'
echo '  NEO4J_server_memory_pagecache_size: 22g'
echo ''
echo 'Then: docker compose restart neo4j'
echo 'WARNING: Neo4j will restart. Wait for health check before querying.'
