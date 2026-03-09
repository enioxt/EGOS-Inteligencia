# Documentação do EGOS Inteligência

Este diretório centraliza documentação técnica, operacional, legal e material de demonstração do projeto.

## Navegação rápida

### Governança e operação
- [Política de atualização diária](DAILY_UPDATE_POLICY.md)
- [Lições aprendidas](LESSONS_LEARNED.md)
- [Governança de PR de IA](ai-pr-governor.md)

### Dados e ETL
- [Fontes de dados (visão geral)](data-sources.md)
- [Contrato de onboarding de fontes](source_onboarding_contract.md)
- [Registro de fontes (CSV)](source_registry_br_v1.csv)
- [Contrato do dataset demo](demo/dataset-contract.md)

### Release pública
- [Checklist de release público](release/public_repo_release_checklist.md)
- [Runbook de release](release/release_runbook.md)
- [Política de release](release/release_policy.md)
- [Taxonomia de labels](release/label_taxonomy.md)
- [Matriz de endpoints públicos](release/public_endpoint_matrix.md)
- [Matriz de boundary público (CSV)](release/public_boundary_matrix.csv)

### Compliance e jurídico
- [Índice legal (EN)](legal/legal-index.md)
- [Pacote público de compliance](legal/public-compliance-pack.md)
- [Índice legal (PT-BR)](pt-BR/legal-index.md)

### Documentação em português
- [README (PT-BR)](pt-BR/README.md)
- [Contribuição (PT-BR)](pt-BR/CONTRIBUTING.md)
- [FAQ (PT-BR)](pt-BR/FAQ.md)
- [Download de dados (PT-BR)](pt-BR/DOWNLOAD_DADOS.md)

### Relatórios e análises
- [Relatórios](reports/)
- [Análises](analysis/)
- **[Capacidades do Sistema (Março 2026)](SYSTEM_CAPABILITIES_2026-03.md)** — 26 tools testadas, 42 endpoints, 14 APIs, comparação competitiva brutal
- **[Dossiê Técnico Completo (Março 2026)](TECHNICAL_DOSSIE_2026-03.md)** — Audit: arquitetura, features, riscos, LGPD, 13 tasks
- [Avaliação Honesta](HONEST_ASSESSMENT_2026-03.md) — O que funciona e o que não funciona (de verdade)
- [Análise Comparativa Intelink vs EGOS](MERGE_ANALYSIS.md) — Alternativas de merge, recomendação
- [Decisão de stack e escala (Python/Go/Node)](analysis/STACK_SCALING_DECISION_2026-03.md)
- [Plano Mycelium Audit Trail (não repúdio)](analysis/MYCELIUM_AUDIT_TRAIL_2026-03.md)
- [Showcase](showcase/)
- [Planos](plans/)

### Para novos contribuidores
- [README principal (setup local, API keys, IDEs)](../README.md#opção-3-rodar-localmente)
- [GitHub Issues abertas](https://github.com/enioxt/EGOS-Inteligencia/issues) — issues #44-#48 com instruções claras
- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [TASKS.md](../TASKS.md) — todas as tasks com status real

## Convenções

- Sempre prefira Markdown para documentação textual.
- Mantenha links relativos para funcionar no GitHub e em clones locais.
- Ao adicionar arquivos novos, atualize este índice para manter descoberta rápida.
