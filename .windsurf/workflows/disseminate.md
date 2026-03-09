---
description: "Saves new knowledge and patterns to Memory MCP, documentation, and social channels."
---

# /disseminate — Knowledge Dissemination

> **Works in:** ANY EGOS repo
> **When to Use:** After implementing a feature, fixing a bug, making an architectural decision, or completing a milestone.

---

## 1. Identify New Knowledge

What was created or changed?

- **Infrastructure**: Docker, caching, ETL, deployment?
- **Feature**: New component, API endpoint, agent?
- **Architecture**: Design pattern, data flow, integration?
- **Bug fix**: Root cause, prevention mechanism?
- **Governance**: Security policy, workflow, meta-prompt?

## 2. Save to Cascade Memory

```
create_memory({
  Title: "Session — [description]",
  Content: "Detailed markdown with files, decisions, gotchas...",
  CorpusNames: ["enioxt/REPO_NAME"],
  Tags: ["relevant", "tags"],
  Action: "create"
})
```

## 3. Check Meta-Prompt Triggers

```
Read .guarani/prompts/triggers.json
- Did any trigger apply this session?
- Should a new trigger be added?
- Was a meta-prompt useful? Document the outcome.
```

## 4. Update Documentation

- `docs/knowledge/HARVEST.md` — Add patterns, gotchas, learnings
- `TASKS.md` — Mark completed, add discovered tasks
- `.guarani/` — If architecture decisions were made

## 5. Post on Social Channels (if milestone)

Use `/postar` workflow for unified posting:
- **Telegram** (@ethikin): Full markdown, up to 4096 chars
- **Discord**: Markdown, up to 2000 chars
- **X.com** (@anoineim): 280 chars max + link

## 6. Update Bot/AI System Prompts (if applicable)

If new data sources, tools, or capabilities were added, update relevant system prompts.

---

## Checklist

- [ ] Cascade Memory updated (create_memory)
- [ ] Meta-prompt triggers reviewed
- [ ] TASKS.md updated
- [ ] Documentation updated (HARVEST.md, .guarani/)
- [ ] Social channels posted (if milestone)
