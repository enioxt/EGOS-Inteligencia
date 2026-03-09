# Catálogo de Fontes de Dados — EGOS Inteligência

**38 carregadas | 3 pipelines aguardando dados | 60+ ainda não construídas**
Última atualização: 2026-03-03

---

## 1. CARREGADAS (38 fontes)

Todas as fontes abaixo possuem pipelines ETL funcionais em `etl/src/bracc_etl/pipelines/` e estão carregadas no Neo4j de produção.

| # | Fonte | Pipeline | Nós Criados | Relacionamentos | Notas |
|---|-------|----------|-------------|-----------------|-------|
| 1 | CNPJ (Receita Federal) | `cnpj` | 53,6M Company, 1,98M Person | 24,6M SOCIO_DE | ~85GB descomprimido |
| 2 | TSE (Eleições + Doações) | `tse` | 7,1M Person, 101K Election | 8,2M DOOU, 2,93M CANDIDATO_EM | Histórico 2002-2024 |
| 3 | Transparência (Contratos) | `transparencia` | 38K Contract, 27,6K Amendment | 32K VENCEU, 29K AUTOR_EMENDA | Contratos federais |
| 4 | CEIS/CNEP (Sanções) | `sanctions` | 23,8K Sanction | 23,8K SANCIONADA | Empresas/pessoas impedidas |
| 5 | BNDES (Empréstimos) | `bndes` | 9,2K Finance | 8,7K RECEBEU_EMPRESTIMO | |
| 6 | PGFN (Dívida Ativa) | `pgfn` | 24M Finance | 24M DEVE | Dívida ativa da União |
| 7 | ComprasNet (Contratos) | `comprasnet` | 1,08M Contract | 1,07M VENCEU | Compras federais |
| 8 | TCU (Sanções de Auditoria) | `tcu` | 45K Sanction | 45K SANCIONADA | Inabilitados/inidôneos |
| 9 | TransfereGov | `transferegov` | 71K Amendment, 67K Convenio | 320K BENEFICIOU, 70K GEROU_CONVENIO | Transferências federais |
| 10 | RAIS (Estatísticas Trabalhistas) | `rais` | 29,5K LaborStats | -- | Agregado por CNAE+UF (sem CPF) |
| 11 | INEP (Educação) | `inep` | 224K Education | 18K MANTEDORA_DE | Censo educacional |
| 12 | DATASUS/CNES | `datasus` | 602K Health | 435K OPERA_UNIDADE | Cadastro de estabelecimentos de saúde |
| 13 | IBAMA (Embargos) | `ibama` | 79K Embargo | 79K EMBARGADA | Fiscalização ambiental |
| 14 | DOU (Diário Oficial) | `dou` | 3,98M DOUAct | 169K MENCIONOU, 13K PUBLICOU | Parquet via BigQuery |
| 15 | Câmara (Despesas) | `camara` | 4,6M Expense | 4,6M GASTOU, 4,9M FORNECEU | CEAP de deputados |
| 16 | Senado (Despesas) | `senado` | 272K Expense | 272K FORNECEU | CEAPS de senadores |
| 17 | ICIJ (Offshore Leaks) | `icij` | 4,8K OffshoreEntity, 6,6K OffshoreOfficer | 2,3K OFFICER_OF | Panama/Paradise/Pandora Papers |
| 18 | OpenSanctions (PEPs Globais) | `opensanctions` | 118K GlobalPEP | 7,6K GLOBAL_PEP_MATCH | Cruzamento por nome com entidades brasileiras |
| 19 | CVM (Processos) | `cvm` | 522 CVMProceeding | 1,1K CVM_SANCIONADA | Sanções de valores mobiliários |
| 20 | CVM Fundos | `cvm_funds` | 41K Fund | -- | Cadastro de fundos de investimento |
| 21 | Servidores Federais | *(transparencia)* | 635K PublicOffice | 636K RECEBEU_SALARIO | Servidores + remunerações |
| 22 | CEAF (Servidores Expulsos) | `ceaf` | 4,1K Expulsion | 4,1K EXPULSO | Demitidos por má conduta |
| 23 | CEPIM (ONGs Impedidas) | `cepim` | 3,6K BarredNGO | 3,6K IMPEDIDA | ONGs impedidas de convênios |
| 24 | CPGF (Cartões Corporativos) | `cpgf` | 1,46M GovCardExpense | -- | LGPD mascara CPFs |
| 25 | Viagens a Serviço | `viagens` | 3,71M GovTravel | -- | LGPD mascara CPFs |
| 26 | Renúncias Fiscais | `renuncias` | 291,8K TaxWaiver | 291,8K RECEBEU_RENUNCIA | R$414B+ em benefícios fiscais |
| 27 | Acordos de Leniência | `leniency` | 112 LeniencyAgreement | -- | Empresas que confessaram |
| 28 | BCB Penalidades | `bcb` | 3,5K BCBPenalty | -- | Multas a instituições financeiras |
| 29 | STF (Supremo Tribunal) | `stf` | 2,38M LegalCase | -- | Processos do Supremo |
| 30 | PEP CGU | `pep_cgu` | 133,8K PEPRecord | -- | Pessoas politicamente expostas |
| 31 | TSE Bens (Patrimônio) | `tse_bens` | 14,3M DeclaredAsset | 14,3M DECLAROU_BEM | Patrimônio declarado por candidatos |
| 32 | TSE Filiados | `tse_filiados` | 16,5M PartyMembership | -- | Histórico de filiação partidária |
| 33 | OFAC SDN | `ofac` | 39,2K InternationalSanction* | -- | Sanções do Tesouro dos EUA |
| 34 | Sanções UE | `eu_sanctions` | *(incluído acima)* | -- | Sanções consolidadas da UE |
| 35 | Sanções ONU | `un_sanctions` | *(incluído acima)* | -- | Sanções do Conselho de Segurança |
| 36 | Banco Mundial | `world_bank` | *(incluído acima)* | -- | Empresas impedidas |
| 37 | Holdings (derivado CNPJ) | `holdings` | -- | 59K HOLDING_DE | Derivado dos sócios CNPJ |
| 38 | SIOP (Emendas Orçamentárias) | `siop` | 71,1K Amendment | -- | Execução de emendas parlamentares |
| 39 | Senado CPIs | `senado_cpis` | 3 CPI | -- | Investigações parlamentares |

