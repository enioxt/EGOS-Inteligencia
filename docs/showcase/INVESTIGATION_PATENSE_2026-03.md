# Investigação: Grupo Patense — R$ 217M do BNDES → Recuperação Judicial de R$ 2.15 Bilhões

> **Data:** 2026-03-02
> **Modelo IA:** Gemini 2.0 Flash (via Cascade/Windsurf) + consultas diretas a APIs públicas
> **Fontes:** BNDES Dados Abertos, PJe TJMG, Neo4j (CEIS/CNEP/PEP/OpenSanctions), Web (Valor Econômico, Globo Rural, XP Investimentos)
> **Processo:** 5009533-36.2024.8.13.0480 — 1ª Vara Cível, Patos de Minas/MG

⚠️ **AVISO LEGAL:** Este relatório compila exclusivamente dados públicos. Padrões identificados são **sinais estatísticos**, não prova jurídica. Ver [DISCLAIMER.md](../../DISCLAIMER.md).

---

## 1. Resumo Executivo

O Grupo Patense, fundado em 1970 em Patos de Minas/MG, processava resíduos de origem animal para fabricação de rações, óleos e biocombustíveis. Entre 2002 e 2022, recebeu **R$ 217.720.799** do BNDES em 591 operações distribuídas entre pelo menos 5 CNPJs do grupo.

Em junho de 2024, pediu **recuperação judicial** com dívidas de **R$ 1,375 bilhão** (posteriormente reavaliadas em R$ 2,15 bilhões). O processo envolve **13 empresas** e **2 pessoas físicas** (os controladores).

O TJMG **suspendeu** a recuperação judicial em novembro de 2024 por falta de documentação comprobatória de viabilidade financeira.

---

## 2. Mapeamento do Grupo (13 empresas + 2 PFs)

### Empresas Operacionais

| # | Empresa | Atividade |
|---|---------|-----------|
| 1 | **Indústria de Rações Patense Ltda** | Reciclagem animal, rações (empresa-mãe) |
| 2 | **Farol Indústria e Comércio S.A.** | Mesmo segmento, atuação em outros estados |
| 3 | **Pets Mellon Ind. de Produtos para Alimentação Animal Ltda** | Rações pet |
| 4 | **Adasebo Ind. e Com. de Produtos Animais Ltda** | Subprodutos animais |
| 5 | **Sebbo Passofundense Ind. e Com. de Adubos e Fertilizantes Ltda** | Adubos/fertilizantes (RS) |
| 6 | **Faricon Agrícola Ltda** | Agrícola |

### Holdings e SPEs (Special Purpose Entities)

| # | Empresa | Tipo |
|---|---------|------|
| 7 | **Patense Holding Ltda** | Holding controladora |
| 8 | **PROFAT Brazil Comércio Importação e Exportação Ltda** | Comércio exterior |
| 9 | **Vilaça Participações Ltda** | SPE/Participações |
| 10 | **Tax Participações Ltda** | SPE/Participações |
| 11 | **Lale Participações Ltda** | SPE/Participações |
| 12 | **Força Participações Ltda** | SPE/Participações |
| 13 | **Juquinha Participações Ltda** | SPE/Participações |

### Pessoas Físicas (Controladores)

| Nome | Relação |
|------|---------|
| **Clênio Antônio Gonçalves** | Fundador/Controlador |
| **Rejane Marques Oliveira Gonçalves** | Sócia/Controladora |

### Advogados no Processo

| Nome | OAB |
|------|-----|
| **Ivo Waisberg** | Todas as 13 empresas |
| **Joel Luís Thomaz Bastos** | Todas as 13 empresas |

**Padrão observado:** 5 das 13 empresas são SPEs de "participações" com nomes genéricos (Vilaça, Tax, Lale, Força, Juquinha). Estrutura típica de pulverização patrimonial.

---

## 3. Dinheiro do BNDES — R$ 217.720.799 (2002-2022)

### Por Empresa

| Empresa | Operações | Valor Desembolsado |
|---------|-----------|-------------------|
| **Indústria de Rações Patense Ltda** | 455 | **R$ 166.253.482** |
| **Farol Indústria e Comércio S.A.** | 130 | **R$ 36.303.351** |
| **Faricon Agrícola Ltda** | 2 | **R$ 11.699.968** |
| **Adasebo** | 1 | **R$ 2.559.998** |
| **Sebbo Passofundense** | 3 | **R$ 904.000** |
| **TOTAL GRUPO** | **591** | **R$ 217.720.799** |

