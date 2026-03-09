# REPORT_STANDARD.md — Padrão de Relatórios de Investigação

> **VERSION:** 1.0.0 | **UPDATED:** 2026-03-04
> **SSOT:** Este é o padrão canônico. Qualquer LLM que gerar relatórios DEVE seguir este schema.

---

## Princípios Fundamentais

1. **NUNCA ACUSAR** — Relatórios apresentam fatos públicos, nunca conclusões acusatórias
2. **CITAR FONTE** — Todo dado deve ter fonte, URL e data de consulta
3. **CONFIANÇA** — Cada dado tem nível de confiança: Alta (API oficial), Média (cruzamento), Baixa (inferência)
4. **GAPS EXPLÍCITOS** — O que NÃO foi encontrado é tão importante quanto o que foi
5. **REPRODUTÍVEL** — Qualquer pessoa deve conseguir verificar cada dado seguindo as fontes

---

## Schema JSON (para geração programática)

```json
{
  "report_id": "REPORT-YYYY-NNN",
  "version": "1.0",
  "generated_at": "ISO-8601",
  "generated_by": {
    "model": "nome/modelo-usado",
    "cost": "R$ X.XX",
    "platform": "EGOS Inteligência"
  },

  "metadata": {
    "title": "Título do relatório",
    "subtitle": "Descrição em uma frase",
    "entity_type": "company | person | group | sector",
    "date": "DD/MM/YYYY",
    "sources_count": 0,
    "observations_count": 0,
    "confidence_overall": "alta | media | baixa"
  },

  "legal_disclaimer": "Este relatório apresenta exclusivamente dados de acesso público, obtidos via APIs oficiais do governo brasileiro e datasets abertos. Não constitui acusação, denúncia ou parecer jurídico. As observações aqui contidas são compilações factuais de registros públicos, cabendo aos órgãos competentes qualquer apuração.",

  "sections": [
    {
      "id": "summary",
      "title": "Resumo",
      "required": true,
      "content": "Parágrafo executivo (max 200 palavras)",
      "key_numbers": [
        {"label": "Label", "value": "R$ X", "context": "explicação curta"}
      ]
    },
    {
      "id": "entity_data",
      "title": "Dados da Entidade",
      "required": true,
      "fields": [
        {"field": "Razão Social / Nome", "value": "", "source": "Receita Federal / BrasilAPI"},
        {"field": "CNPJ / CPF", "value": "", "source": "Receita Federal"},
        {"field": "Situação Cadastral", "value": "", "source": "Receita Federal"},
        {"field": "CNAE / Atividade", "value": "", "source": "Receita Federal"},
        {"field": "Endereço", "value": "", "source": "Receita Federal"},
        {"field": "Data de Abertura / Nascimento", "value": "", "source": "Receita Federal"}
      ]
    },
    {
      "id": "ownership",
      "title": "Quadro Societário / Vínculos",
      "required": true,
      "note": "Se não disponível, explicar o gap",
      "entries": [
        {
          "name": "",
          "role": "Sócio | Administrador | Diretor",
          "type": "PF | PJ",
          "document": "CPF mascarado ou CNPJ",
          "alert": "Se sócio PJ → investigar cadeia societária"
        }
      ]
    },
    {
      "id": "graph_analysis",
      "title": "Análise no Grafo (Neo4j)",
      "required": true,
      "metrics": {
        "found_in_graph": true,
        "node_type": "Company | Person | Sanction",
        "total_connections": 0,
        "connection_types": [
          {"type": "SOCIO_DE", "count": 0},
          {"type": "SANCIONADA", "count": 0},
          {"type": "DOOU", "count": 0},
          {"type": "VENCEU", "count": 0}
        ],
        "multi_hop_paths": "Resultados do find_connection_path se aplicável"
      }
    },
    {
      "id": "source_checks",
      "title": "Verificação em Bases Públicas",
      "required": true,
      "checks": [
        {
          "source": "CEIS (Empresas Inidôneas)",
          "result": "Encontrado | Nenhum registro",
          "confidence": "alta | media | baixa",
          "details": "",
          "api_url": "https://api.portaldatransparencia.gov.br/..."
        },
        {
          "source": "CNEP (Empresas Punidas)",
          "result": "",
          "confidence": "",
          "details": ""
        },
        {
          "source": "PEP (Pessoa Politicamente Exposta)",
          "result": "",
          "confidence": "",
          "details": ""
        },
        {
          "source": "OpenSanctions (Global)",
          "result": "",
          "confidence": "",
          "details": ""
        },
        {
          "source": "BNDES (Financiamentos)",
          "result": "",
          "confidence": "",
          "details": "",
          "total_value": "R$ 0"
        },
        {
          "source": "Receita Federal (QSA)",
          "result": "",
          "confidence": "",
          "details": ""
        },
        {
          "source": "DataJud (Processos)",
          "result": "",
          "confidence": "",
          "details": ""
        },
        {
          "source": "PNCP (Contratos/Licitações)",
          "result": "",
          "confidence": "",
          "details": ""
        }
      ]
    },
    {
      "id": "observations",
      "title": "Observações Factuais",
      "required": true,
      "note": "NUNCA acusações. Apenas compilações de fatos com dados.",
      "items": [
        {
          "number": 1,
          "title": "Título descritivo do fato",
          "description": "Descrição factual com números e datas",
          "data_points": ["dado1", "dado2"],
          "sources": ["fonte1", "fonte2"]
        }
      ]
    },
    {
      "id": "gaps",
      "title": "Dados Não Disponíveis / Gaps",
      "required": true,
      "items": [
        {
          "data": "O que falta",
          "reason": "Por que não temos",
          "when": "Quando teremos (ETA)",
          "impact": "Como afeta a análise"
        }
      ]
    },
    {
      "id": "sources_list",
      "title": "Fontes Utilizadas",
      "required": true,
      "sources": [
        {
          "number": 1,
          "name": "Nome da fonte",
          "url": "URL oficial",
          "consulted_at": "DD/MM/YYYY",
          "records_count": "N registros consultados"
        }
      ]
    },
    {
      "id": "methodology",
      "title": "Metodologia",
      "required": false,
      "content": "Explicação de como os dados foram cruzados"
    },
    {
      "id": "reproduction_steps",
      "title": "Como Verificar (Cidadão / Desenvolvedor)",
      "required": false,
      "citizen_steps": ["passo 1", "passo 2"],
      "developer_steps": ["query Neo4j", "chamada API"]
    }
  ],

  "footer": {
    "platform": "EGOS Inteligência",
    "url": "https://inteligencia.egos.ia.br",
    "license": "AGPL-3.0",
    "github": "https://github.com/enioxt/EGOS-Inteligencia",
    "quote": "Dados públicos, código aberto, transparência real."
  }
}
```

