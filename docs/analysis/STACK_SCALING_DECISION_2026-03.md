# Python vs Go vs Node.js para escalar o EGOS (2026-03)

## Resposta curta

- **Não migrar o core para Go ou Node.js agora.**
- **Manter Python** no backend e ETL, e atacar primeiro os gargalos reais: Neo4j, política de consumo de APIs externas, cache e fila.
- **Extrair para Go apenas hotspots medidos** (se houver componentes com pressão de throughput/CPU muito alta).
- **Manter Node.js** onde já faz sentido (bots/eventos e frontend).

## Quais APIs/integrações estão realmente no stack hoje

### No backend/chat tools
- Portal da Transparência (`api.portaldatransparencia.gov.br`) em tools de transparência.
- TransfereGov (`api.transferegov.gestao.gov.br`) em tools de transferências.
- Brave Search API (quando `BRAVE_API_KEY` existe), com fallback para DuckDuckGo HTML.

### Em scripts/downloader
- TSE (downloads por URL de dataset público).
- OpenSanctions (download de datasets JSON).
- ICIJ Offshore Leaks.
- Câmara dos Deputados (arquivos CSV de dados abertos).
- Portais com bloqueio/captcha já estão documentados com estratégia de download manual.

## Limites já implementados

### Entrada no EGOS API
- Rate limit padrão para anônimos: `60/minute`.
- Limite para autenticados configurável (`rate_limit_auth`, default `300/minute`).
- Chave de rate limit por usuário JWT (quando houver token) com fallback para IP.

### Respeito à fonte externa
- Script do DataJud com `RATE_LIMIT_SEC=1` (1 requisição/segundo) por padrão.
- Download batch com retries/timeouts no script geral de datasets.
- Vários scripts ETL já tratam `429`/retentativas com backoff.


## Inventário validado no código (Go/Python/Node/LLMs)

### Linguagens/stack em uso
- **Python** no core de API e ETL (FastAPI, pipelines e integrações de dados).
- **Node.js** já está no ecossistema para bots e frontend (coerente com o posicionamento do projeto).
- **Go** não aparece como stack produtiva atual no repositório.

### LLMs e roteamento
- Configuração expõe `openrouter_api_key` e `ai_model`, indicando uso de roteamento de modelo via OpenRouter no backend.
- O risco de custo de LLM é real para MVP e precisa de orçamento/guardrails operacionais.

### Limites observáveis hoje
- Entrada da API pública: `rate_limit_anon=60/minute` e `rate_limit_auth=300/minute` (padrão).
- Rate limit por usuário autenticado (JWT) com fallback para IP.
- DataJud downloader com `RATE_LIMIT_SEC=1` e espera explícita entre requisições.
- Script de download geral usa retry e timeout em `aria2c`, mas sem orçamento unificado por provedor.

### Gap atual (o que ainda falta formalizar)
- Não há matriz versionada de orçamento por fonte (`qps_max`, `req/dia`, janela de pausa).
- Não há documento único com orçamento de custo de LLM por ferramenta/ambiente.

## Onde está o risco real (e por que trocar linguagem não resolve sozinho)

1. **Overload em APIs governamentais**
   - Risco técnico e de compliance existe se o consumo não tiver orçamento por fonte.
   - Mudar Python para Go não muda a necessidade de throttling, janelas de coleta e idempotência.

2. **Custo de LLM no MVP**
   - Existe risco de custo variável por volume e ferramentas dependentes de API externa.
   - O controle é de produto e operação: budget mensal, fallback de modelo e roteamento por tipo de pergunta.

3. **Latência de query no banco de grafo**
   - O gargalo de escala tende a estar em modelagem/índice/query no Neo4j e cache hit-rate, não na linguagem da API.

## Como contornar com menor risco

### 1) Orçamento por fonte (obrigatório)
- Definir **QPS por host** (ex.: 0.2–1 req/s em fontes sensíveis).
- Definir **limite diário** por conector.
- Aplicar **token bucket** por provedor e trava global.

### 2) Fila e workers para ingestão
- Colocar coleta/enriquecimento em jobs assíncronos (não no caminho síncrono do usuário).
- Adicionar DLQ, retries com jitter e idempotência por `run_id`.

### 3) Circuit breaker por provedor
- Ao detectar 429/5xx em sequência, pausar automaticamente o conector por janela.
- Retomar de forma gradual para evitar rajada de volta.

### 4) Priorizar dumps oficiais e incremental
- Preferir dumps/arquivos oficiais em lote quando existir.
- Rodar apenas delta incremental por data/ID.

### 5) Governança de LLM
- Budget mensal por ambiente (dev/staging/prod).
- Política de fallback para modelo mais barato e cache de respostas repetitivas.
- Métrica de custo por ferramenta e por tipo de pergunta.

## Previsão prática de evolução (90 dias)

### Fase 1 (0–30 dias)
- Matriz de orçamento por fonte (`qps_max`, `requests_dia`, `janela`), versãoada em repositório.
- Métricas mínimas: erro 429/5xx por fonte, latência p95 por endpoint, hit-rate de cache.

### Fase 2 (31–60 dias)
- Circuit breaker + fila para conectores mais sensíveis.
- SLO para API pública (disponibilidade e p95) e regra de degrade controlado.

### Fase 3 (61–90 dias)
- Benchmark de hotspots reais.
- Somente aqui decidir extração cirúrgica para Go (se algum componente continuar gargalo).

## Critério objetivo para considerar Go

Migrar um componente isolado para Go **apenas se**:
- p95/p99 seguir fora de alvo após otimização de query+cache+fila;
- componente for claramente CPU-bound ou de altíssimo fan-out;
- houver contrato de interface estável para separar sem reescrever domínio inteiro.

## Conclusão

- **Python continua a melhor base do EGOS hoje** pelo ecossistema de dados/ETL e maturidade já existente no projeto.
- **Node.js permanece adequado para bots/eventos/frontend**.
- **Escala segura depende mais de política de consumo externo + arquitetura operacional** do que de troca de linguagem.
