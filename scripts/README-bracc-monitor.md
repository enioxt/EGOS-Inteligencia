# BR-ACC Upstream Monitor (TASK-013)

Script que roda **2x ao dia** e monitora o upstream **World-Open-Graph/br-acc**: forks, PRs abertos, issues e sugestões de alinhamento do `TASKS.md` com PRs mergeados. Gera um relatório JSON e opcionalmente envia notificações para Discord e Telegram.

## O que o script faz

- **Forks:** Lista forks do upstream, marca os novos desde a última execução, compara cada fork com o upstream (diff de arquivos) e categoriza por área (tradução, ETL, frontend, API, infra, docs).
- **Pull Requests:** Lista PRs abertos no upstream, detecta possíveis duplicatas (mesmo conjunto de arquivos), categoriza por tipo e notifica quando há PR novo.
- **Issues:** Lista issues abertas no upstream e faz cross-reference com as issues do nosso repositório (`enioxt/EGOS-Inteligencia`) para sinalizar possível trabalho duplicado.
- **Roadmap:** Lê o `TASKS.md` do repositório, lista PRs mergeados no upstream desde a última execução e sugere vínculos TASK-XXX ↔ PR (apenas relatório; não altera o `TASKS.md` automaticamente).

## Requisitos

- **Node.js 18+**
- **Variável de ambiente:** `GITHUB_TOKEN` ou `GH_TOKEN` (obrigatória para a GitHub API).

## Uso local

```bash
cd scripts
npm ci
export GITHUB_TOKEN=ghp_...
npm run monitor
```

O relatório é escrito em `scripts/bracc-monitor-report.json`. O estado (forks/PRs já conhecidos) fica em `scripts/.bracc-monitor-state.json` para a próxima execução.

## Variáveis de ambiente

| Variável | Obrigatória | Descrição |
|----------|-------------|-----------|
| `GITHUB_TOKEN` ou `GH_TOKEN` | Sim | Token da GitHub API (scope `repo` para repositórios públicos basta o token padrão). |
| `REPORT_PATH` | Não | Caminho do relatório JSON (padrão: `scripts/bracc-monitor-report.json`). |
| `STATE_PATH` | Não | Caminho do arquivo de estado (padrão: `scripts/.bracc-monitor-state.json`). |
| `DISCORD_WEBHOOK_URL` | Não | URL do webhook do Discord para notificações. |
| `TELEGRAM_BOT_TOKEN` | Não | Token do bot do Telegram (usado com `TELEGRAM_CHAT_ID`). |
| `TELEGRAM_CHAT_ID` | Não | ID do chat/canal para onde enviar as mensagens. |

Ver também `.env.example` na raiz do repositório.

## Rodar no GitHub Actions

O workflow **BR-ACC Monitor** (`.github/workflows/bracc-monitor.yml`) está configurado para:

- **Agendamento:** 2x ao dia às **09:00 UTC** e **21:00 UTC** (06:00 e 18:00 em UTC-3).
- **Manual:** Aba **Actions** → workflow "BR-ACC Monitor" → "Run workflow".

O estado é persistido entre execuções via cache do Actions. O relatório é publicado como artefato (**bracc-monitor-report**) com retenção de 14 dias.

Para receber notificações no Discord/Telegram, configure os secrets do repositório:

- `DISCORD_WEBHOOK_URL`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

## Rodar no servidor (Contabo / cron)

Para rodar em um servidor com cron (por exemplo Contabo), use Node 18+ e carregue as variáveis de ambiente (por exemplo a partir de um `.env` em `/opt/bracc` ou no crontab):

```bash
# Exemplo crontab (06:00 e 18:00 UTC-3)
0 6,18 * * * cd /opt/bracc/scripts && . ../.env 2>/dev/null; npm run monitor >> /var/log/bracc-monitor.log 2>&1
```

Defina `STATE_PATH` para um caminho persistente (por exemplo `/opt/bracc/scripts/.bracc-monitor-state.json`) para que o script reconheça forks e PRs já vistos entre execuções.

## On-demand via bot

A issue original menciona execução sob demanda por comando do bot. O código do bot (Discord/Telegram) fica fora deste repositório. Para disparar o monitor por comando (ex.: `/monitor-bracc`), o bot pode chamar a API do GitHub para acionar o workflow:

- Endpoint: `POST /repos/{owner}/{repo}/actions/workflows/bracc-monitor.yml/dispatches`
- Token com permissão `actions: write`.

Não é necessária alteração no script; basta o bot usar o `workflow_dispatch` do Actions.

## Limitações

- **Primeira execução:** Sem estado anterior, todos os forks e PRs são considerados “já conhecidos”; não há notificação de “novo” na primeira vez.
- **TASKS.md:** Apenas gera sugestões de vínculo no relatório; não atualiza o `TASKS.md` automaticamente.
