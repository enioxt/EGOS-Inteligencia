# Gap Analysis de mercado (referências para benchmarking)

> Objetivo: mapear categorias de soluções globais relevantes para comparar arquitetura, custo e risco antes da implementação final.

## 1) Categorias-chave de referência

1. **Workflow/orquestração**: Temporal, Conductor/Orkes, Camunda
2. **Automation/iPaaS**: n8n, Make, Zapier, Workato
3. **Chatbot/IA enterprise**: Microsoft Copilot stack, Salesforce Einstein, Intercom Fin, Zendesk AI
4. **E-mail inteligência**: Superhuman AI features, Front, Missive, Gmail/Outlook + AI copilots
5. **WhatsApp enterprise**: Meta Cloud API, Twilio, BSPs locais
6. **Observabilidade/AIOps**: Datadog, New Relic, Grafana Cloud, Elastic

---

## 2) Matriz de decisão sugerida

Avaliar cada fornecedor em:

- Tempo de implantação
- Custo total (fixo + variável)
- Suporte no Brasil
- Compliance/LGPD/GDPR
- Qualidade de API e webhooks
- Confiabilidade/SLA
- Facilidade de auditoria e trilha de decisão
- Lock-in e portabilidade

---

## 3) Gaps críticos identificados para o plano atual

1. **Catálogo formal de políticas** por ação/tenant ainda não consolidado.
2. **Estratégia de fallback multicanal** (WhatsApp indisponível -> e-mail/app) precisa virar contrato técnico.
3. **Métricas de qualidade do agente** (assertividade de classificação/sugestão de resposta) ainda não definidas.
4. **Gestão de prompts e versões** com auditoria por tenant precisa ser padrão desde o início.
5. **Teste de usabilidade extrema** (mão de obra de campo, baixa literacia digital) deve entrar no ciclo de release.

---

## 4) Recomendação prática

- Executar um piloto curto com 1 stack por categoria (workflow, WhatsApp, e-mail).
- Medir SLA real, custo por operação e taxa de erro.
- Só depois fixar contratos de longo prazo com fornecedores.
