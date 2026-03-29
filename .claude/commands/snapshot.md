# /snapshot — Criar Snapshot de Contexto

Cria um snapshot completo do contexto atual do projeto usando o Context Manager.

## Uso

```bash
bun scripts/context-manager.ts snapshot [trigger]
```

Onde `trigger` pode ser:
- `commit` — Após commit importante
- `deploy` — Após deploy
- `task_complete` — Ao concluir uma task
- `repo_change` — Ao mudar de repositório
- `manual` — Snapshot manual (padrão)

## Output

Cria dois arquivos em `docs/_context_snapshots/`:
- `snapshot_TIMESTAMP_TRIGGER.json` — Snapshot completo (JSON)
- `snapshot_TIMESTAMP_TRIGGER.md` — Resumo legível (Markdown)

## Exemplo

```bash
bun scripts/context-manager.ts snapshot commit
```

## Snapshot contém:

- Repo, branch, último commit
- Arquivos não comitados
- Tasks P0/P1/P2 atuais
- Últimos 10 commits
- Configuração LLM
- Contexto de trabalho atual
- Trigger e posição Fibonacci
