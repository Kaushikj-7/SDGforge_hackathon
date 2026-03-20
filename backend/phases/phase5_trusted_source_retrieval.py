#!/usr/bin/env python3
"""
Phase 5: Trusted Source Retrieval
Upgraded to Autonomous Agent Tool Calling
The LLM dictates when and how to search APIs.
"""

import json
import requests
import os

try:
    from config import GEMINI_API_KEY
except ImportError:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")


# ---------------------------------------------------------
# Local Tools (Simulating what an MCP Server provides)
# ---------------------------------------------------------
def fetch_via_api(databaseing, query):
    """
    Tool A: Connects to PubMed or FDA (Simulated for Hackathon/demo, or connects to real_medical_apis)
    """
    print(f"   [Tool Executing] Fetching {databaseing} for '{query}'...")
    # In a full build, this would route to real_medical_apis.py
    # Here we simulate the return from those databases to save time/bandwidth

    if databaseing.lower() == "fda":
        return f"FDA Warning: {query} may have interactions. Not recommended for off-label use."
    elif databaseing.lower() == "pubmed":
        return f"PubMed Study ID 12345: Efficacy of {query} remains unsupported in clinical trials."
    else:
        return f"Database {databaseing} returned no results."


def read_webpage_direct(url):
    """
    Tool B: Fetches raw HTML and returns markdown for the LLM
    """
    print(f"   [Tool Executing] Reading webpage natively: {url}...")
    try:
        resp = requests.get(url, timeout=10)
        return resp.text[:1000]  # Simulated strip
    except:
        return "Failed to fetch webpage."


# ---------------------------------------------------------
# The Agentic execution loop
# ---------------------------------------------------------
def retrieve_trusted_sources(query, max_results=3, force_test=False):
    """
    Main autonomous loop. The LLM dictates the steps.
    """
    print(f"🔬 Phase 5: Agentic Tool Retrieval for query: '{query}'")

    if not force_test and (
        not GEMINI_API_KEY or GEMINI_API_KEY == "your_gemini_api_key_here"
    ):
        print("⚠️ Gemini API not found. Returning mocked generic sources.")
        return mock_fallback_sources()

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}

    prompt = f"""
You are an autonomous Medical Research Agent.
You need to find evidence for: "{query}".

You have two tools available:
1) fetch_via_api(databaseing, query) - databaseing must be "fda" or "pubmed".
2) read_webpage_direct(url) - read a direct URL.

Return your exact action as a JSON. Once you have enough context, return the final array of sources.

Return format:
{{
  "action": "tool_call" | "finalize",
  "tool": "fetch_via_api" | "read_webpage_direct" | null,
  "parameters": {{"databaseing": "fda", "query": "..."}},
  "final_sources": [
      {{"source": "FDA", "title": "Drug warning", "url": "https://fda.gov", "snippet": "..."}}
  ]
}}
    """

    # We will simulate a one-shot tool execution for the pipeline
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1},
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        if resp.status_code == 200:
            content = resp.json()["candidates"][0]["content"]["parts"][0]["text"]

            # Extract JSON block
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            json_str = content[json_start:json_end]

            data = json.loads(json_str)

            if data.get("action") == "tool_call":
                tool = data.get("tool")
                params = data.get("parameters", {})

                # Execute tool
                if tool == "fetch_via_api":
                    context = fetch_via_api(
                        params.get("databaseing", "pubmed"), params.get("query", query)
                    )
                elif tool == "read_webpage_direct":
                    context = read_webpage_direct(
                        params.get("url", "http://example.com")
                    )

                # In a full Agent framework (like LangChain), we loop this back to the LLM.
                # For this streamlined pipeline, we auto-synthesize the final dictionary based on the tool result.
                return [
                    {
                        "source": params.get("databaseing", "medical_database").upper(),
                        "title": f"Agentic search for {query}",
                        "url": "https://pubmed.ncbi.nlm.nih.gov/"
                        if params.get("databaseing") == "pubmed"
                        else "https://fda.gov",
                        "snippet": context,
                    }
                ]

            elif data.get("action") == "finalize":
                return data.get("final_sources", [])

        return mock_fallback_sources()

    except Exception as e:
        print(f"Agent Retrieval Error: {e}")
        return mock_fallback_sources()


def mock_fallback_sources():
    return [
        {
            "source": "WHO",
            "title": "Standard Medical Guidelines",
            "url": "https://www.who.int/",
            "snippet": "It is critical to verify health information with clinical professionals.",
        }
    ]


if __name__ == "__main__":
    sources = retrieve_trusted_sources("does ivermectin cure viruses")
    print(json.dumps(sources, indent=2))
