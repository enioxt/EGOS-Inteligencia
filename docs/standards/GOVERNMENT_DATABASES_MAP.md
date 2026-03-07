# Mapa de Bases de Dados Governamentais — EGOS Inteligência

> **Versão:** 1.0.0 | **Data:** 2026-03-06
> **Objetivo:** Mapear todas as bases públicas e restritas relevantes para
> investigações de inteligência financeira e compliance no Brasil.

---

## 1. Bases Públicas (Acessíveis — já integradas ou planejadas)

| Base | Órgão | Status no EGOS | Dados |
|------|-------|----------------|-------|
| **CNPJ/QSA** | Receita Federal | ✅ ETL ativo (~70%) | Empresas, sócios, situação cadastral |
| **CEIS** | CGU/Portal Transparência | ✅ ETL ativo (23.848 sanções) | Empresas inidôneas e suspensas |
| **CNEP** | CGU/Portal Transparência | ✅ ETL ativo | Empresas punidas (não suspensas) |
| **CVM** | gov.br/cvm | 🔄 Manual | Processos administrativos, fundos, participantes |
| **DOU** | Imprensa Nacional | 🔄 Manual | Diário Oficial da União |
| **DataJud** | CNJ | ⚠️ Pipeline existe, 0 dados | Processos judiciais (cível, criminal, trabalhista) |
| **Querido Diário** | Open Knowledge Brasil | 📋 Planejado | Diários Oficiais municipais/estaduais |
| **BNDES** | BNDES | 📋 Planejado | Contratos e operações de financiamento |
| **TSE** | TSE | 📋 Planejado | Candidatos, doações, prestação de contas |
| **Portal de Compras** | ME | 📋 Planejado | Licitações e contratos federais |
| **IBGE** | IBGE | 📋 Planejado | Dados socioeconômicos por município |
| **BNMP** | CNJ | 📋 Planejado | Mandados de prisão (parcialmente público) |
| **PEP** | CGU | 📋 Planejado | Pessoas Expostas Politicamente |
| **CEAF** | CGU | 📋 Planejado | Expulsões da administração federal |
| **Extrateto** | CNJ | 📋 Planejado | Remunerações acima do teto do Judiciário |

---

## 2. Bases Restritas (Acesso apenas por autoridades)

> **Estas bases NÃO são acessíveis ao público.** Listamos aqui para que
> autoridades que utilizem nossa ferramenta saibam quais cruzamentos
> seriam possíveis com seus acessos legais.

| Base | Órgão | Acesso | Dados |
|------|-------|--------|-------|
| **COAF/UIF** | Min. Fazenda | Autoridades financeiras | Comunicações de operações suspeitas (CTOs) |
| **SIMBA** | Banco Central | Ordem judicial | Movimentação bancária completa |
| **SISBACEN** | Banco Central | Autoridades regulatórias | Operações de câmbio, dados financeiros |
| **CCS** | Banco Central | Autoridades | Cadastro de Clientes do SFN (quem tem conta onde) |
| **INFOSEG** | SENASP/MJ | Polícias, MP | Dados policiais integrados (mandados, inquéritos) |
| **SISCOAF** | COAF | Instituições obrigadas | Comunicações de atividades financeiras suspeitas |
| **RFB Fiscal** | Receita Federal | Sigilo fiscal | IRPF, IRPJ, DCTF, DIRF completos |
| **DETRAN** | Cada estado | Convênio policial | Dados veiculares completos, infrações |
| **RENAVAM** | DENATRAN | Autoridades | Registro nacional de veículos |
| **CAGED/RAIS** | MTE | Acesso detalhado restrito | Emprego formal por empresa (nível individual) |
| **SEEU** | CNJ | Juízes, MP | Execução penal unificada |
| **DRCI** | Min. Justiça | Cooperação internacional | Recuperação de ativos internacionais |
| **INTERPOL I-24/7** | INTERPOL | Polícias | Alertas e difusões internacionais |
| **SISBIN** | ABIN | Inteligência de Estado | Dados de inteligência integrados |
| **COFI/BCB** | Banco Central | Interno BCB | Supervisão prudencial de instituições financeiras |

---

## 3. Proposta de Valor para Autoridades

### O que oferecemos (gratuito, código aberto)

1. **Infraestrutura de cruzamento** — Neo4j com 141M+ nós de dados públicos
2. **ETL industrializado** — pipelines testados para ingestão de múltiplas fontes
3. **Provenance/Não-repúdio** — hash SHA-256 por registro, rastreabilidade completa
4. **Visualização de grafos** — frontend para navegação de relações corporativas
5. **Relatórios auditáveis** — formato padronizado, fontes explícitas, sem acusações
6. **Código auditável** — AGPL v3, qualquer órgão pode auditar e forkar

### O que as autoridades adicionam

Com acesso às bases restritas (COAF, SIMBA, CCS, INFOSEG), os cruzamentos
possíveis **multiplicam exponencialmente**:

- CNPJ público + COAF = detectar empresas com comunicações de suspeição
- QSA público + CCS = mapear onde cada sócio tem contas
- Sanções CEIS + SIMBA = rastrear fluxo financeiro de empresas sancionadas
- DataJud + INFOSEG = cruzar processos judiciais com inquéritos policiais

### Como colaborar

> Sou Enio Rocha, desenvolvedor, e disponibilizo esta ferramenta e meu
> trabalho gratuitamente para qualquer órgão público brasileiro que deseje
> implementar ou adaptar esta infraestrutura. O código é livre (AGPL v3).
> Podemos unir forças com organizações que já atuam nessa área no Brasil.
>
> - **GitHub:** github.com/enioxt/EGOS-Inteligencia
> - **Contato:** via GitHub Issues ou email no perfil
> - **Código:** fork livre, contribuições bem-vindas

---

## 4. Limitações Declaradas

1. **Apenas dados públicos.** Não acessamos nenhuma base restrita.
2. **ETL em progresso.** Nem todas as bases públicas estão 100% ingeridas.
3. **Dados podem estar desatualizados.** Dependemos dos ciclos de publicação oficiais.
4. **Erros são possíveis.** Convidamos correções via GitHub Issues.
5. **Não somos autoridade.** Não investigamos, não acusamos, não julgamos.

---

*EGOS Inteligência — Código aberto, dados públicos, transparência radical.*