*\* InternationalSanction: 39,2K total entre OFAC + UE + ONU + Banco Mundial*

**Totais em produção (2026-03-03):** ~9,1M nós, ~34K relacionamentos carregados (ETL em andamento para completar 141M nós planejados).

---

## 2. PIPELINE EXISTE — DADOS PENDENTES (3 fontes)

| Fonte | Pipeline | Status | Bloqueio |
|-------|----------|--------|----------|
| PNCP (Licitações) | `pncp` | Baixando — 35 arquivos (2021-08→2024-06), em execução até 2026-02 | Tempo — API pagina por mês |
| SICONFI (Finanças Municipais) | `siconfi` | Baixando dados 2024 (~530K/700K linhas), pipeline corrigido (CSV não JSON) | Tempo — 5.570 municípios × 5 anos |
| CAGED (Movimentação Trabalhista) | `caged` | Pipeline reescrito como LaborStats agregado. Precisa re-download do FTP PDET | Dados públicos não têm CNPJ do empregador |

---

## 3. AINDA NÃO CONSTRUÍDAS (60+ fontes)

### 3.1 CGU / Portal da Transparência

| # | Fonte | Formato | Volume Est. | Nós/Rels | Valor | Notas |
|---|-------|---------|-------------|----------|-------|-------|
| 1 | Bolsa Família/BPC | CSV | ~20M | SocialBenefit | BAIXO | CPFs mascarados pela LGPD |

### 3.2 BCB / Banco Central

| # | Fonte | Formato | Volume Est. | Valor | Notas |
|---|-------|---------|-------------|-------|-------|
| 2 | BCB Multas | CSV | ~5K | ALTO | Multas administrativas |
| 3 | ESTBAN | CSV | ~500K/mês | BAIXO | Balancetes de agências bancárias |
| 4 | IF.data | CSV | ~2K trimestral | BAIXO | Métricas de instituições financeiras |
| 5 | BCB Liquidação | CSV | ~200 | MÉDIO | Instituições financeiras liquidadas |

