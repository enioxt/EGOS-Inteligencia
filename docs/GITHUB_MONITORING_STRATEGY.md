# GitHub Monitoring Strategy — Gem Hunter & Repo Tracking

> **Version:** 1.0 | **Updated:** 2026-03-04

## Overview

Three methods available for monitoring GitHub repos and running Gem Hunter:

| Method | Best For | Cost | Setup |
|--------|----------|------|-------|
| **GitHub MCP** (Windsurf) | Interactive sessions, ad-hoc searches | Free (with PAT) | Already configured |
| **GitHub Actions Cron** | Automated weekly Gem Hunter runs | Free (public repos) | Needs workflow file |
| **PAT in VPS scripts** | Server-side automation | Free | PAT in `.env` |

## Recommended Approach

### 1. GitHub PAT (Personal Access Token)

**Required for all methods.** Generate at: https://github.com/settings/tokens

Scopes needed:
- `repo` (read access to public repos)
- `read:user` (read user profiles)

Store in:
- **Windsurf MCP:** `~/.codeium/windsurf/mcp_config.json` → `github.env.GITHUB_TOKEN`
- **VPS:** `/opt/bracc/infra/.env` → `GITHUB_TOKEN=ghp_...`
- **GitHub Actions:** Already has `GITHUB_TOKEN` automatically

### 2. Interactive: GitHub MCP Tools

Use during Windsurf sessions for:
- `mcp5_search_repositories` — Find new civic tech repos
- `mcp5_list_commits` — Track upstream (World-Open-Graph/br-acc) activity
- `mcp5_list_issues` / `mcp5_list_pull_requests` — Monitor community PRs
- `mcp5_get_file_contents` — Read specific files from other repos

### 3. Automated: GitHub Actions Cron (Recommended for Gem Hunter)

Create `.github/workflows/gem-hunter.yml`:

```yaml
name: Gem Hunter Weekly
on:
  schedule:
    - cron: '0 10 * * 1'  # Every Monday 10AM UTC
  workflow_dispatch:

jobs:
  hunt:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install httpx openai
      - run: python agents/gem_hunter/gem_hunter.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
      - uses: actions/upload-artifact@v4
        with:
          name: gem-report
          path: agents/gem_hunter/gem_report.json
```

### 4. VPS-based: Cron Script (Fallback)

For running Gem Hunter on VPS directly:

```bash
# Add to VPS crontab:
0 10 * * 1 /opt/bracc/scripts/run-gem-hunter.sh >> /opt/bracc/logs/gem-hunter.log 2>&1
```

## Repos to Monitor

| Repo | Purpose | Method |
|------|---------|--------|
| `World-Open-Graph/br-acc` | Upstream fork | GitHub Actions + MCP |
| `nferdica/brazil-visible` | Inspiration (92 APIs) | Gem Hunter |
| `MatheusMarkies/Transparencia-360` | Competitor analysis | Gem Hunter |
| `okfn-brasil/querido-diario` | Gazette monitor | Gem Hunter |
| `augusto-herrmann/transparencia-dados-abertos-brasil` | Portal survey | Gem Hunter |

## Current Status

- **GitHub PAT:** ⚠️ EXPIRED — needs regeneration
- **GitHub MCP:** Configured but blocked by expired PAT
- **GitHub Actions:** Not yet set up (needs workflow file + OPENROUTER secret)
- **Gem Hunter tags:** 21 search queries in `agents/gem_hunter/gem_hunter_tags.json`
