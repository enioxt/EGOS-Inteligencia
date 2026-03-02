# Mapa de Portais de Transparência — Brasil

> **Data:** 02/03/2026 | **Status:** Pesquisa Inicial
> **Objetivo:** Identificar gaps, propor melhorias, recomendar APIs abertas

---

## 1. Padrão de Referência: Federal

### Portal da Transparência (CGU) — ⭐⭐⭐⭐⭐ MELHOR DO BRASIL
- **URL:** portaldatransparencia.gov.br
- **API:** api.portaldatransparencia.gov.br (REST, JSON, chave gratuita)
- **Endpoints:** Servidores, Licitações, Contratos, Viagens, CPGF, Emendas, Sanções (CEIS/CNEP/CEAF/CEPIM), Bolsa Família, etc.
- **O que faz certo:**
  - API documentada com Swagger
  - Chave gratuita (registro simples)
  - Dados estruturados em JSON
  - Paginação, filtros por período/órgão/UF
  - Atualização diária
- **Limitações:**
  - Alguns endpoints exigem filtros mínimos (CPF ou código órgão para servidores)
  - Sem dados municipais (apenas federais)
  - Sem busca full-text (precisa saber código do órgão SIAPE)

---

## 2. Avaliações Existentes

### PNTP — Programa Nacional de Transparência Pública (ATRICON/TCU)
- **10.335 portais avaliados** em 2025
- **122 municípios SEM portal** de transparência
- **109 portais com 100%** de transparência
- **998 selos diamante**
- **Média prefeituras:** 67,48%
- **Média câmaras:** 65,17%
- **Resultado:** https://radardatransparencia.com/

### Transparência Internacional — ITGP (Índice de Transparência e Governança Pública)
- **300+ municípios** avaliados em 12 estados
- **100+ critérios** incluindo dados abertos, participação social, combate à corrupção
- Avaliação estadual em 2025 revelou avanços e falhas
- **Resultado:** transparenciainternacional.org.br/itgp/municipal/

### Radar Transparente
- Rankings por exercício, filtros por município
- Análise baseada em critérios técnicos reconhecidos
- **URL:** radartransparente.com.br

---

## 3. Portais Estaduais — Análise Rápida

### MODELO: São Paulo
- **Portal:** transparencia.sp.gov.br
- **API:** Dados abertos parciais via CKAN
- **Score PNTP:** Alto
- **Limitação:** API não tão rica quanto a federal

### MODELO: Minas Gerais
- **Portal:** transparencia.mg.gov.br
- **Destaque:** Boa visualização de empenhos, liquidações, pagamentos
- **API:** Portal de Dados Abertos MG (dados.mg.gov.br)

### PROBLEMAS COMUNS (estados com notas baixas):
- Portal existe mas sem API
- Dados em PDF (não estruturados)
- Desatualizado (>30 dias de atraso)
- Sem busca por nome/CPF/CNPJ
- Sem dados de licitações/contratos acessíveis
- Interface confusa, difícil de navegar

---

## 4. Portais Municipais — Principais Gaps

### Problemas Identificados (dados PNTP 2025):

| Problema | Impacto | Proporção |
|----------|---------|-----------|
| **Sem portal** | Total falta de transparência | 122 municípios |
| **Portal sem dados de licitações** | Impossível monitorar compras | ~40% dos municípios |
| **Sem API** | Dados inacessíveis por máquinas | ~95% dos municípios |
| **Dados em PDF** | Impossível processar automaticamente | ~70% dos municípios |
| **Desatualizado (>30 dias)** | Dados stale | ~30% dos municípios |
| **Sem busca por fornecedor** | Não dá para investigar empresas | ~60% dos municípios |
| **Sem dados de servidores/salários** | Supersalários escondidos | ~50% dos municípios |

---

## 5. Proposta de Melhorias

### Para Municípios

1. **API REST mínima obrigatória** — endpoints para: receitas, despesas, licitações, contratos, servidores, folha de pagamento
2. **Formato JSON** (não PDF) — dados estruturados, pesquisáveis
3. **Atualização diária** — no máximo 7 dias de atraso
4. **Busca por fornecedor/CNPJ** — permite cross-reference com CEIS/CNEP
5. **Padrão SICONV/TransfereGov** — mesma estrutura do portal federal

### Para Estados

1. **Portal de Dados Abertos** estilo CKAN com APIs
2. **Integração com Querido Diário** — diários oficiais digitalizados e pesquisáveis
3. **API de servidores/salários** com busca por nome/CPF
4. **Dashboard de contratos** com histórico de aditivos

### Para o EGOS Inteligência

1. **Crawler de portais municipais** — bot que verifica periodicamente quais portais existem, têm API, dados atualizados
2. **Score de transparência próprio** — baseado em: existência de API, formato de dados, atualização, cobertura
3. **Relatórios comparativos** — ranking visual por estado/município
4. **Alertas** — notificar quando um portal fica offline ou desatualizado

---

## 6. Dados já Disponíveis via API

### APIs Funcionais (já integradas ou prontas para integrar):

| Fonte | Cobertura | API | Status EGOS |
|-------|-----------|-----|-------------|
| Portal da Transparência | Federal | REST + chave | ✅ Integrado |
| TransfereGov | Federal (emendas/transferências) | REST livre | ✅ Integrado |
| Câmara dos Deputados | Federal (CEAP, votações) | REST livre | ✅ Integrado |
| Querido Diário | 510+ municípios (diários oficiais) | REST livre | ✅ Integrado |
| DataJud (CNJ) | Todos os tribunais | REST + chave | ✅ Integrado |
| IBGE | Nacional (códigos, população) | REST livre | Parcial |
| TSE | Eleições (candidatos, doações) | Bulk download | Parcial (ETL) |
| Receita Federal | Nacional (empresas/CNPJ) | Bulk download | ETL 12.5% |
| OpenSanctions | Global (PEPs, sanções) | Bulk download | ✅ Carregado |

### APIs a Integrar (futuro):

| Fonte | Cobertura | Tipo | Prioridade |
|-------|-----------|------|-----------|
| Dados Abertos SP | Estado SP | CKAN | P1 |
| Dados Abertos MG | Estado MG | CKAN | P1 |
| ComprasNet/ComprasGov | Federal (licitações) | REST | P1 |
| SIAFI/Tesouro | Federal (gastos detalhados) | REST | P2 |
| Senado Federal | Federal (votações, CEAP senadores) | REST | P2 |
| TCU Contas Públicas | Federal (auditorias) | Bulk | P2 |
| Dados Abertos RJ | Estado RJ | CKAN | P2 |

---

## 7. Referências

- [PNTP 2025](https://radardatransparencia.com/) — 10.335 portais avaliados
- [Transparência Internacional ITGP](https://transparenciainternacional.org.br/itgp/) — 100+ critérios
- [Radar Transparente](https://radartransparente.com.br/) — Rankings municipais
- [NúcleoGov Diagnóstico](https://diagnostico.transparencia.com.br/) — Diagnóstico 2025
- [Querido Diário](https://queridodiario.ok.org.br/) — Diários oficiais de 510+ cidades

---

*"Transparência não é opcional. É obrigação legal (LAI 12.527/2011)."*
