# Caso Vorcaro / Banco Master — Mapa Público de Entidades e Sinais

> **TASK-074** | Criado: 2026-03-06 | **Atualizado: 2026-03-06 v2 (Neo4j cross-reference)**
> **Regra:** Fatos = documento oficial ou registro público. Mídia = sinal/contexto, nunca conclusão.
> Nenhuma acusação. Nenhuma afirmação de culpa.

---

## 1. Fatos Confirmados (Fontes Oficiais)

### 1.1 BCB — Liquidação Extrajudicial

8 instituições liquidadas entre nov/2025 e fev/2026:

| # | Instituição | Data |
|---|-------------|------|
| 1 | Banco Master S/A | Nov/2025 |
| 2 | Banco Master de Investimento | Nov/2025 |
| 3 | Banco Letsbank (BlueBank) | Nov/2025 |
| 4 | Corretora do conglomerado | Nov/2025 |
| 5 | Will Financeira (Will Bank) | Jan/2026 |
| 6 | CBSF DTVM (ex-Reag Investimentos) | Jan/2026 |
| 7 | Banco Pleno (ex-Voiter) | Fev/2026 |
| 8 | Pleno DTVM | Fev/2026 |

**Fonte:** DOU, comunicados BCB (nov/2025, jan/2026, fev/2026).

### 1.2 CVM — PAS 19957.007976/2020-94

Em 02/12/2025, o Colegiado rejeitou unanimemente Termos de Compromisso:

| Acusado | Valor proposto |
|---------|----------------|
| Banco Master S.A. | R$ 5.940.000 |
| Viking Participações Ltda. | R$ 4.950.000 |
| Daniel Bueno Vorcaro | R$ 2.970.000 |
| Entre Investimentos e Participações Ltda. | R$ 4.950.000 |
| Antônio Carlos Freixo Júnior | R$ 2.475.000 |

**Total rejeitado:** ~R$ 21,3 milhões. O processo (aberto em 2020, 19 acusados) apura irregularidades na emissão e distribuição de cotas do FII Brazil Realty (BLZ11).

**Fonte:** https://www.gov.br/cvm/pt-br/assuntos/noticias/2025/cvm-rejeita-proposta-de-termo-de-compromisso-com-entre-investimentos-e-participacoes-ltda-banco-master-s-a-viking-participacoes-ltda-e-diretores

**Nota:** Rejeição de Termo de Compromisso ≠ condenação. Significa que o PAS prossegue.

### 1.3 Operação Compliance Zero

Deflagrada em nov/2025 em paralelo à liquidação. Investiga suspeitas relacionadas ao sistema financeiro.

**Fonte:** Comunicados oficiais; detalhes operacionais não confirmados em fonte primária nesta pesquisa.

---

## 2. Entidades Mapeadas (Registros Públicos + Grafo Neo4j)

### 2.1 CNPJs Confirmados no Grafo EGOS Inteligência

| CNPJ | Razão Social | Fonte |
|------|-------------|-------|
| 33.923.798/0003-64 | BANCO MASTER S/A - EM LIQUIDACAO EXTRAJUDICIAL | QSA/Neo4j |
| 09.526.594/0003-05 | BANCO MASTER DE INVESTIMENTO S.A. - EM LIQUIDACAO EXTRAJUDICIAL | QSA/Neo4j |
| 33.884.941/0007-80 | BANCO MASTER MULTIPLO S.A. | QSA/Neo4j |
| 33.886.862/0006-27 | MASTER S/A CORRETORA - EM LIQUIDACAO EXTRAJUDICIAL | QSA/Neo4j |
| 07.875.796/0001-75 | VIKING PARTICIPACOES LTDA | QSA/Neo4j |
| 30.037.396/0001-02 | ENTRE INVESTIMENTOS E PARTICIPACOES LTDA. | QSA/Neo4j |
| 52.695.155/0001-93 | ENTRE INVESTIMENTOS E PARTICIPACOES II LTDA | QSA/Neo4j |
| 61.024.352/0017-39 | BANCO PLENO SA | QSA/Neo4j |

### 2.2 Rede Societária — Daniel Bueno Vorcaro (15 empresas no QSA)

| CNPJ | Razão Social |
|------|-------------|
| 33.923.798/0003-64 | BANCO MASTER S/A |
| 09.526.594/0003-05 | BANCO MASTER DE INVESTIMENTO S.A. |
| 54.331.263/0001-02 | MASTER HOLDING FINANCEIRA S.A. |
| 55.757.077/0001-00 | MASTER PARTICIPACOES S.A. |
| 54.043.545/0001-04 | MASTER HOLDING FINANCEIRA SERVICOS S.A. |
| 55.997.450/0001-92 | MASTER SERVICOS S.A. |
| 57.445.179/0001-08 | DV HOLDING FINANCEIRA SA |
| 07.875.796/0001-75 | VIKING PARTICIPACOES LTDA |
| 30.157.849/0001-34 | VINC CONSULTORIA E INVESTIMENTOS LTDA. |
| 28.770.133/0001-66 | HEDGEHOG TRADING TECHNOLOGY INFORMATICA LTDA |
| 22.921.619/0001-71 | ORION BH DESENVOLVIMENTO IMOBILIARIO SPE LTDA |
| 13.332.529/0001-54 | VIA EXPRESSA S/A |
| 11.519.788/0001-63 | PIRES FOMENTO MERCANTIL LTDA |
| 46.459.239/0001-25 | STAR MUSIC LTDA |
| 10.791.605/0001-00 | GESTACAR GESTAO DE NEGOCIOS LTDA |