### 3.3 Judiciário

| # | Fonte | Formato | Volume Est. | Valor | Notas |
|---|-------|---------|-------------|-------|-------|
| 6 | CNJ DataJud | API REST (chave self-service) | Dezenas de milhões | MUITO ALTO | Processos de todos os tribunais |
| 7 | STJ Dados Abertos | CSV/XML | ~500K | ALTO | Decisões do tribunal superior |
| 8 | CNCIAI (Improbidade) | API | ~10K | MUITO ALTO | Condenações por improbidade administrativa |
| 9 | CARF (Recursos Fiscais) | Estruturado | ~500K | MÉDIO | Decisões de recursos tributários federais |

### 3.4 Agências Reguladoras (11 fontes)

| # | Fonte | Formato | Volume Est. | Valor | Notas |
|---|-------|---------|-------------|-------|-------|
| 19 | ANP (Royalties Petróleo/Gás) | API + CSV | ~100K/ano | MÉDIO | Royalties + preços de combustíveis |
| 20 | ANEEL (Energia) | API | ~50K | MÉDIO | Concessões e contratos de energia |
| 21 | ANM (Mineração) | API + CSV | ~100K | ALTO | Direitos minerários, ligados a desmatamento |
| 22 | ANTT (Transportes) | API | ~10K | BAIXO | Concessões de transporte |
| 23 | ANS (Planos de Saúde) | API | ~50K | BAIXO | Operadoras de planos |
| 24 | ANVISA (Medicamentos/Alimentos) | API | ~100K | BAIXO | Registros de produtos |
| 25 | ANAC (Aviação) | API | ~10K | BAIXO | Concessões aeroportuárias |
| 26 | ANTAQ (Hidrovias) | API | ~5K | BAIXO | Contratos portuários |
| 27 | ANA (Água) | API | ~10K | BAIXO | Outorgas de recursos hídricos |
| 28 | ANATEL (Telecomunicações) | API | ~50K | BAIXO | Licenças de telecom |
| 29 | SUSEP (Seguros) | CSV | ~10K | BAIXO | Dados do mercado segurador |

### 3.5 Financeiro / Valores Mobiliários

| # | Fonte | Formato | Volume Est. | Valor | Notas |
|---|-------|---------|-------------|-------|-------|
| 30 | CVM Completo (Participações/Fundos) | CSV | Milhões | ALTO | Cadeias de participação acionária |
| 31 | Receita DIRBI | CSV | Grande | MÉDIO | Declarações de benefícios fiscais |

### 3.6 Meio Ambiente

| # | Fonte | Formato | Volume Est. | Valor | Notas |
|---|-------|---------|-------------|-------|-------|
| 32 | MapBiomas Alerta | API REST | 465K+ alertas | ALTO | Desmatamento validado, sobreposição com propriedades |
| 33 | SiCAR (Cadastro Rural) | Shapefiles | ~7M propriedades | ALTO | Limites de propriedades rurais + proprietários |
| 34 | ICMBio/CNUC | API | ~2,5K | BAIXO | Limites de áreas de conservação |

### 3.7 Trabalho

| # | Fonte | Formato | Volume Est. | Valor | Notas |
|---|-------|---------|-------------|-------|-------|
| 35 | CAGED | BigQuery | ~2M/mês | MÉDIO | Admissões/demissões mensais (sem CPF nos dados públicos) |
| 36 | RAIS Microdados | BigQuery | ~50M/ano | MÉDIO | Dados identificados requerem autorização formal |

### 3.8 Orçamento / Fiscal

| # | Fonte | Formato | Volume Est. | Valor | Notas |
|---|-------|---------|-------------|-------|-------|
| 37 | SIOP Emendas | CSV + API | ~30K/ano | ALTO | Detalhes de execução de emendas parlamentares |
| 38 | SICONFI | API REST (siconfipy) | ~5,5K municípios | MÉDIO | Dados fiscais municipais/estaduais |
| 39 | Tesouro Emendas | CSV | ~50K | ALTO | Gastos de emendas rastreados pelo Tesouro |
| 40 | SIGA Brasil | CSV export | Enorme | MÉDIO | Execução orçamentária federal completa |