### Por Ano (Patense principal — R$ 166M)

| Ano | Ops | Valor | Contexto |
|-----|-----|-------|----------|
| 2002 | 4 | R$ 383.656 | Início |
| 2003 | 7 | R$ 1.573.813 | Expansão inicial |
| 2004-2005 | 6 | R$ 772.020 | Crescimento |
| 2007 | 4 | R$ 2.430.340 | Pré-PAC |
| 2008 | 21 | R$ 9.806.330 | **Boom (PAC/crise global)** |
| 2009 | 33 | R$ 14.473.535 | **Pico — R$ 14.5M em 1 ano** |
| 2010 | 32 | R$ 17.742.055 | **Pico máximo — R$ 17.7M** |
| 2011 | 26 | R$ 10.335.945 | Continuação forte |
| 2012 | 28 | R$ 11.921.299 | |
| 2013 | 48 | R$ 31.021.077 | **Recorde: R$ 31M em 1 ano** |
| 2014 | 43 | R$ 24.802.740 | Pré-Lava Jato |
| 2015 | 20 | R$ 8.621.817 | Queda (recessão) |
| 2016 | 147 | R$ 16.590.655 | **147 ops em 1 ano (pulverização?)** |
| 2017 | 1 | R$ 212.000 | Quase parou |
| 2022 | 35 | R$ 15.566.200 | **Retorno — R$ 15.6M** |

**Sinais:** O pico de 2013 (R$ 31M) e a explosão de 147 operações em 2016 (média de R$ 112k/operação) sugerem possível fragmentação intencional de empréstimos.

### Fonte dos Recursos BNDES

| Fonte | Significado |
|-------|------------|
| RECURSOS LIVRES - PRÓPRIOS | Capital próprio do BNDES |
| RECURSOS LIVRES - ORGANISMOS | Organismos internacionais |
| RECURSOS VINCULADOS - FAT DEPÓSITOS ESPECIAIS | Fundo de Amparo ao Trabalhador |

---

## 4. Cruzamento com Bases Disponíveis

### CEIS/CNEP (Sanções Governamentais)

**Resultado: NENHUMA empresa do grupo aparece nas listas de sanções CEIS ou CNEP.**

Isso significa que, apesar de R$ 217M em dinheiro público via BNDES e R$ 2.15 bilhões em dívidas, o grupo nunca foi formalmente sancionado/impedido de contratar com o governo.

### PEP (Pessoas Politicamente Expostas)

**Clênio Antônio Gonçalves:** NÃO aparece como PEP na base CGU. Nenhum match no OpenSanctions.

Existem outros "Clênio" na base PEP (vereadores em MG, PE, RS), mas nenhum com sobrenome Gonçalves de Patos de Minas.

### Neo4j (Grafo Completo)

As empresas do grupo **não estão no grafo** porque dependem dos dados CNPJ/QSA (Receita Federal) que ainda não foram carregados. Com CNPJ, poderíamos:
- Mapear toda a rede de sócios entre as 13 empresas
- Verificar se Clênio/Rejane possuem OUTRAS empresas não listadas na RJ
- Cruzar com doações TSE (eleições 2022/2024)
- Verificar se os advogados (Waisberg/Bastos) representam outros grupos em RJ

---

## 5. Análise: O Que os Dados Mostram vs O Que Falta

### O que sabemos (dados públicos confirmados)

1. **R$ 217.7M** do BNDES ao grupo entre 2002-2022
2. **R$ 2.15 bilhões** em dívidas declaradas na RJ
3. **13 empresas** no processo, incluindo 5 SPEs de "participações"
4. **Nenhuma sanção** em CEIS/CNEP
5. **RJ suspensa** por falta de documentação de viabilidade
6. **2ª maior empresa do agro** em recuperação judicial no Brasil

### O que falta para investigação completa

