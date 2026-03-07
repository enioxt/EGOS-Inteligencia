# Contributing to BR/ACC Open Graph

Language: **English** | [Português (Brasil)](docs/pt-BR/CONTRIBUTING.md)

Thanks for helping improve BR/ACC Open Graph.

## Ground Rules

- Keep changes aligned with public-interest transparency goals.
- Do not add secrets, credentials, or private infrastructure details.
- Respect public-safe defaults and privacy/legal constraints.

## Development Setup

```bash
cd api && uv sync --dev
cd ../etl && uv sync --dev
cd ../frontend && npm install
```

## Scripts and automation

The repo includes optional scripts. The **BR-ACC Upstream Monitor** (TASK-013) runs twice daily via GitHub Actions to track upstream forks, open PRs, issues, and roadmap suggestions; see [scripts/README-bracc-monitor.md](scripts/README-bracc-monitor.md) for usage and env vars.

## Quality Checks

Run these before opening a pull request:

```bash
make check
make neutrality
```

## Pull Request Expectations

- Keep PR scope focused and explain the user impact.
- Include tests for behavior changes.
- Update docs when interfaces or workflows change.
- Ensure all required CI and security checks are green.

## AI-Assisted Contributions

AI-assisted contributions are allowed.  
Human contributors remain responsible for:

- technical correctness,
- security/privacy compliance,
- and final review/sign-off before merge.
