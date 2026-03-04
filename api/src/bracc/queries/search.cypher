CALL db.index.fulltext.queryNodes("entity_search", $query)
YIELD node, score
WITH node, score, labels(node) AS node_labels
WHERE NONE(label IN node_labels WHERE label IN ['User', 'Investigation', 'Annotation', 'Tag'])
  AND ($entity_type IS NULL OR ANY(label IN node_labels WHERE toLower(label) = $entity_type))
  AND ($is_pep = false OR toLower(toString(node.source)) CONTAINS 'pep')
  AND ($has_sanctions = false OR toLower(toString(node.source)) CONTAINS 'ceis' OR toLower(toString(node.source)) CONTAINS 'cnep')
  AND ($has_contracts = false OR toLower(toString(node.source)) CONTAINS 'compras' OR toLower(toString(node.source)) CONTAINS 'contrat')
  AND ($city IS NULL OR $city = '' OR toLower(node.city) = toLower($city) OR toLower(node.municipio) = toLower($city))
  AND ($state IS NULL OR $state = '' OR toLower(node.state) = toLower($state) OR toLower(node.uf) = toLower($state))
RETURN node, score, node_labels,
       elementId(node) AS node_id,
       coalesce(node.cpf, node.cnpj, node.contract_id, node.sanction_id, node.amendment_id, node.cnes_code, node.finance_id, node.embargo_id, node.school_id, node.convenio_id, node.stats_id, elementId(node)) AS document_id
ORDER BY score DESC
SKIP $skip
LIMIT $limit