### 3.9 Legislativo

| # | Fonte | Formato | Volume Est. | Valor | Notas |
|---|-------|---------|-------------|-------|-------|
| 41 | Câmara API Completa (Votações/Projetos) | API REST + BigQuery | Milhões | MÉDIO | Votações de deputados, autoria de projetos |
| 42 | Senado API Completa (Votações/CPIs) | API REST + BigQuery | Grande | MÉDIO | Votações do Senado, detalhes de CPIs |
| 43 | TSE Filiados | BigQuery | ~15M | MÉDIO | Histórico de filiação partidária |
| 44 | TSE Bens (Patrimônio de Candidatos) | BigQuery | ~500K | ALTO | Patrimônio declarado por eleição |

### 3.10 Sanções Internacionais

| # | Fonte | Formato | Volume Est. | Valor | Notas |
|---|-------|---------|-------------|-------|-------|
| 45 | OFAC SDN | CSV direto | ~12K | ALTO | Lista de sanções do Tesouro dos EUA |
| 46 | Sanções UE | CSV direto | ~5K | ALTO | Lista consolidada de sanções da UE |
| 47 | Sanções ONU | XML direto | ~2K | ALTO | Sanções do Conselho de Segurança da ONU |
| 48 | Banco Mundial | CSV (OpenSanctions) | ~1K | MÉDIO | Empresas/indivíduos impedidos |
| 49 | INTERPOL Alertas Vermelhos | API REST | ~7K | MÉDIO | Requer chave de API |

### 3.11 Estadual / Municipal

| # | Fonte | Formato | Volume Est. | Valor | Notas |
|---|-------|---------|-------------|-------|-------|
| 50 | PNCP Completo | API REST Swagger | Enorme | ALTO | Portal nacional de compras públicas |
| 51 | TCE-SP | API REST | Grande | ALTO | Tribunal de Contas de São Paulo |
| 52 | TCE-PE | API REST (busca CPF/CNPJ) | Grande | MÉDIO | Tribunal de Contas de Pernambuco |
| 53 | TCE-RJ | API REST | Grande | MÉDIO | Tribunal de Contas do Rio de Janeiro |
| 54 | TCE-RS | Downloads em massa | Grande | MÉDIO | Tribunal de Contas do Rio Grande do Sul |
| 55 | MiDES | BigQuery | Enorme | MUITO ALTO | 72% dos municípios cobertos |
| 56 | Querido Diário | API REST + ZIPs | 104K+ diários | ALTO | Texto integral de diários oficiais municipais |
| 57-66 | Portais de Transparência Estaduais | Varia | Varia | MÉDIO | SP, MG, BA, CE, GO, PR, SC, RS, PE, RJ |

---

## 4. ATALHOS (dados pré-processados)

Datasets mantidos pela comunidade que aceleram a ingestão.

| # | Repo / Fonte | O que é | Volume | Valor | Status |
|---|--------------|---------|--------|-------|--------|
| G1 | brasil-io-public (holding.csv.gz) | Cadeias de participação empresa-empresa | 787K rels, 9MB | ALTO | Pronto para carregar |
| G2 | SINARC | Grafo anti-corrupção pré-construído | 90GB | REFERÊNCIA | Formato não claro, usar para validação |
| G3 | cnpj-chat/cnpj-data-pipeline | CNPJ por estado em Parquet (GitHub Releases) | Grande | MÉDIO | Formato alternativo de CNPJ |
| G4 | rictom/rede-cnpj | SQLite com relacionamentos CNPJ pré-computados | Grande | MÉDIO | Inclui crosslinks TSE/Transparência |
| G5 | hackfestcc/dados-hackfestcc | Datasets curados anti-corrupção | Pequeno | BAIXO | Datasets de referência |
| G6 | DanielFillol/DataJUD_API_CALLER | Downloader em Go para DataJud em massa | -- | ALTO | Acelera ingestão do CNJ |
| G7 | Serenata de Amor (suspicions.xz) | Anomalias CEAP pré-analisadas | 8K registros | MÉDIO | Despesas de deputados pré-analisadas |
| G8 | mcp-senado | Servidor MCP para API do Senado (56 tools) | -- | BAIXO | Ferramenta de desenvolvimento |
| G9 | mcp-portal-transparencia | Servidor MCP para API do Portal da Transparência | -- | BAIXO | Ferramenta de desenvolvimento |