---

## Regras de Linguagem

### OBRIGATÓRIO
- "Registros públicos indicam que..."
- "Segundo dados do Portal da Transparência..."
- "Conforme consulta à API do BNDES em DD/MM/YYYY..."
- "Observa-se que..." (factual, sem julgamento)
- "Cabe aos órgãos competentes apurar..."

### PROIBIDO
- ~~"A empresa é corrupta"~~ → "A empresa possui N registros de sanção"
- ~~"Lavagem de dinheiro"~~ → "Movimentação financeira que merece análise por órgão competente"
- ~~"Fraude"~~ → "Padrão identificado que difere da média do setor"
- ~~"Certamente"~~ → "Os dados disponíveis sugerem..."
- ~~CPF completo~~ → "***.***.***-XX" (sempre mascarar)

### Níveis de Confiança

| Nível | Quando usar | Exemplo |
|-------|-------------|---------|
| **Alta** | Dado vem de API oficial, verificável | CNPJ da Receita, sanção do CEIS |
| **Média** | Cruzamento entre fontes, fuzzy match | Nome similar em duas bases |
| **Baixa** | Inferência, dado incompleto | "Possível vínculo" baseado em endereço |

---

## Seções Obrigatórias vs Opcionais

| Seção | Obrigatória | Notas |
|-------|-------------|-------|
| Legal Disclaimer | ✅ | SEMPRE primeiro, antes de qualquer dado |
| Resumo | ✅ | Max 200 palavras |
| Dados da Entidade | ✅ | CNPJ/CPF, situação, endereço |
| Quadro Societário | ✅ | Se vazio, explicar gap |
| Análise no Grafo | ✅ | Conexões, tipos de relacionamento |
| Verificação em Bases | ✅ | Todas as bases consultadas |
| Observações Factuais | ✅ | Min 1, max 10 |
| Gaps | ✅ | O que NÃO foi encontrado |
| Fontes | ✅ | Com URL e data |
| Metodologia | ❌ | Para relatórios complexos |
| Passos de Verificação | ❌ | Para relatórios públicos |
| Comparação Premium | ❌ | Para marketing/showcase |
| Roadmap | ❌ | Para relatórios de showcase |

---

## Formato de Saída

### HTML (padrão para site)
- Dark mode: `--bg: #0a0e17`, `--text: #e2e8f0`, `--accent: #3b82f6`
- Self-contained: CSS inline, sem dependências externas
- Responsivo: media queries para mobile
- Caminho: `frontend/public/reports/{slug}.html`

### Markdown (para exportação)
- Gerado pelo `export_service.py`
- Segue mesmo schema, sem CSS

### JSON (para API)
- Segue o schema JSON acima
- Endpoint: `POST /api/v1/investigations/{id}/report`

---

## Checklist para Novo Relatório

- [ ] Legal disclaimer no topo
- [ ] Todos os dados com fonte e data de consulta
- [ ] Nível de confiança em cada verificação
- [ ] CPFs mascarados (***.***.***-XX)
- [ ] Linguagem não acusatória em todas as observações
- [ ] Gaps explícitos (o que não encontrou e por quê)
- [ ] Fontes com URLs verificáveis
- [ ] Números verificados contra API live
- [ ] Relatório salvo em `frontend/public/reports/`
- [ ] Metadata consistente (data, modelo, custo)

---

## Exemplos de Relatórios Existentes

| Relatório | Tipo | Seções | Fontes |
|-----------|------|--------|--------|
| `patense.html` | Grupo empresarial (showcase) | 11 seções, 4 obs | 6 bases |
| `report-01-superar-ltda.html` | Empresa sancionada | 7 seções, 1 obs | 5 bases |
| `report-02-manaus-transparencia.html` | Município | - | - |
| `report-03-recuperacao-judicial-sp.html` | Judicial | - | - |

---

*"Transparência é um direito. O padrão garante que qualquer modelo respeite os fatos."*
