# Perguntas Frequentes (FAQ) — EGOS Inteligência

> **Para cidadãos, jornalistas e pesquisadores.** Sem jargão técnico.

---

## O que é o EGOS Inteligência?

É uma plataforma gratuita e de código aberto que cruza dados públicos brasileiros para que qualquer pessoa possa pesquisar conexões entre empresas, políticos, contratos e sanções governamentais.

Pense nele como um "Google para dinheiro público" — você digita o nome de uma empresa ou CNPJ e vê todas as relações que ela tem com o governo: contratos ganhos, sanções recebidas, doações eleitorais, empréstimos do BNDES, e mais.

## Para quem é?

- **Cidadãos curiosos** que querem saber como o dinheiro público é gasto
- **Jornalistas** investigando conexões entre empresas e governo
- **Pesquisadores acadêmicos** estudando governança e transparência
- **Organizações da sociedade civil** monitorando contratos públicos
- **Servidores públicos** buscando informações sobre fornecedores

## Preciso pagar algo?

Não. O EGOS Inteligência é 100% gratuito e de código aberto (licença AGPL-3.0). Qualquer pessoa pode usar, e qualquer desenvolvedor pode verificar, melhorar ou auditar o código.

## De onde vêm os dados?

Todos os dados são **públicos e oficiais**, coletados de fontes governamentais abertas. Hoje temos 36 fontes integradas (108 mapeadas), incluindo:

| Fonte | O que tem | Exemplos |
|-------|-----------|----------|
| **Receita Federal (CNPJ)** | Cadastro de todas as empresas do Brasil | Razão social, sócios, endereço, atividade |
| **Portal da Transparência** | Contratos e servidores federais | Quem ganhou licitação, quanto recebeu |
| **CEIS/CNEP** | Empresas e pessoas impedidas de contratar com o governo | Sanções por irregularidades |
| **TSE** | Doações eleitorais e patrimônio de candidatos | Quem doou para quem, quanto declarou |
| **BNDES** | Empréstimos do banco de desenvolvimento | Quanto cada empresa recebeu |
| **IBAMA** | Embargos ambientais | Áreas embargadas por desmatamento |
| **ComprasNet/PNCP** | Licitações federais | 1 milhão+ de contratos |
| **Câmara/Senado** | Gastos parlamentares (CEAP/CEAPS) | Como deputados e senadores usam a cota |
| **ICIJ** | Panama Papers, Paradise Papers, Pandora Papers | Offshores ligadas a brasileiros |
| **OpenSanctions** | Pessoas Politicamente Expostas (PEPs) globais | Lista internacional de PEPs |

A lista completa está em [data-sources.md](data-sources.md).

## O que é um "grafo de conhecimento"?

É um mapa de conexões. Em vez de ver dados em tabelas separadas (uma tabela de empresas, outra de contratos, outra de sanções), o grafo conecta tudo: a empresa X ganhou o contrato Y, foi sancionada na lista Z, recebeu empréstimo W do BNDES, e seu sócio doou para o candidato K.

Essas conexões são o que tornam o EGOS Inteligência diferente de simplesmente consultar o site da Receita Federal ou do Portal da Transparência — aqui, você vê o **quadro completo**.

## O que é ETL?

ETL significa **Extract, Transform, Load** (Extrair, Transformar, Carregar). É o processo automático de:

1. **Extrair** — Baixar dados brutos das fontes governamentais (planilhas, CSVs, APIs)
2. **Transformar** — Limpar, padronizar e cruzar os dados (por exemplo, conectar uma empresa pelo CNPJ em diferentes bases)
3. **Carregar** — Inserir os dados no grafo de conhecimento, criando as conexões

Toda grande empresa de tecnologia usa ETL — Google, Meta, bancos, fintechs, a própria Receita Federal. A diferença é que o nosso é de código aberto: qualquer pessoa pode ver exatamente como os dados são processados.

## Isso é legal?

Sim. Todos os dados utilizados são **públicos e de acesso aberto**, disponibilizados pelo próprio governo através de portais de transparência, Lei de Acesso à Informação (LAI) e dados abertos.

O EGOS Inteligência é uma ferramenta de **pesquisa pessoal**. Padrões encontrados são sinais estatísticos, não prova jurídica ou acusação de qualquer tipo.

## Vocês identificam CPFs?

Não. O sistema foi projetado para **não expor dados pessoais sensíveis**. CPFs são bloqueados em todas as buscas e respostas, em conformidade com a LGPD (Lei Geral de Proteção de Dados).

## Posso confiar nos dados?

Os dados vêm diretamente de fontes oficiais do governo brasileiro, sem alteração. Cada informação tem atribuição de fonte — você sempre sabe de onde veio.

Porém, é importante entender:
- Dados governamentais podem ter atrasos na atualização
- Homônimos podem gerar falsos cruzamentos
- Padrões estatísticos não são prova — são pistas para investigação mais aprofundada

## Como posso usar?

### No site
Acesse [inteligencia.egos.ia.br](https://inteligencia.egos.ia.br) e use o chat para fazer perguntas em linguagem natural. Exemplos:

- "Buscar empresa Galvão Engenharia"
- "Quantas entidades tem no grafo?"
- "Empresas sancionadas no CEIS e CNEP ao mesmo tempo"

### Nos bots
- **Telegram:** Converse com [@EGOSin_bot](https://t.me/EGOSin_bot)
- **Discord:** Junte-se ao servidor e use o bot EGOS Intelligence

### Na API
Desenvolvedores podem acessar diretamente: `GET /api/v1/search?q=termo`

## O que vocês NÃO têm (ainda)?

Somos honestos sobre as limitações atuais:

- **CNPJ/QSA completo** — Estamos carregando 53 milhões de empresas (em andamento)
- **DataJud** — Dados judiciais do CNJ (planejado)
- **Dados municipais** — Apenas dados federais por enquanto
- **Algoritmos avançados** — PageRank, detecção de comunidades e anomalias estão planejados
- **Dados em tempo real** — Atualizações são periódicas, não instantâneas

## Como posso contribuir?

- **Código:** O repositório está em [github.com/enioxt/EGOS-Inteligencia](https://github.com/enioxt/EGOS-Inteligencia)
- **Reportar erros:** Abra uma issue no GitHub
- **Sugerir fontes de dados:** Use o bot ou abra uma issue
- **Divulgar:** Compartilhe com jornalistas, pesquisadores e cidadãos interessados

## Quem mantém o projeto?

O EGOS Inteligência é parte do ecossistema [EGOS](https://egos.ia.br) — um projeto independente de código aberto focado em transparência e governança com inteligência artificial.

---

*"Siga o dinheiro público. Dados abertos, código aberto."*
