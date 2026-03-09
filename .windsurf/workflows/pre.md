---
description: "Pre-processa instruções vagas em prompts técnicos otimizados"
---

# /pre — Pre-Processor de Instruções

> **Works in:** ANY EGOS repo

## Quando Usar

- Instrução vaga ou curta (< 50 chars)
- Quer simular múltiplas perspectivas antes de executar
- Quer garantir que nada foi esquecido

## Passos

1. **Carregar Pre-Processor**

Read `.guarani/preprocessor.md` if it exists.

2. **Capturar Instrução Original**

Copie exatamente o que o usuário disse.

3. **Simular Perspectivas (3-4 personas)**

- Engenheiro Senior
- Especialista em Seguranca
- Usuario Final
- QA Engineer

4. **Check Meta-Prompt Triggers**

Read `.guarani/prompts/triggers.json` — does this instruction match any trigger?
If yes, load the corresponding meta-prompt before executing.

5. **Gerar Output Padronizado**

```text
### INSTRUCAO ORIGINAL:
>>> [citacao] <<<

### PERSPECTIVAS SIMULADAS:
[perspectivas]

### INSTRUCAO MELHORADA:
>>> [versao otimizada] <<<

### SUBTAREFAS:
1. [ ] ...

### CRITERIOS DE ACEITACAO:
- [ ] ...

---
**EXECUTAR?** [SIM / PERGUNTAR]
```

6. **Aguardar Aprovacao**

- Se usuario aprovar: executar
- Se tiver duvidas: esclarecer primeiro

7. **Executar Instrucao Melhorada**

- Usar Sequential Thinking se P0/P1
- Seguir subtarefas na ordem

## Atalho

Este workflow e ativado AUTOMATICAMENTE quando:
- Instrucao < 50 caracteres
- Contem palavras vagas ("rapidinho", "simples", "basico")
- P0/P1 mencionado
