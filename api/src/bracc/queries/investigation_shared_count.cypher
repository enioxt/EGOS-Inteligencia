MATCH (i:Investigation)
WHERE i.share_token IS NOT NULL
RETURN count(i) AS total
