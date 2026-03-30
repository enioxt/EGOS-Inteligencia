MATCH (i:Investigation {share_token: $token})-[:HAS_TAG]->(t:Tag)
RETURN t.id AS id,
       i.id AS investigation_id,
       t.name AS name,
       t.color AS color
ORDER BY t.name
LIMIT 1000
