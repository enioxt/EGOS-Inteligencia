# Relatório de Investigação #01: SUPERAR LTDA

> **Gerado por:** EGOS Inteligência (inteligencia.egos.ia.br)
> **Data:** 02/03/2026 | **Modelo LLM:** Google Gemini 2.0 Flash (via OpenRouter)
> **Stack:** Neo4j + FastAPI + React + Brave Search + Portal da Transparência + DataJud
> **Custo estimado desta análise:** ~R$ 0,05 (tokens LLM) + R$ 0,00 (APIs gratuitas)

---

## Dados da Empresa

| Campo | Valor |
|-------|-------|
| **Razão Social** | SUPERAR LTDA |
| **CNPJ** | 13.482.516/0001-61 |
| **Situação Cadastral** | ATIVA |
| **CNAE Principal** | Comércio varejista especializado de eletrodomésticos e equipamentos de áudio e vídeo |
| **Capital Social** | R$ 500.000,00 |
| **Endereço** | Governador Mário Covas S/N, Cariacica - ES |
| **Data de Abertura** | 07/04/2011 |
| **Fonte** | BrasilAPI / Receita Federal |

### Quadro Societário (QSA)

| Sócio | Qualificação |
|-------|-------------|
| ALDIVAR BAGATOLI | Administrador |
| MASTER ELETRODOMESTICO LTDA | Sócio (Pessoa Jurídica) |

> **⚠️ Alerta:** Sócio PJ (MASTER ELETRODOMESTICO LTDA) — investigar cadeia societária para identificar beneficiários finais.

---

## Análise no Grafo (Neo4j)

| Métrica | Valor |
|---------|-------|
| **Nó encontrado** | ✅ Sim |
| **Tipo** | Company |
| **Conexões totais** | 7 |
| **Tipo de conexões** | SANCIONADA (7x) |

> A empresa possui **7 registros de sanção** no grafo, conectada a 7 nós do tipo Sanction.
> Isso indica múltiplas punições por diferentes órgãos ou em diferentes períodos.

---

## Passo a Passo: Como Geramos Este Relatório

### Para Leigos — Qualquer Cidadão Pode Fazer Isso

1. **Acesse** inteligencia.egos.ia.br
2. **Pesquise** o CNPJ `13.482.516/0001-61` na barra de busca
3. **Visualize** as conexões no grafo interativo
4. **Use o chatbot** (ícone de chat) e pergunte:
   - "Quais sanções a empresa SUPERAR LTDA tem?"
   - "Quem são os sócios da SUPERAR?"
   - "A SUPERAR tem contratos com o governo?"
5. **O sistema cruza automaticamente** dados de:
   - Receita Federal (CNPJ, sócios)
   - Portal da Transparência (sanções CEIS/CNEP)
   - DataJud (processos judiciais)
   - Querido Diário (diários oficiais)
   - DuckDuckGo/Brave (notícias)

### Para Desenvolvedores — Como Funciona por Baixo

```
1. Busca → Neo4j MATCH (c:Company {cnpj: "13482516000161"})
2. Conexões → MATCH (c)-[r]-(n) RETURN type(r), n
3. CEIS → GET api.portaldatransparencia.gov.br/api-de-dados/ceis?cnpjSancionado=...
4. DataJud → POST api-publica.datajud.cnj.jus.br/{tribunal}/_search
5. CNPJ → GET brasilapi.com.br/api/cnpj/v1/13482516000161
6. LLM → Gemini 2.0 Flash analisa e cruza todas as fontes
```

---

## O Que Falta Para Completar (Gaps Identificados)

| Dado Faltante | Por quê | Quando teremos |
|---------------|---------|----------------|
| **Sócios completos (QSA de todas filiais)** | ETL Receita Federal em 15% | ~3-5 dias |
| **Contratos com o governo** | Portal API requer código órgão específico | Disponível por consulta |
| **Processos judiciais** | DataJud não encontrou por nome genérico | Buscar por CNPJ quando disponível |
| **Beneficiário final** | MASTER ELETRODOMESTICO LTDA precisa ser investigada | Consulta manual ou ETL |
| **Notícias e denúncias** | Brave Search não retornou resultados específicos | Melhorar query |

---

## Comparação: O Que Palantir/NSA/i2 Teriam a Mais

| Capacidade | EGOS Intel | Palantir Gotham | i2 Analyst Notebook |
|-----------|-----------|----------------|---------------------|
| Grafo de entidades | ✅ 317K nós | ✅ Bilhões de nós | ✅ Milhões |
| Cross-reference automático | ✅ 18 ferramentas | ✅ Centenas de conectores | ✅ Dezenas |
| AI/NLP | ✅ Gemini 2.0 Flash | ✅ AIP (GPT-4 nível) | ❌ Limitado |
| Dados financeiros (SWIFT, bancos) | ❌ | ✅ | ✅ |
| Dados de telecomunicações | ❌ | ✅ | ✅ |
| Geolocalização em tempo real | ❌ | ✅ | ✅ |
| OCR de documentos | ❌ | ✅ | ✅ |
| Link analysis visual | ✅ (Force-directed) | ✅ (Avançado) | ✅ (Referência) |
| Custo | **GRÁTIS** (open-source) | ~US$10M/ano | ~US$50K/licença |
| Acesso | **Público** (qualquer cidadão) | Restrito (governo/militar) | Restrito (polícia) |

---

*"Transparência não é privilégio de quem pode pagar. É direito de todo cidadão."*
*EGOS Inteligência — inteligencia.egos.ia.br — Código aberto, dados abertos.*