---

## 5. DATASETS BIGQUERY (via Base dos Dados)

[basedosdados.org](https://basedosdados.org) fornece dados públicos brasileiros limpos e padronizados no BigQuery. Plano gratuito tem limites; planos pagos para uso intenso.

| Dataset BQ | Tabelas Principais | Carregado? | Notas |
|------------|-------------------|------------|-------|
| br_rf_cnpj | empresas, socios, estabelecimentos | SIM (CSV direto) | Usado download direto da Receita |
| br_tse_eleicoes | candidatos, receitas, despesas, bens_candidato, filiacao_partidaria | PARCIAL | Candidatos + doações via TSE direto; bens + filiados ainda não |
| br_me_rais | microdados_vinculos | PARCIAL | Agregado carregado; microdados requerem autorização formal |
| br_me_caged | microdados_movimentacao | NÃO | Dados trabalhistas mensais |
| br_stf_corte_aberta | decisoes | NÃO | Decisões do Supremo |
| br_camara_dados_abertos | votacao, proposicao, deputado | PARCIAL | Despesas carregadas; votações/projetos ainda não |
| br_senado_cpipedia | cpi | NÃO | Dados de CPIs |
| br_bd_diretorios_brasil | municipio, uf, setor_censitario | NÃO | Tabelas de referência para joins |
| br_mides | licitacao, contrato, item | NÃO | Licitações municipais (72% cobertura) |

---

## 6. MATRIZ DE PRIORIDADE DE INGESTÃO

Ordem recomendada baseada em: valor para detecção de padrões, esforço de implementação e volume de dados.

| Prioridade | Fonte | Esforço | Volume | Valor | Justificativa |
|------------|-------|---------|--------|-------|---------------|
| 1 | Lista PEP CGU | Trivial (CSV) | ~100K | ALTO | Substitui PEP_ROLES hardcoded; classificação PEP oficial |
| 2 | CEAF (Servidores Expulsos) | Fácil (CSV) | ~10K | ALTO | Servidores expulsos por má conduta; cruzar com empresas |
| 3 | Acordos de Leniência | Trivial (CSV) | ~34 | MUITO ALTO | Empresas que admitiram ilícitos; dataset minúsculo, valor imenso |
| 4 | OFAC SDN | Fácil (CSV) | ~12K | ALTO | Sanções internacionais; download direto, bem estruturado |
| 5 | Brasil.IO Holdings | Trivial (9MB download) | 787K rels | ALTO | Cadeias empresa-empresa; enriquecimento imediato do grafo |
| 6 | DOU via IN XML | Médio (parsing XML) | Grande | ALTO | Bypass do Cloudflare; nomeações e atos oficiais |
| 7 | TSE Bens (Patrimônio) | Fácil (BigQuery) | ~500K | ALTO | Patrimônio declarado; detectar crescimento patrimonial inexplicável |
| 8 | TSE Filiados | Fácil (BigQuery) | ~15M | MÉDIO | Histórico de filiação; útil para mapeamento de redes políticas |
| 9 | CVM Completo (Participações) | Médio (CSV) | Milhões | ALTO | Cadeias de participação revelam beneficiários ocultos |
| 10 | CNJ DataJud | Médio (API + chave) | Enorme | MUITO ALTO | Processos judiciais; maior lacuna no grafo atual |

### Escala de Esforço
- **Trivial**: Download direto de CSV, schema compatível com padrões existentes, <1 dia
- **Fácil**: CSV/BigQuery, transformações menores necessárias, 1-2 dias
- **Médio**: Paginação de API, conversão de formato ou autenticação necessária, 3-5 dias
- **Difícil**: Scraping, bypass de Cloudflare, parsing complexo ou pedido formal de dados, 1-2 semanas
