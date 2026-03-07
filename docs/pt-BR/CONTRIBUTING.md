# Contribuindo com o BR/ACC Open Graph

Idioma: [English](../../CONTRIBUTING.md) | **Português (Brasil)**

Obrigado por contribuir com o BR/ACC Open Graph.

## Regras Gerais

- Mantenha as mudanças alinhadas ao objetivo de transparência de interesse público.
- Não adicione segredos, credenciais ou detalhes de infraestrutura privada.
- Respeite defaults públicos de segurança, privacidade e compliance.

## Setup de Desenvolvimento

```bash
cd api && uv sync --dev
cd ../etl && uv sync --dev
cd ../frontend && npm install
```

## Scripts e automação

O repositório inclui scripts opcionais. O **Monitor do upstream BR-ACC** (TASK-013) roda 2x ao dia via GitHub Actions para acompanhar forks, PRs e issues do upstream e sugestões de roadmap; ver [scripts/README-bracc-monitor.md](../../scripts/README-bracc-monitor.md) para uso e variáveis de ambiente.

## Checagens de Qualidade

Execute antes de abrir PR:

```bash
make check
make neutrality
```

## Expectativas para Pull Request

- Mantenha o escopo da PR focado e explique o impacto para usuário.
- Inclua testes para mudanças de comportamento.
- Atualize documentação quando interfaces ou fluxos mudarem.
- Garanta todos os checks obrigatórios verdes no CI.

## Contribuições com Assistência de IA

Contribuições com assistência de IA são permitidas.  
Contribuidores humanos continuam responsáveis por:

- correção técnica,
- conformidade de segurança e privacidade,
- revisão final e aprovação antes do merge.