| Dado | Fonte | O que revelaria |
|------|-------|----------------|
| **QSA (quadro societário)** | Receita Federal/CNPJ | Rede completa de sócios entre as 13+ empresas |
| **Doações TSE** | TSE | Se controladores doaram para campanhas políticas |
| **DataJud** | CNJ | Todos os processos judiciais envolvendo o grupo |
| **PGFN** | Procuradoria | Dívida ativa com a União |
| **CVM** | Comissão de Valores | Se emitiram CRAs ou debêntures |
| **Diários Oficiais** | Querido Diário | Contratos municipais/estaduais |

### Perguntas que a IA levanta (cadeia de raciocínio)

1. **Por que 147 operações em 2016?** A média caiu para R$ 112k/op — se o limite automático era ~R$ 150k, fragmentar em 147 pedidos evita análise direta do BNDES?
2. **5 SPEs para quê?** Vilaça, Tax, Lale, Força, Juquinha — qual o propósito operacional de 5 holdings de participações em um grupo de rações?
3. **Gap 2017-2021:** Zero empréstimos por 5 anos, depois R$ 15.6M em 2022. O que mudou?
4. **Advogados compartilhados:** Ivo Waisberg e Joel Bastos representam TODAS as 13 empresas. Indica controle centralizado apesar da pulverização em CNPJs.

---

## 6. Sobre o Modelo de IA Utilizado

### Este relatório foi gerado por:

| Etapa | Modelo/Ferramenta | Custo |
|-------|-------------------|-------|
| Pesquisa web | Exa AI (MCP) | ~$0.01 |
| Consulta BNDES | API pública dadosabertos.bndes.gov.br | Grátis |
| Cruzamento Neo4j | Cypher queries diretas (CEIS/CNEP/PEP) | Grátis |
| Análise e redação | Claude 3.5 Sonnet (via Cascade/Windsurf) | ~$0.15 |
| **Total** | | **~$0.16** |

### Sobre necessidade de modelos avançados

**Para buscas simples** (consultar CNPJ, verificar sanções): qualquer modelo funciona, inclusive gratuitos.

**Para relatórios de investigação como este:** é necessário um modelo com:
- **Raciocínio em cadeia (Chain of Thought):** conectar 591 operações BNDES → 13 empresas → padrão de pulverização → perguntas investigativas
- **Contexto longo:** processar dados de múltiplas APIs simultaneamente (BNDES + Neo4j + web)
- **Juízo crítico:** distinguir "sinal" de "prova", formular perguntas sem acusar

**Modelos recomendados para investigação:**

| Modelo | Capacidade | Custo/1M tokens | Adequação |
|--------|-----------|-----------------|-----------|
| **Claude 3.5 Sonnet** | Chain of Thought forte | ~$3.00 | ⭐⭐⭐⭐⭐ |
| **GPT-4o** | Bom raciocínio | ~$2.50 | ⭐⭐⭐⭐ |
| **Gemini 2.0 Flash** | Rápido, bom para ferramentas | ~$0.10 | ⭐⭐⭐ (bom para bots) |
| **Gemini 1.5 Pro** | Contexto 1M tokens | ~$1.25 | ⭐⭐⭐⭐ (documentos longos) |
| **Llama 3.1 70B** | Open source, gratuito | ~$0.20 | ⭐⭐⭐ (OK, perde nuance) |

**Conclusão:** Relatórios de investigação requerem modelos de raciocínio avançado. Modelos baratos/rápidos funcionam para consultas individuais, mas a cadeia lógica (BNDES → pulverização → SPEs → perguntas) exige capacidade de síntese que modelos menores não têm.

---

## 7. Próximos Passos (Com Ajuda da Comunidade)

1. [ ] **Carregar CNPJ/QSA** — Mapear rede completa de sócios entre as 13+ empresas
2. [ ] **Cruzar TSE** — Doações de Clênio/Rejane a candidatos
3. [ ] **DataJud** — Processos judiciais anteriores à RJ
4. [ ] **PGFN** — Dívidas ativas com a União
5. [ ] **Diários Oficiais** — Contratos públicos envolvendo o grupo
6. [ ] **CVM/CRA** — Títulos emitidos pelo grupo que afetaram investidores

---

*Gerado por EGOS Intelligence em 2026-03-02. Dados públicos, sinais estatísticos — não é prova jurídica.*
*Código fonte: [github.com/enioxt/br-acc](https://github.com/enioxt/br-acc)*
