# Registro de Atividades de Tratamento — LGPD Art. 37

**Controlador:** EGOS Inteligência (World Transparency Graph)
**Versão:** 1.0.0
**Data:** 2026-03-03
**Encarregado (DPO):** Via GitHub Issues ([template de privacidade](https://github.com/enioxt/EGOS-Inteligencia/issues/new?template=data_correction.yml))

---

## 1. Dados Públicos de Empresas (CNPJ)

| Campo | Valor |
|-------|-------|
| **Categoria** | Dados públicos de pessoa jurídica |
| **Fonte** | Receita Federal — Dados Abertos CNPJ |
| **Base Legal** | LGPD Art. 7°, IV (estudos por órgão de pesquisa) + Art. 7°, §4° (dados tornados públicos pelo titular) + LAI (Lei 12.527/2011) |
| **Finalidade** | Transparência pública, análise de vínculos societários, detecção de padrões em contratações |
| **Dados Tratados** | Razão social, CNPJ, endereço comercial, CNAE, situação cadastral, capital social, quadro societário (nomes + qualificação) |
| **Dados Excluídos** | CPF de sócios (mascarado), dados pessoais sensíveis |
| **Retenção** | Enquanto os dados forem públicos na fonte original. Atualização a cada nova publicação da Receita Federal |
| **Compartilhamento** | Nenhum. Dados acessíveis apenas via API pública do EGOS Inteligência |
| **Medidas de Segurança** | CPF masking middleware, public_guard.py bloqueia lookup de pessoas, HTTPS obrigatório |

## 2. Dados Eleitorais (TSE)

| Campo | Valor |
|-------|-------|
| **Categoria** | Dados públicos eleitorais |
| **Fonte** | Tribunal Superior Eleitoral — Repositório de Dados Eleitorais |
| **Base Legal** | LAI + LGPD Art. 7°, §4° (dados tornados públicos) |
| **Finalidade** | Mapeamento de doações eleitorais, patrimônio declarado, filiações partidárias |
| **Dados Tratados** | Nome de candidato, número, partido, votos, doações (valor + doador CNPJ), bens declarados |
| **Dados Excluídos** | CPF de eleitores, dados biométricos |
| **Retenção** | Permanente (dados históricos eleitorais são de interesse público) |
| **Compartilhamento** | Nenhum |
| **Medidas de Segurança** | Mesmas do item 1 |

## 3. Contratos e Licitações Públicas

| Campo | Valor |
|-------|-------|
| **Categoria** | Dados públicos de contratações governamentais |
| **Fonte** | Portal da Transparência, ComprasNet, PNCP, TransfereGov |
| **Base Legal** | LAI Art. 8° (transparência ativa) + LGPD Art. 7°, §4° |
| **Finalidade** | Análise de concentração de fornecedores, detecção de fracionamento, auditoria social |
| **Dados Tratados** | Objeto do contrato, valor, CNPJ do fornecedor, órgão contratante, modalidade, datas |
| **Dados Excluídos** | CPF de servidores responsáveis (quando disponível, é mascarado) |
| **Retenção** | Permanente (interesse público) |
| **Compartilhamento** | Nenhum |
| **Medidas de Segurança** | Rate limiting, cache-aside, circuit breaker para APIs externas |

## 4. Sanções e Impedimentos

| Campo | Valor |
|-------|-------|
| **Categoria** | Dados públicos de sanções administrativas |
| **Fonte** | CEIS, CNEP, TCU, CEAF, CEPIM, OFAC, EU/UN Sanctions, OpenSanctions |
| **Base Legal** | LAI + LGPD Art. 7°, §4° + interesse legítimo em prevenção de fraude |
| **Finalidade** | Identificar empresas/pessoas impedidas de contratar com o governo |
| **Dados Tratados** | Nome/razão social, CNPJ, tipo de sanção, período, órgão sancionador |
| **Dados Excluídos** | CPF (mascarado quando presente) |
| **Retenção** | Enquanto a sanção estiver vigente + 5 anos após término |
| **Compartilhamento** | Nenhum |
| **Medidas de Segurança** | Mesmas do item 1, neutralidade linguística obrigatória |

## 5. Pessoas Politicamente Expostas (PEP)

| Campo | Valor |
|-------|-------|
| **Categoria** | Dados públicos de agentes públicos |
| **Fonte** | CGU — Lista PEP, Servidores Federais (Portal da Transparência) |
| **Base Legal** | LAI Art. 8° (transparência ativa de remunerações) + LGPD Art. 7°, §4° |
| **Finalidade** | Identificar conflitos de interesse, enriquecimento patrimonial, vínculos societários |
| **Dados Tratados** | Nome, cargo, órgão, remuneração bruta (dados já públicos pelo Portal da Transparência) |
| **Dados Excluídos** | CPF (mascarado), endereço pessoal, dados sensíveis |
| **Retenção** | Enquanto o dado for público na fonte original |
| **Compartilhamento** | Nenhum |
| **Medidas de Segurança** | public_guard.py bloqueia lookup de Person nodes em modo público |

## 6. Dados de Interação (Chat/API)

| Campo | Valor |
|-------|-------|
| **Categoria** | Dados de uso do serviço |
| **Fonte** | Interação do usuário com a API |
| **Base Legal** | LGPD Art. 7°, I (consentimento implícito pelo uso) + Art. 7°, IX (interesse legítimo: segurança) |
| **Finalidade** | Manutenção do serviço, rate limiting, detecção de abuso |
| **Dados Tratados** | IP (hash), queries de busca, conversation_id, timestamps |
| **Dados Excluídos** | Nenhum dado pessoal é coletado deliberadamente |
| **Retenção** | Conversas: 30 min TTL em memória. Logs: 7 dias. Activity feed: 500 eventos em memória |
| **Compartilhamento** | Nenhum |
| **Medidas de Segurança** | Rate limiting (60/min anon, 300/min auth), prompt injection detection, IP hashing |

---

## Medidas Técnicas e Organizacionais

| Medida | Implementação |
|--------|---------------|
| **CPF Masking** | Middleware automático em todas as respostas da API (`CPFMaskingMiddleware`) |
| **Public Guard** | Bloqueia lookup de Person/Partner nodes em modo público (`public_guard.py`) |
| **Neutralidade** | CI automatizado proíbe palavras acusatórias no código-fonte (9 termos bloqueados) |
| **Rate Limiting** | SlowAPI: 60 req/min anônimo, 300 req/min autenticado, 30 req/min chat |
| **HTTPS** | Caddy com TLS automático para todos os endpoints |
| **CORS** | Headers explícitos (Authorization, Content-Type, Accept, Origin, X-Requested-With) |
| **Prompt Injection** | 10 padrões regex monitorados, logging sem bloqueio |
| **Circuit Breaker** | Proteção contra cascading failures em APIs externas |
| **Backup** | Neo4j: backup diário às 3AM, retenção de 5 últimos |
| **Código Aberto** | Todo o código é auditável em github.com/enioxt/EGOS-Inteligencia |

## Direitos do Titular (LGPD Art. 18)

Requisições de acesso, correção ou eliminação devem ser feitas via:

1. **GitHub Issue:** [Template de correção de dados](https://github.com/enioxt/EGOS-Inteligencia/issues/new?template=data_correction.yml)
2. **Prazo:** 15 dias úteis para resposta (LGPD Art. 18, §5°)
3. **Processo:** Registro → Verificação de escopo → Decisão com fundamentação → Comunicação ao titular

---

*Documento mantido conforme LGPD Art. 37. Última atualização: 2026-03-03.*
