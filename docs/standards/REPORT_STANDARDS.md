# Padrão de Relatórios — EGOS Inteligência

> **Versão:** 1.0.0 | **Data:** 2026-03-06
> **Princípio:** Conectar pontos, nunca acusar. Dados públicos, fontes rastreáveis.

---

## 1. Regras Fundamentais

1. **Nenhuma acusação.** Nunca afirmamos culpa, dolo ou intenção.
2. **Nenhuma especulação.** Não inferimos motivações ou consequências não documentadas.
3. **Dados públicos apenas.** Toda informação deve ter fonte oficial rastreável.
4. **Fonte por afirmação.** Cada fato deve citar a fonte específica (URL, DOU, processo).
5. **Mídia ≠ Fato.** Cobertura jornalística é sinal/contexto, nunca prova.
6. **Temporal.** Todo relatório informa data de coleta. Dados podem mudar.
7. **Código aberto.** O código que gerou o relatório é auditável por qualquer pessoa.

---

## 2. Estrutura Obrigatória de Relatórios

Todo relatório deve conter, nesta ordem:

### 2.1 Cabeçalho
```markdown
# [Título descritivo — sem linguagem acusatória]
> **TASK-XXX** | Criado: YYYY-MM-DD | Atualizado: YYYY-MM-DD vN
> **Regra:** Fatos = documento oficial ou registro público. Mídia = contexto.
> Nenhuma acusação. Nenhuma afirmação de culpa.
```

### 2.2 Disclaimer Legal (obrigatório no topo)
```markdown
> **AVISO LEGAL:** Este documento compila exclusivamente dados de fontes
> públicas oficiais. Não constitui denúncia, acusação ou prova de
> irregularidade. Relações societárias e processos administrativos são
> fatos registrais, não implicam conduta ilícita. Erros são possíveis —
> contribuições e correções são bem-vindas via GitHub Issues.
```

### 2.3 Seções do Corpo
1. **Fatos Confirmados** — apenas com fonte oficial (URL, DOU, nº processo)
2. **Entidades Mapeadas** — CNPJs, nomes, vínculos confirmados no QSA/grafo
3. **Sinais e Contexto** — imprensa, sempre com caveat explícito
4. **Lacunas Investigativas** — o que NÃO sabemos (transparência radical)
5. **Próximas Verificações** — checklist claro do que falta cruzar
6. **Pontos Fracos** — autocrítica honesta da análise

### 2.4 Rodapé Obrigatório
```markdown
---
*Documento gerado por EGOS Inteligência. Código aberto: github.com/enioxt/EGOS-Inteligencia*
*Dados públicos, sem acusações, sem afirmações de culpa.*
*Encontrou um erro? Abra uma issue: github.com/enioxt/EGOS-Inteligencia/issues*
```

---

## 3. Rastreabilidade de Dados (Provenance)

Cada dado no relatório deve indicar:

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| **Fonte** | URL ou referência oficial | `gov.br/cvm/...` |
| **Método** | Como foi obtido | `bulk_download`, `api`, `manual` |
| **Data de coleta** | Quando foi verificado | `2026-03-06` |
| **Hash** | SHA-256 da linha bruta (quando disponível) | `a1b2c3...` |
| **Status** | `verified` / `legacy` / `unverified` | `verified` |

> O módulo `bracc_etl/provenance.py` implementa hashing determinístico
> para garantir não-repúdio dos dados brutos processados pelo ETL.

---

## 4. Rotas de Pesquisa e Colaboração

Todo relatório deve explicitar:

1. **Rotas abertas** — caminhos de pesquisa que podem ser seguidos
2. **Rotas bloqueadas** — dados que requerem acesso restrito (judicial, COAF, etc.)
3. **Convite à verificação** — pedir que leitores confirmem, corrijam ou adicionem

```markdown
> **Para pesquisadores e autoridades:** Este relatório é um ponto de partida.
> As rotas de pesquisa indicadas podem ser expandidas com acesso a bases
> restritas (COAF, SIMBA, CCS, INFOSEG). Disponibilizamos o código e a
> infraestrutura gratuitamente para qualquer órgão público que deseje
> utilizá-los. Contato: [GitHub Issues ou email].
```

---

## 5. O Que NÃO Fazer

- ❌ Usar palavras como "criminoso", "fraudador", "culpado", "lavagem"
- ❌ Afirmar que relação societária implica irregularidade
- ❌ Omitir fontes ou usar "segundo fontes" sem identificar
- ❌ Apresentar hipóteses como fatos
- ❌ Ignorar dados que contradizem a narrativa
- ❌ Usar linguagem sensacionalista ou clickbait
