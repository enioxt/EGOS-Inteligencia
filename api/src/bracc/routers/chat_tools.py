"""OpenRouter function-calling tool definitions for EGOS Inteligência chat agent.

27 tools covering: Neo4j graph (+ path finder), Portal da Transparência, DataJud, BNMP,
Querido Diário, PNCP, OAB, OpenCNPJ, Brave Search, and more.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_entities",
            "description": "Pesquisa entidades no grafo Neo4j por nome, CNPJ, ou termo. Retorna empresas, sanções, contratos, embargos, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Termo de busca: nome de empresa, CNPJ, ou palavra-chave"},
                    "entity_type": {"type": "string", "description": "Filtro opcional: company, sanction, contract, embargo, person, election, finance", "enum": ["company", "sanction", "contract", "embargo", "person", "election", "finance", "convenio", "publicoffice"]},
                    "limit": {"type": "integer", "description": "Máximo de resultados (1-20)", "default": 8},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_graph_stats",
            "description": "Retorna estatísticas gerais do grafo: total de nós, relacionamentos, contagem por tipo de entidade.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_entity_connections",
            "description": "Busca conexões/relacionamentos de uma entidade específica no grafo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity_id": {"type": "string", "description": "ID da entidade (elementId do Neo4j)"},
                },
                "required": ["entity_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_connection_path",
            "description": "Descobre conexões ocultas entre duas entidades (pessoas, empresas, sanções) através de múltiplos graus de separação. Busca caminhos no grafo: A é sócio de B, que doou para C, que tem contrato com D. Útil para investigações de rede.",
            "parameters": {
                "type": "object",
                "properties": {
                    "entity_a": {"type": "string", "description": "Nome ou CNPJ da primeira entidade (ex: 'GRUPO PATENSE', 'JOSE DA SILVA')"},
                    "entity_b": {"type": "string", "description": "Nome ou CNPJ da segunda entidade (ex: 'BNDES', 'PETROBRAS')"},
                    "max_depth": {"type": "integer", "description": "Graus de separação máximos (1-6). Default: 4. Mais graus = busca mais profunda mas mais lenta.", "default": 4},
                },
                "required": ["entity_a", "entity_b"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Pesquisa na web por noticias, investigacoes, denuncias, materias de jornais sobre empresas, politicos, cidades. Use para encontrar informacoes atuais que nao estao no grafo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Termo de busca (ex: 'investigacao prefeito Uberlandia', 'denuncia empresa X CNPJ')"},
                    "max_results": {"type": "integer", "description": "Maximo de resultados (1-10)", "default": 5},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_emendas",
            "description": "Busca emendas parlamentares direcionadas a um municipio. Mostra quanto dinheiro federal foi destinado via emendas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "municipio": {"type": "string", "description": "Nome do municipio (ex: Uberlandia, Sao Paulo, Patos de Minas)"},
                    "uf": {"type": "string", "description": "Sigla do estado (ex: MG, SP, RJ)"},
                    "ano": {"type": "integer", "description": "Ano de referencia", "default": 2024},
                },
                "required": ["municipio"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_transferencias",
            "description": "Busca transferencias federais (convenios, repasses) para um municipio. Mostra o fluxo de dinheiro federal para a cidade.",
            "parameters": {
                "type": "object",
                "properties": {
                    "municipio": {"type": "string", "description": "Nome do municipio"},
                    "uf": {"type": "string", "description": "Sigla do estado"},
                    "ano": {"type": "integer", "description": "Ano de referencia", "default": 2024},
                },
                "required": ["municipio"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_ceap",
            "description": "Busca gastos CEAP (Cota para Exercicio da Atividade Parlamentar) de deputados. Mostra despesas com passagens, combustivel, alimentacao, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "parlamentar": {"type": "string", "description": "Nome do parlamentar (ex: 'Joao Silva')"},
                    "uf": {"type": "string", "description": "Sigla do estado para filtrar deputados"},
                    "ano": {"type": "integer", "description": "Ano de referencia", "default": 2024},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_pep_city",
            "description": "Busca pessoas politicamente expostas (PEPs) de uma cidade: deputados, prefeito, vereadores, investigados. Retorna deputados federais do estado e noticias sobre politicos locais.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cidade": {"type": "string", "description": "Nome da cidade (ex: Uberlandia, Patos de Minas)"},
                    "uf": {"type": "string", "description": "Sigla do estado (ex: MG, SP)"},
                },
                "required": ["cidade"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_gazettes",
            "description": "Busca em diarios oficiais municipais via Querido Diario (Open Knowledge Brasil). Encontra licitacoes, contratos, nomeacoes, decretos publicados no diario oficial da cidade.",
            "parameters": {
                "type": "object",
                "properties": {
                    "municipio": {"type": "string", "description": "Nome do municipio (ex: Uberlandia, Sao Paulo)"},
                    "query": {"type": "string", "description": "Termo de busca no diario oficial (ex: 'licitacao', 'contrato', nome de empresa)"},
                    "max_results": {"type": "integer", "description": "Maximo de resultados (1-10)", "default": 5},
                },
                "required": ["municipio"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cnpj_info",
            "description": "Busca informacoes de empresa por CNPJ: razao social, socios, capital social, CNAE, situacao cadastral. Use para investigar fornecedores encontrados no CEAP ou em contratos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cnpj": {"type": "string", "description": "CNPJ da empresa (com ou sem formatacao, ex: 12.345.678/0001-90 ou 12345678000190)"},
                },
                "required": ["cnpj"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_votacoes",
            "description": "Busca votacoes nominais na Camara dos Deputados. Mostra como cada deputado votou em proposicoes. Sem nome de parlamentar, lista votacoes recentes com placar (sim/nao/abstencao).",
            "parameters": {
                "type": "object",
                "properties": {
                    "parlamentar": {"type": "string", "description": "Nome do deputado para ver como votou (opcional)"},
                    "proposicao": {"type": "string", "description": "Tema ou numero da proposicao (opcional)"},
                    "ano": {"type": "integer", "description": "Ano de referencia", "default": 2024},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_servidores",
            "description": "Busca servidores publicos federais: nome, salario, cargo, orgao. Portal da Transparencia oficial.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string", "description": "Nome do servidor"},
                    "cpf": {"type": "string", "description": "CPF do servidor (opcional)"},
                    "orgao": {"type": "string", "description": "Orgao de exercicio (opcional)"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_licitacoes",
            "description": "Busca licitacoes do governo federal: pregoes, concorrencias, dispensas. Filtro por UF e ano.",
            "parameters": {
                "type": "object",
                "properties": {
                    "orgao": {"type": "string", "description": "Codigo do orgao (opcional)"},
                    "uf": {"type": "string", "description": "UF (ex: SP, MG, RJ)"},
                    "ano": {"type": "integer", "description": "Ano de referencia", "default": 2024},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_cpgf",
            "description": "Busca gastos com cartao corporativo do governo (CPGF). Restaurantes, hoteis, compras. Investigue gastos suspeitos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string", "description": "Nome do portador do cartao"},
                    "orgao": {"type": "string", "description": "Codigo do orgao"},
                    "mes": {"type": "integer", "description": "Mes (1-12)"},
                    "ano": {"type": "integer", "description": "Ano", "default": 2024},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_viagens",
            "description": "Busca viagens a servico do governo: diarias, passagens, destinos. Investigue viagens frequentes ou caras.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string", "description": "Nome do servidor que viajou"},
                    "orgao": {"type": "string", "description": "Codigo do orgao"},
                    "ano": {"type": "integer", "description": "Ano", "default": 2024},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_contratos",
            "description": "Busca contratos do governo federal: fornecedor, valor, vigencia. Investigue aditivos e sobrepreco.",
            "parameters": {
                "type": "object",
                "properties": {
                    "orgao": {"type": "string", "description": "Codigo do orgao"},
                    "fornecedor": {"type": "string", "description": "Nome do fornecedor"},
                    "ano": {"type": "integer", "description": "Ano", "default": 2024},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_sancoes",
            "description": "Busca empresas sancionadas (CEIS - inidoneas, CNEP - punidas). Empresa sancionada ganhando contrato = irregularidade.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cnpj": {"type": "string", "description": "CNPJ da empresa"},
                    "nome": {"type": "string", "description": "Nome da empresa"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_processos",
            "description": "Busca processos judiciais no DataJud (CNJ). Todos os tribunais do Brasil. Busque por numero, classe (recuperacao judicial, improbidade) ou recentes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "numero_processo": {"type": "string", "description": "Numero do processo (formato CNJ)"},
                    "nome_parte": {"type": "string", "description": "Nome de uma das partes (limitado)"},
                    "tribunal": {"type": "string", "description": "Tribunal: TJSP, TJRJ, TJMG, TRF1-6, STJ, TST, etc.", "default": "TJSP"},
                    "classe": {"type": "string", "description": "Classe processual: Recuperacao Judicial, Acao de Improbidade, Execucao Fiscal, etc."},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "bnmp_mandados",
            "description": "Busca mandados de prisao no BNMP (Banco Nacional de Mandados de Prisao - CNJ). Verifica se pessoa tem mandado ativo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string", "description": "Nome completo da pessoa"},
                },
                "required": ["nome"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "procurados_lookup",
            "description": "Busca pessoas procuradas pela Policia Federal e Interpol Brasil.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string", "description": "Nome da pessoa procurada"},
                },
                "required": ["nome"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lista_suja_lookup",
            "description": "Consulta a Lista Suja do Trabalho Escravo (MTE). Verifica se empresa ou empregador foi flagrado com trabalho analogo a escravidao.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string", "description": "Nome do empregador ou empresa"},
                    "uf": {"type": "string", "description": "Sigla do estado (opcional)"},
                },
                "required": ["nome"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "pncp_licitacoes",
            "description": "Busca licitacoes no PNCP (Portal Nacional de Contratacoes Publicas). Inclui TODAS as esferas: federal, estadual e municipal.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cnpj_orgao": {"type": "string", "description": "CNPJ do orgao contratante"},
                    "uf": {"type": "string", "description": "Sigla do estado (ex: SP, MG)"},
                    "data_inicio": {"type": "string", "description": "Data inicio (YYYYMMDD)", "default": "20240101"},
                    "data_fim": {"type": "string", "description": "Data fim (YYYYMMDD)", "default": "20241231"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "oab_advogado",
            "description": "Consulta advogado pelo numero OAB ou nome. Verifica se inscricao esta ativa, seccional, situacao.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string", "description": "Nome do advogado"},
                    "numero_oab": {"type": "string", "description": "Numero de inscricao OAB"},
                    "seccional": {"type": "string", "description": "Seccional OAB (ex: SP, RJ, MG)"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "opencnpj",
            "description": "Consulta CNPJ via OpenCNPJ (API publica gratuita). Retorna dados cadastrais completos: razao social, socios (QSA), CNAEs, capital social, situacao cadastral. Use como alternativa/complemento a cnpj_info.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cnpj": {"type": "string", "description": "CNPJ da empresa (com ou sem formatacao)"},
                },
                "required": ["cnpj"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cypher_query",
            "description": "Executa query Cypher READ-ONLY no Neo4j. Use para consultas analiticas que os outros tools nao cobrem: top N por criterio, contagens, agregacoes, cruzamentos. Labels disponiveis: Company, Person, Sanction, Contract, PublicOffice, Embargo, Election, Amendment, Convenio, PEPRecord, GovCardExpense, GovTravel, BarredNGO. Propriedades comuns: name, razao_social, cnpj, cpf, source, value, date. Relacionamentos: SOCIO_DE, CONTRATADA_POR, SANCIONADA_POR, RECEBEU_EMENDA, VIAJOU_PARA. SEMPRE use LIMIT (max 50).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Query Cypher read-only (MATCH/RETURN apenas). Ex: MATCH (c:Company)-[:SOCIO_DE]-(p:Person) RETURN c.razao_social, p.name LIMIT 10"},
                    "params": {"type": "object", "description": "Parametros opcionais para a query ($nome, $cnpj, etc.)"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "data_summary",
            "description": "Retorna resumo dinamico do sistema: total de nos, relacionamentos, fontes de dados, tipos de entidades com contagem, numero de ferramentas. Use para responder perguntas sobre o que o sistema tem/sabe.",
            "parameters": {"type": "object", "properties": {}},
        },
    },

]
