from agents import function_tool
from ddgs import DDGS
from tools.shared import log

@function_tool
def internet_search(query: str):
    log(f"🌍 Buscando → {query}")
    results = []

    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=8):
            results.append({
                "title": r.get("title"),
                "url": r.get("href"),
                "snippet": r.get("body")
            })

    return results
