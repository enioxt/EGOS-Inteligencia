# PREFERENCES — Coding Standards for EGOS Inteligência

> **Version:** 1.0.0 | **Updated:** 2026-03-03

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12, FastAPI, uvicorn, httpx |
| Frontend | React 18, Vite, TypeScript, CSS Modules |
| Database | Neo4j 5.x (graph), Redis (cache) |
| AI | OpenRouter API (Gemini Flash / GPT-4o-mini) |
| ETL | Python, uv, systemd services |
| Deploy | Docker Compose on Contabo VPS |

## Python Code Style

### Size Limits
- **400 lines** max per module
- **300 lines** max per router file
- **200 lines** max per ETL pipeline script

### Linting & Formatting
```bash
uv run ruff check src/        # Lint
uv run ruff format src/        # Format
uv run pytest -x --tb=short   # Test
```

### Imports (order)
```python
# 1. stdlib → 2. third-party → 3. local
import os
from typing import Any
from fastapi import APIRouter
from src.bracc.services.cache import get_cached
```

### Commits: `type(scope): description`
`feat` | `fix` | `docs` | `refactor` | `chore`

## Neo4j Rules

```cypher
// ❌ Query without LIMIT
MATCH (n:Company) RETURN n

// ✅ Always LIMIT
MATCH (n:Company) WHERE n.name CONTAINS $name RETURN n LIMIT 100

// ❌ Unbounded traversal
MATCH path=(a)-[*]-(b) RETURN path

// ✅ Bounded traversal (max 3 hops)
MATCH path=(a)-[*1..3]-(b) RETURN path LIMIT 50
```

## API Route Rules

```python
# ❌ No error handling
@router.get("/search")
async def search(q: str):
    return neo4j.run(query)

# ✅ Proper pattern
@router.get("/search")
async def search(q: str, limit: int = 100):
    try:
        result = await neo4j.run(query, params={"q": q, "limit": limit})
        return {"data": result, "count": len(result)}
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(500, "Search failed")
```

## Frontend Rules (React/Vite)

- **TypeScript strict** — avoid `any` where possible
- **CSS Modules** — `Component.module.css`, not inline styles
- **Lucide icons** — `lucide-react` for all icons
- **No console.log** in production code (use console.debug)

## Security

1. **API Keys** — NEVER hardcode. Use `.env`
2. **CPF/PII** — Mask in all public output (***.***.***-XX)
3. **Neo4j queries** — ALWAYS have LIMIT clause
4. **JWT** — Secret in env var, never in code
5. **Prompt Injection** — Sanitize external text before LLM
6. **CORS** — Restrict to known origins in production

## Anti-Patterns

```python
# ❌ Hardcoded URLs
url = "https://api.portaldatransparencia.gov.br/..."

# ✅ Config-driven
url = settings.transparency_api_url

# ❌ Blocking calls in async context
import requests
resp = requests.get(url)

# ✅ Async HTTP
import httpx
async with httpx.AsyncClient() as client:
    resp = await client.get(url)

# ❌ Global mutable state
results = []  # module-level

# ✅ Function-scoped or dependency injection
async def search() -> list:
    results = []
```

## External API Claims

> **RULE:** When making claims about external APIs (Portal Transparência, PNCP, DataJud, etc.):
> 1. **ALWAYS** search via Exa MCP or web_search BEFORE asserting
> 2. **CITE** the source URL
> 3. **NEVER** assume endpoint stability — APIs change
> 4. **SAVE** discoveries via `create_memory`
