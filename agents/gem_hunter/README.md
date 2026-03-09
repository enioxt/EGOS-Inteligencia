# 💎 Gem Hunter v2

**Autonomous Collaboration Agent for EGOS Intelligence**

O Gem Hunter monitora passivamente o ecossistema Open-Source global (focado na API pública do GitHub) buscando por inovações e joias ("Gems") ligadas a Open Source Intelligence (OSINT), Justiça Cívica (Civic Tech) e Análise de Grafos (Neo4j). 

## ⚙️ Como funciona
1. **Scraping Direcionado**: O script procura diariamente por repositórios criados/atualizados que contenham termos estratégicos definidos em `gem_hunter_tags.json`.
2. **Avaliação Agêntica**: Utilizando o LLM (Llama 3 70B via OpenRouter), o agente lê o nome, descrição e o README do repositório para validar se o projeto é realmente útil ou tem sinergia.
3. **Outreach (Loop Rápido)**: Repositórios aprovados como "Gems" recebem automaticamente uma estrela (Star) da conta de máquina e são adicionados ao relatório diário `gem_report.json` para que um humano (ou outro agente do EGOS) crie uma Issue/Pull Request colaborativa ("Gem Hunter Outreach").

## 🚀 Como Rodar
`GITHUB_TOKEN="ghp_seu_token" OPENROUTER_API_KEY="<OPENROUTER_API_KEY_AQUI>" ./gem_hunter.py`

## 🧱 Configuração
Altere as palavras-chave no arquivo `gem_hunter_tags.json` para expandir ou contrair o raio de caçada.
