# /restore-context — Recuperar Contexto Anterior

Recupera e exibe o último snapshot de contexto salvo.

## Uso

```bash
bun scripts/context-manager.ts latest
```

Ou para listar todos os snapshots disponíveis:

```bash
bun scripts/context-manager.ts list
```

## Output

Exibe o último snapshot completo com:
- Estado do repositório
- Tasks ativas
- Commits recentes
- Configuração LLM

## Integração com /start

O comando `/start` agora verifica automaticamente se existe um snapshot recente e exibe um resumo do último contexto salvo.

## Limpeza

Para remover snapshots antigos (mantendo os últimos 50):

```bash
bun scripts/context-manager.ts cleanup
```