### 2.3 Sócios do Conglomerado Master (QSA público)

| Nome | Empresas (no QSA) |
|------|-------------------|
| DANIEL BUENO VORCARO | Master S/A, Master Investimento, Viking |
| LUIZ ANTONIO BULL | Master S/A, Master Investimento, Master Multiplo, Corretora |
| AUGUSTO FERREIRA LIMA | Master S/A, Banco Pleno, Voiter e 13+ empresas |
| ANDRE KRUSCHEWSKY LIMA | Master S/A, Master Multiplo |
| ANGELO ANTONIO RIBEIRO DA SILVA | Master S/A, Master Investimento, Master Multiplo |
| FELIPE WALLACE SIMONSEN | Master S/A |
| VITOR MANUEL FARINHA NUNES | Master Multiplo |
| ADRIANO GARZON CORREA | Viking Participações |

### 2.4 Fundo de Investimento

| Nome | Código | Relevância |
|------|--------|-----------|
| Brazil Realty FII | BLZ11 | Objeto do PAS CVM |

### 2.5 CEIS/CNEP — Sanções Verificadas

**23.848 sanções** carregadas no grafo. **Nenhuma sanção CEIS/CNEP encontrada** para nenhum dos CNPJs do conglomerado Master, Viking, ou Entre Investimentos.

> Nota: ausência de sanção ≠ inocência. Significa apenas que não há registro no CEIS/CNEP para estes CNPJs na data da consulta.

---

## 3. Sinais e Contexto (Cobertura Jornalística)

> **ATENÇÃO:** Informações de imprensa. Incluídas como contexto, não como fatos confirmados.

- BCB teria apontado "insolvência financeira" e "suspeitas de fraudes contábeis" como motivação.
- Estadão (jan/2026): rede de empresas relacionadas aos executivos soma 2.500+ CNPJs (dados Receita Federal).
- FGC ativado para ressarcir investidores de CDBs — reportado como o maior acionamento da história do fundo.
- Grupo Fictor ofereceu aporte de R$ 3 bilhões antes da liquidação; oferta não prosseguiu.

---

## 4. Lacunas Investigativas (Atualizado v2)

1. ~~**CNPJs completos**~~ ✅ Resolvido — 8 CNPJs confirmados no grafo Neo4j.
2. ~~**Grafo Neo4j**~~ ✅ Resolvido — query por STARTS WITH em razao_social funciona; 15 empresas de Vorcaro mapeadas.
3. **DataJud** — pipeline existe (`etl/pipelines/datajud.py`) mas **0 cases carregados**. Necessário ingestão de dados.
4. **Diários Oficiais** — não foram cruzados com as entidades mapeadas.
5. **19 acusados CVM** — apenas 5 nomes públicos no comunicado da CVM; os demais 14 requerem acesso ao processo.
6. **FGC** — valores exatos de ressarcimento não confirmados em fonte primária.
7. ~~**CEIS/CNEP**~~ ✅ Verificado — 23.848 sanções no grafo, **0 matches** para entidades Master/Viking/Entre.

---

## 5. Próximas Verificações

- [x] Consultar CNPJs no QSA público — ✅ 8 CNPJs confirmados no Neo4j
- [x] Buscar entidades no grafo Neo4j por CNPJ — ✅ 15 empresas de Vorcaro + 8 sócios
- [x] Verificar sanções CEIS/CNEP — ✅ Nenhuma encontrada (23.848 sanções no grafo)
- [ ] Ingerir dados DataJud para cruzar processos judiciais com entidades mapeadas
- [ ] Cruzar com Diários Oficiais (Querido Diário) para publicações relacionadas
- [ ] Expandir rede: buscar 2º grau de separação (sócios dos sócios)
- [ ] Monitorar andamento do PAS CVM — decisão final pendente
- [ ] Quando ETL completar (~30% restante): verificar se aparecem mais CNPJs

---

## 6. Pontos Fracos Desta Análise (v2)

1. **Dependência de imprensa:** Seção 3 depende de cobertura jornalística.
2. ~~Sem CNPJ verificado~~ ✅ Resolvido.
3. **ETL incompleto (~70%):** Pode haver mais empresas/sócios não carregados ainda.
4. **Sem DataJud:** Ausência de cruzamento com o Judiciário é a maior lacuna.
5. **Temporal:** Dados coletados em 06/03/2026. Caso em rápida evolução.
6. **14 acusados CVM desconhecidos:** Sem acesso ao corpo do PAS.

---

*Documento gerado automaticamente por EGOS Inteligência. Dados públicos, sem acusações, sem afirmações de culpa.*
