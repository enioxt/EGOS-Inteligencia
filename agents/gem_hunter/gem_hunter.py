#!/usr/bin/env python3
import os
import json
import time
import base64
import requests
from typing import List, Dict, Any
from datetime import datetime, timedelta

# Configurations
TAGS_FILE = os.path.join(os.path.dirname(__file__), 'gem_hunter_tags.json')
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

def load_config() -> dict:
    if not os.path.exists(TAGS_FILE):
        return {"tags": ["osint"], "queries": ["dados abertos"]}
    with open(TAGS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def search_github(query: str, days_ago: int = 30) -> List[Dict[str, Any]]:
    """Search Github repositories that were updated recently matching the query."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "EGOS-Gem-Hunter"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    date_filter = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
    q = f'"{query}" pushed:>{date_filter}'
    url = f"https://api.github.com/search/repositories?q={q}&sort=updated&order=desc"
    
    print(f"🔍 Searching GitHub API with query: {q}")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 403:
        print("⚠️ GitHub API Rate Limit exceeded.")
        return []
    elif response.status_code != 200:
        print(f"⚠️ GitHub API Error {response.status_code}: {response.text}")
        return []

    data = response.json()
    return data.get('items', [])[:5]  # Limit to top 5 per query to save tokens

def get_readme(repo_full_name: str) -> str:
    """Fetch the README content of a repository."""
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "EGOS-Gem-Hunter"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    url = f"https://api.github.com/repos/{repo_full_name}/readme"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        content = data.get('content', '')
        if content:
            try:
                return base64.b64decode(content).decode('utf-8')
            except Exception as e:
                print(f"Error decoding README for {repo_full_name}: {e}")
    return ""

def evaluate_with_llm(repo: Dict[str, Any], readme_content: str) -> dict:
    """Use OpenRouter (or OpenAI compatible API) to evaluate if the repo is a Gem."""
    if not OPENROUTER_API_KEY:
        print("⚠️ OPENROUTER_API_KEY not set. Skipping AI Evaluation.")
        return {"is_gem": True, "reason": "No LLM API Key to judge, assuming it's a gem.", "action": "Manual review"}

    prompt = f"""
You are the EGOS Gem Hunter. You look for open-source repositories that can help a Civic Intelligence & OSINT platform in Brazil.
Evaluate this repository based on its name, description, and README.

Name: {repo.get('full_name')}
Description: {repo.get('description')}
Stars: {repo.get('stargazers_count')}

README snippet:
{readme_content[:1500]}

Is this a strategic "Gem" we should collaborate with, fork, or study? Respond with a JSON object ONLY containing:
{{
  "is_gem": true/false,
  "reason": "Short explanation",
  "action": "Star and review / Fork / Ignore"
}}
"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/llama-3.3-70b-instruct",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            result_text = response.json()['choices'][0]['message']['content']
            return json.loads(result_text)
        else:
            print(f"LLM Error: {response.text}")
            return {"is_gem": False, "reason": "API Error", "action": "Ignore"}
    except Exception as e:
        print(f"Evaluation exception: {e}")
        return {"is_gem": False, "reason": str(e), "action": "Ignore"}

def star_repository(repo_full_name: str):
    """Star the repository using the GitHub API."""
    if not GITHUB_TOKEN:
        print(f"⚠️ Cannot star '{repo_full_name}' - No GITHUB_TOKEN provided.")
        return

    url = f"https://api.github.com/user/starred/{repo_full_name}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {GITHUB_TOKEN}",
        "User-Agent": "EGOS-Gem-Hunter"
    }
    response = requests.put(url, headers=headers)
    if response.status_code == 204:
        print(f"⭐ Successfully starred {repo_full_name}!")
    else:
        print(f"⚠️ Failed to star {repo_full_name}: {response.status_code}")

def run_hunter():
    print("🚀 Starting Gem Hunter v2...")
    config = load_config()
    queries = config.get("queries", [])
    gems_found = []

    for query in queries:
        repos = search_github(query)
        for repo in repos:
            full_name = repo['full_name']
            print(f"\nEvaluating found repo: {full_name}")
            
            readme = get_readme(full_name)
            evaluation = evaluate_with_llm(repo, readme)
            
            if evaluation.get("is_gem"):
                print(f"💎 GEM FOUND: {full_name}")
                print(f"Reason: {evaluation.get('reason')}")
                
                # Action: Star the repository
                star_repository(full_name)
                
                gems_found.append({
                    "repo": full_name,
                    "url": repo['html_url'],
                    "reason": evaluation.get("reason")
                })
        
        time.sleep(2) # Be polite to GitHub API

    if gems_found:
        print("\n🏆 Gem Hunter Report:")
        for gem in gems_found:
            print(f" - {gem['repo']}: {gem['reason']}")
        
        report_path = os.path.join(os.path.dirname(__file__), 'gem_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(gems_found, f, indent=2, ensure_ascii=False)
        print(f"Report saved to {report_path}")
    else:
        print("\n💨 No new gems found today.")

if __name__ == "__main__":
    run_hunter()
