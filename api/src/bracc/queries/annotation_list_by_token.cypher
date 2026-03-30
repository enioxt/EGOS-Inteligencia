MATCH (i:Investigation {share_token: $token})-[:HAS_ANNOTATION]->(a:Annotation)
RETURN a.id AS id,
       a.entity_id AS entity_id,
       i.id AS investigation_id,
       a.text AS text,
       a.created_at AS created_at
ORDER BY a.created_at DESC
LIMIT 1000
