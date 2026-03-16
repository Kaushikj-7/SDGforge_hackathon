"""
Tool registry: wraps all existing phases and MCP servers
as named async callables the orchestrator can invoke.
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from phases.phase4_misinformation_detection import detect_misinformation
from phases.phase5_trusted_source_retrieval import retrieve_trusted_sources
from real_medical_apis import ComprehensiveMedicalAPIs
from phases.phase6_fact_correction import correct_misinformation

from mcp.who_server import get_who_alerts, get_who_fact_sheet
from mcp.fda_server import search_drug_recalls, get_drug_label
from mcp.openfda_server import get_adverse_events

medical_api = ComprehensiveMedicalAPIs()


async def async_detect(claim: str):
    return await asyncio.to_thread(detect_misinformation, claim)


async def async_pubmed(query: str):
    # Using the real PubMed API instead of the mock phase 5 retrieval
    results = await asyncio.to_thread(medical_api.search_pubmed_comprehensive, query)
    # Convert results to string to fit in the LLM's context easily.
    if not results:
        return "No results found."
    return "\n\n".join(
        [
            f"Source: {r.get('source', 'Unknown')}, Title: {r.get('title', 'N/A')}, Snippet: {r.get('snippet', 'N/A')}, URL: {r.get('url', 'N/A')}"
            for r in results
        ]
    )


async def async_correct(claim_with_evidence: str):
    # Phase 6 usually takes claim, sources, analysis
    return await asyncio.to_thread(
        correct_misinformation, claim_with_evidence, [], None
    )


# Tool manifest — maps tool name to async function + description
TOOL_REGISTRY = {
    "phase4_detect": {
        "fn": async_detect,
        "description": "Run Groq Llama3-70B misinformation detection. Returns verdict + confidence.",
        "input_key": "claim",
    },
    "phase5_pubmed": {
        "fn": async_pubmed,
        "description": "Search PubMed for peer-reviewed evidence on the claim topic.",
        "input_key": "query",
    },
    "phase5_drugbank": {
        "fn": async_pubmed,
        "description": "Search DrugBank for drug interaction and safety data.",
        "input_key": "query",
    },
    "phase6_correct": {
        "fn": async_correct,
        "description": "Use Gemini 1.5-Flash to generate a cited correction with sources.",
        "input_key": "claim_with_evidence",
    },
    "who_alerts": {
        "fn": get_who_alerts,
        "description": "Search WHO outbreak news and alerts for disease-related claims.",
        "input_key": "topic",
    },
    "who_fact_sheet": {
        "fn": get_who_fact_sheet,
        "description": "Fetch WHO official fact sheet for a health topic.",
        "input_key": "topic",
    },
    "fda_drug_label": {
        "fn": get_drug_label,
        "description": "Fetch FDA official drug label — indications, warnings, interactions.",
        "input_key": "drug_name",
    },
    "fda_recalls": {
        "fn": search_drug_recalls,
        "description": "Search FDA recall database for a specific drug.",
        "input_key": "drug_name",
    },
    "openfda_adverse": {
        "fn": get_adverse_events,
        "description": "Fetch real-world adverse event reports from FDA FAERS.",
        "input_key": "drug_name",
    },
}


async def call_tool(tool_name: str, input_value: str) -> dict:
    """
    Invoke a tool by name with a string input.
    Returns tool output as a dict.
    Catches exceptions so one failing tool does not abort the loop.
    """
    if tool_name not in TOOL_REGISTRY:
        return {"error": f"Unknown tool: {tool_name}"}
    tool = TOOL_REGISTRY[tool_name]
    try:
        result = await tool["fn"](**{tool["input_key"]: input_value})
        return {"tool": tool_name, "result": result}
    except Exception as e:
        return {"tool": tool_name, "error": str(e)}
