# Health Misinformation Detection — Agentic Browser Extension
## Complete Build Instructions

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture Decisions](#2-architecture-decisions)
3. [Repository Structure](#3-repository-structure)
4. [Backend Upgrades](#4-backend-upgrades)
5. [MCP Servers](#5-mcp-servers)
6. [Agent Orchestrator](#6-agent-orchestrator)
7. [Browser Extension](#7-browser-extension)
8. [API Layer (FastAPI)](#8-api-layer-fastapi)
9. [Claim Deduplication & Cache](#9-claim-deduplication--cache)
10. [SDGforge Integration](#10-sdgforge-integration)
11. [Environment & Config](#11-environment--config)
12. [Build Order & Milestones](#12-build-order--milestones)
13. [Testing Checklist](#13-testing-checklist)
14. [Known Gotchas](#14-known-gotchas)

---

## 1. Project Overview

### What you are building

An upgraded Chrome/Edge browser extension that lets users highlight any text on any medical website and instantly receive an AI-powered fact-check verdict — confidence score, risk level, correction, and cited sources — rendered in a floating Shadow DOM popup.

### What already exists (do not break)

| File | Role | Status |
|---|---|---|
| `simple_analyzer.py` | Main CLI pipeline | Keep, wrap in API |
| `config.py` | API keys | Keep, extend |
| `phase1_user_input.py` | Input normalization | Keep as tool |
| `phase4_misinformation_detection.py` | Groq Llama3-70B detection | Keep as tool |
| `phase5_trusted_source_retrieval.py` | PubMed + DrugBank search | Keep as tool |
| `phase6_fact_correction.py` | Gemini 1.5-Flash correction | Keep as tool |
| `real_medical_apis.py` | API wrappers | Keep, extend |
| `browser-extension/` | Existing extension skeleton | Refactor entirely |

### Core design rule

**The extension ships zero AI code.** All Groq, Gemini, PubMed, DrugBank, and MCP calls live on the Python backend. The extension is a thin client: it reads selected text, sends a POST request, and renders the JSON response. Extension bundle target: under 50kb.

---

## 2. Architecture Decisions

### Why Shadow DOM for the popup

Standard DOM injection (`document.createElement`, `innerHTML`) is blocked by Content Security Policy headers on health sites like WebMD, Healthline, Mayo Clinic, and NEJM. Shadow DOM (`element.attachShadow({ mode: 'open' })`) creates an isolated DOM tree that:
- Is exempt from host page CSP
- Cannot be styled or broken by host page CSS
- Does not mutate the host page structure
- Works on every site including those with strict CSP

### Why you never fetch the URL

Sites behind paywalls (NEJM, Lancet), login walls (hospital portals), or aggressive bot detection will block any server-side proxy fetch. You do not need to fetch the URL because the user already has the content rendered in their browser. The content script reads text directly from the live DOM — no network call required.

Your payload to the backend is:
```
selected_text      — the highlighted claim (50–500 chars)
surrounding_context — ±500 chars from the DOM around the selection
page_title         — document.title
page_url           — window.location.href (for source attribution only)
```

This is all text that is already present in the browser. No fetch. No CORS. No proxy.

### Why Server-Sent Events (SSE) for responses

LLM calls take 1–4 seconds. A frozen popup feels broken. SSE lets your backend stream status updates token-by-token to the extension:

```
data: {"status": "detecting", "message": "Analyzing claim type..."}
data: {"status": "searching", "message": "Searching PubMed (3 results found)..."}
data: {"status": "correcting", "message": "Generating correction with sources..."}
data: {"status": "done", "verdict": {...}}
```

The popup shows live progress. Perceived latency drops from 3s to under 300ms to first meaningful paint.

### Why ReAct agent pattern instead of linear pipeline

Your current pipeline always runs phases 1→4→5→6 in order regardless of claim type. A drug interaction query needs DrugBank first and doesn't need Gemini correction if the interaction is clear-cut. A simple health myth needs Groq detection + one PubMed query. The ReAct loop lets the orchestrator call only the tools it needs and retry with more evidence if confidence is below threshold.

---

## 3. Repository Structure

Reorganize your repo to this structure:

```
SDGforge_hackathon/
│
├── backend/
│   ├── main.py                        # FastAPI app entry point
│   ├── config.py                      # All API keys (move existing)
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── orchestrator.py            # ReAct agent loop (NEW)
│   │   ├── tools.py                   # Wraps existing phases as tools (NEW)
│   │   └── claim_classifier.py        # Drug vs health claim vs myth (NEW)
│   ├── phases/
│   │   ├── phase1_user_input.py       # Move existing file here
│   │   ├── phase4_misinformation_detection.py
│   │   ├── phase5_trusted_source_retrieval.py
│   │   └── phase6_fact_correction.py
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── who_server.py              # WHO API MCP tool (NEW)
│   │   ├── fda_server.py              # FDA recall MCP tool (NEW)
│   │   └── openfda_server.py          # OpenFDA adverse events (NEW)
│   ├── cache/
│   │   ├── __init__.py
│   │   └── claim_cache.py             # SHA256 + SQLite dedup cache (NEW)
│   ├── real_medical_apis.py           # Move existing file here
│   └── sdgforge_hook.py               # SDGforge impact logging (NEW)
│
├── extension/
│   ├── manifest.json                  # Manifest V3
│   ├── content.js                     # Selection listener + Shadow DOM popup
│   ├── service-worker.js              # Cache + HTTP client
│   ├── popup.html                     # Extension toolbar popup (dashboard)
│   ├── popup.js                       # Dashboard logic
│   └── icons/
│       ├── icon16.png
│       ├── icon48.png
│       └── icon128.png
│
├── simple_analyzer.py                 # Keep existing CLI (unchanged)
├── requirements.txt                   # Updated dependencies
└── README.md
```

---

## 4. Backend Upgrades

### 4.1 Install new dependencies

Add to `requirements.txt`:

```
fastapi==0.111.0
uvicorn==0.29.0
sse-starlette==2.1.0
python-dotenv==1.0.1
aiohttp==3.9.5
sqlite3                  # stdlib, no install needed
hashlib                  # stdlib
groq==0.9.0              # already have
google-generativeai==0.7.2  # already have
httpx==0.27.0
pydantic==2.7.1
```

Install:
```bash
pip install -r requirements.txt
```

### 4.2 Update `config.py`

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Existing keys
GROQ_API_KEY    = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY")

# New keys
WHO_API_BASE    = "https://www.who.int/api"          # public, no key needed
FDA_API_BASE    = "https://api.fda.gov"              # public, no key needed
OPENFDA_KEY     = os.getenv("OPENFDA_KEY", "")       # optional, higher rate limit
SDGFORGE_API    = os.getenv("SDGFORGE_API_URL", "http://localhost:8001")
SDGFORGE_TOKEN  = os.getenv("SDGFORGE_TOKEN", "")

# Cache settings
CACHE_DB_PATH   = os.getenv("CACHE_DB_PATH", "./cache/claims.db")
CACHE_TTL_HOURS = 24

# Agent settings
CONFIDENCE_THRESHOLD = 0.85   # loop until this is reached
MAX_AGENT_ITERATIONS = 4      # hard stop to prevent infinite loops

# CORS origins (your extension ID goes here after publishing)
ALLOWED_ORIGINS = [
    "chrome-extension://*",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
]
```

---

## 5. MCP Servers

MCP (Model Context Protocol) servers are lightweight Python modules that expose a specific data source as a callable tool the agent can invoke. Each one is a thin HTTP wrapper — not a separate running process.

### 5.1 `backend/mcp/who_server.py`

```python
"""
MCP Tool: WHO health alerts and disease outbreak feed.
Called by the agent when a claim involves infectious disease,
vaccination, or global health emergency topics.
"""
import aiohttp
from typing import Optional

WHO_DISEASE_FEED = "https://www.who.int/api/news/diseaseoutbreaknews"

async def get_who_alerts(topic: str, limit: int = 3) -> dict:
    """
    Search WHO outbreak news for claims related to a disease or health topic.
    Returns list of relevant alerts with title, date, and URL.
    """
    try:
        async with aiohttp.ClientSession() as session:
            params = {"sf_culture": "en", "$top": 20}
            async with session.get(WHO_DISEASE_FEED, params=params, timeout=5) as r:
                if r.status != 200:
                    return {"source": "WHO", "results": [], "error": f"HTTP {r.status}"}
                data = await r.json()
                items = data.get("value", [])
                # Filter by topic keyword
                filtered = [
                    {
                        "title": item.get("Title", ""),
                        "date":  item.get("PublicationDateAndTime", ""),
                        "url":   f"https://www.who.int{item.get('Url', '')}",
                        "summary": item.get("Summary", "")[:300]
                    }
                    for item in items
                    if topic.lower() in (item.get("Title", "") + item.get("Summary", "")).lower()
                ]
                return {"source": "WHO", "results": filtered[:limit]}
    except Exception as e:
        return {"source": "WHO", "results": [], "error": str(e)}


async def get_who_fact_sheet(topic: str) -> dict:
    """
    Fetch WHO fact sheet for common health topics (vaccines, diseases, nutrition).
    Uses WHO's public fact sheets API endpoint.
    """
    try:
        url = f"https://www.who.int/api/hubs/cms/features?sf_culture=en&$filter=substringof('{topic}',Title)"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=5) as r:
                if r.status != 200:
                    return {"source": "WHO", "fact_sheet": None}
                data = await r.json()
                items = data.get("value", [])
                if items:
                    return {
                        "source": "WHO",
                        "fact_sheet": {
                            "title":   items[0].get("Title"),
                            "url":     f"https://www.who.int{items[0].get('Url','')}",
                            "snippet": items[0].get("Summary", "")[:400]
                        }
                    }
                return {"source": "WHO", "fact_sheet": None}
    except Exception as e:
        return {"source": "WHO", "fact_sheet": None, "error": str(e)}
```

### 5.2 `backend/mcp/fda_server.py`

```python
"""
MCP Tool: FDA drug recall and safety alert database.
Called by the agent when a claim involves a specific drug name,
supplement, or medical device.
"""
import aiohttp
from backend.config import FDA_API_BASE

async def search_drug_recalls(drug_name: str, limit: int = 3) -> dict:
    """
    Search FDA recall database for a specific drug.
    Returns recent recalls with reason, date, and classification.
    """
    try:
        url = f"{FDA_API_BASE}/drug/enforcement.json"
        params = {
            "search": f"product_description:{drug_name}",
            "limit":  limit
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=5) as r:
                if r.status == 404:
                    return {"source": "FDA", "recalls": []}
                data = await r.json()
                results = data.get("results", [])
                return {
                    "source": "FDA",
                    "recalls": [
                        {
                            "drug":           r.get("product_description", "")[:100],
                            "reason":         r.get("reason_for_recall", ""),
                            "classification": r.get("classification", ""),
                            "date":           r.get("recall_initiation_date", ""),
                            "status":         r.get("status", "")
                        }
                        for r in results
                    ]
                }
    except Exception as e:
        return {"source": "FDA", "recalls": [], "error": str(e)}


async def get_drug_label(drug_name: str) -> dict:
    """
    Fetch official FDA drug label — indications, warnings, contraindications.
    This is the ground truth for drug claims.
    """
    try:
        url = f"{FDA_API_BASE}/drug/label.json"
        params = {"search": f"openfda.brand_name:{drug_name}", "limit": 1}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=5) as r:
                if r.status == 404:
                    return {"source": "FDA", "label": None}
                data = await r.json()
                results = data.get("results", [])
                if not results:
                    return {"source": "FDA", "label": None}
                label = results[0]
                return {
                    "source": "FDA",
                    "label": {
                        "indications":       " ".join(label.get("indications_and_usage", []))[:500],
                        "warnings":          " ".join(label.get("warnings", []))[:500],
                        "contraindications": " ".join(label.get("contraindications", []))[:500],
                        "drug_interactions": " ".join(label.get("drug_interactions", []))[:500],
                    }
                }
    except Exception as e:
        return {"source": "FDA", "label": None, "error": str(e)}
```

### 5.3 `backend/mcp/openfda_server.py`

```python
"""
MCP Tool: OpenFDA adverse event reports (FAERS database).
Called when the agent needs real-world drug safety evidence
beyond the official label.
"""
import aiohttp
from backend.config import FDA_API_BASE, OPENFDA_KEY

async def get_adverse_events(drug_name: str, limit: int = 5) -> dict:
    """
    Search FDA Adverse Event Reporting System for a drug.
    Returns top reported adverse events with counts.
    """
    try:
        url = f"{FDA_API_BASE}/drug/event.json"
        params = {
            "search": f"patient.drug.medicinalproduct:{drug_name}",
            "count":  "patient.reaction.reactionmeddrapt.exact",
            "limit":  limit
        }
        if OPENFDA_KEY:
            params["api_key"] = OPENFDA_KEY
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=5) as r:
                if r.status == 404:
                    return {"source": "OpenFDA", "adverse_events": []}
                data = await r.json()
                results = data.get("results", [])
                return {
                    "source": "OpenFDA",
                    "adverse_events": [
                        {"reaction": item.get("term"), "count": item.get("count")}
                        for item in results
                    ]
                }
    except Exception as e:
        return {"source": "OpenFDA", "adverse_events": [], "error": str(e)}
```

---

## 6. Agent Orchestrator

### 6.1 `backend/agent/claim_classifier.py`

```python
"""
Lightweight claim classifier — runs before the agent loop
to decide the optimal tool sequence.
No LLM call needed here: pure keyword + regex heuristics.
Fast: ~1ms, no network.
"""
import re

DRUG_KEYWORDS = [
    "mg", "dosage", "dose", "tablet", "capsule", "injection",
    "interaction", "prescription", "overdose", "side effect",
    "contraindication", "warfarin", "aspirin", "ibuprofen",
    "metformin", "statin", "antibiotic", "paracetamol", "acetaminophen"
]

DISEASE_KEYWORDS = [
    "cancer", "diabetes", "covid", "hiv", "aids", "malaria",
    "tuberculosis", "alzheimer", "stroke", "heart attack",
    "hypertension", "depression", "autism", "vaccine", "immunity"
]

MYTH_PATTERNS = [
    r"cures?\s+\w+",
    r"prevents?\s+\w+",
    r"causes?\s+\w+",
    r"always\s+(safe|healthy|harmful|dangerous)",
    r"never\s+(causes?|leads? to)",
    r"100%\s+(effective|safe|proven)",
    r"doctors\s+(don't want|hate)",
    r"natural\s+\w+\s+(is|are)\s+(better|safer|healthier)"
]

def classify_claim(text: str) -> dict:
    """
    Returns:
        claim_type: "drug_interaction" | "disease_claim" | "health_myth" | "general"
        priority_tools: list of tool names in recommended call order
        drug_names: list of detected drug names (if any)
    """
    text_lower = text.lower()

    is_drug   = any(kw in text_lower for kw in DRUG_KEYWORDS)
    is_disease = any(kw in text_lower for kw in DISEASE_KEYWORDS)
    is_myth   = any(re.search(p, text_lower) for p in MYTH_PATTERNS)

    if is_drug:
        return {
            "claim_type":    "drug_interaction",
            "priority_tools": ["fda_drug_label", "phase5_drugbank", "phase4_detect", "phase6_correct"],
            "drug_names":    _extract_drug_names(text)
        }
    elif is_myth:
        return {
            "claim_type":    "health_myth",
            "priority_tools": ["phase4_detect", "phase5_pubmed", "who_fact_sheet", "phase6_correct"],
            "drug_names":    []
        }
    elif is_disease:
        return {
            "claim_type":    "disease_claim",
            "priority_tools": ["phase4_detect", "who_alerts", "phase5_pubmed", "phase6_correct"],
            "drug_names":    []
        }
    else:
        return {
            "claim_type":    "general",
            "priority_tools": ["phase4_detect", "phase5_pubmed", "phase6_correct"],
            "drug_names":    []
        }

def _extract_drug_names(text: str) -> list:
    """
    Simple capitalized noun extraction for drug name detection.
    Production version should use a medical NER model.
    """
    words = text.split()
    return [w.strip(".,;()") for w in words if w[0].isupper() and len(w) > 3]
```

### 6.2 `backend/agent/tools.py`

```python
"""
Tool registry: wraps all existing phases and MCP servers
as named async callables the orchestrator can invoke.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from phases.phase4_misinformation_detection import detect_misinformation
from phases.phase5_trusted_source_retrieval import search_pubmed, search_drugbank
from phases.phase6_fact_correction import generate_correction
from mcp.who_server import get_who_alerts, get_who_fact_sheet
from mcp.fda_server import search_drug_recalls, get_drug_label
from mcp.openfda_server import get_adverse_events

# Tool manifest — maps tool name to async function + description
TOOL_REGISTRY = {
    "phase4_detect": {
        "fn":          detect_misinformation,
        "description": "Run Groq Llama3-70B misinformation detection. Returns verdict + confidence.",
        "input_key":   "claim"
    },
    "phase5_pubmed": {
        "fn":          search_pubmed,
        "description": "Search PubMed for peer-reviewed evidence on the claim topic.",
        "input_key":   "query"
    },
    "phase5_drugbank": {
        "fn":          search_drugbank,
        "description": "Search DrugBank for drug interaction and safety data.",
        "input_key":   "drug_name"
    },
    "phase6_correct": {
        "fn":          generate_correction,
        "description": "Use Gemini 1.5-Flash to generate a cited correction with sources.",
        "input_key":   "claim_with_evidence"
    },
    "who_alerts": {
        "fn":          get_who_alerts,
        "description": "Search WHO outbreak news and alerts for disease-related claims.",
        "input_key":   "topic"
    },
    "who_fact_sheet": {
        "fn":          get_who_fact_sheet,
        "description": "Fetch WHO official fact sheet for a health topic.",
        "input_key":   "topic"
    },
    "fda_drug_label": {
        "fn":          get_drug_label,
        "description": "Fetch FDA official drug label — indications, warnings, interactions.",
        "input_key":   "drug_name"
    },
    "fda_recalls": {
        "fn":          search_drug_recalls,
        "description": "Search FDA recall database for a specific drug.",
        "input_key":   "drug_name"
    },
    "openfda_adverse": {
        "fn":          get_adverse_events,
        "description": "Fetch real-world adverse event reports from FDA FAERS.",
        "input_key":   "drug_name"
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
```

### 6.3 `backend/agent/orchestrator.py`

This is the core of the agentic upgrade. It wraps your existing phases in a ReAct reasoning loop.

```python
"""
ReAct Agent Orchestrator.
Reason → Act → Observe loop over the tool registry.
Stops when confidence >= CONFIDENCE_THRESHOLD or MAX_AGENT_ITERATIONS reached.
"""
import json
import asyncio
from typing import AsyncGenerator
from groq import AsyncGroq
from backend.config import GROQ_API_KEY, CONFIDENCE_THRESHOLD, MAX_AGENT_ITERATIONS
from backend.agent.claim_classifier import classify_claim
from backend.agent.tools import call_tool, TOOL_REGISTRY

groq_client = AsyncGroq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are a medical fact-checking agent with access to trusted medical tools.

Your job: verify health claims and return a structured verdict.

Available tools:
{tool_descriptions}

Rules:
1. Call tools in the order that makes most sense for this claim type.
2. After each tool call, evaluate if you have enough evidence.
3. If confidence >= 0.85 after a tool call, stop and generate the final verdict.
4. Always call phase6_correct last to generate the cited correction.
5. Never make up sources. Only use what tools return.
6. Return responses as valid JSON only — no prose, no markdown.

For each reasoning step, respond ONLY with this JSON format:
{{
  "thought": "your reasoning about what to do next",
  "action": "tool_name or FINISH",
  "action_input": "input string for the tool",
  "confidence_so_far": 0.0
}}

When action is FINISH, respond with:
{{
  "thought": "sufficient evidence gathered",
  "action": "FINISH",
  "verdict": "TRUE|FALSE|MISLEADING|UNCERTAIN",
  "risk_level": "CRITICAL|HIGH|MEDIUM|LOW",
  "confidence": 0.92,
  "correction": "The accurate medical information...",
  "explanation": "Why the claim is wrong/right...",
  "sources": [
    {{"name": "PubMed", "url": "https://...", "snippet": "..."}}
  ]
}}
"""

def _build_tool_descriptions() -> str:
    return "\n".join(
        f"- {name}: {info['description']}"
        for name, info in TOOL_REGISTRY.items()
    )

async def run_agent(
    selected_text: str,
    surrounding_context: str,
    page_title: str,
    page_url: str
) -> AsyncGenerator[dict, None]:
    """
    Main agent entry point. Yields status dicts for SSE streaming.
    Final yield contains the complete verdict.
    """
    # Step 1: classify claim to get optimal tool order
    classification = classify_claim(selected_text)
    yield {
        "status": "classifying",
        "message": f"Detected: {classification['claim_type'].replace('_', ' ')}",
        "claim_type": classification["claim_type"]
    }

    # Step 2: check dedup cache
    from backend.cache.claim_cache import get_cached_verdict, cache_verdict
    cached = await get_cached_verdict(selected_text)
    if cached:
        yield {"status": "cache_hit", "message": "Returning verified result from cache"}
        yield {"status": "done", "verdict": cached, "from_cache": True}
        return

    # Step 3: build initial agent prompt
    user_message = f"""
Claim to verify: "{selected_text}"

Surrounding context from the webpage:
{surrounding_context[:500]}

Page: {page_title}
URL: {page_url}

Claim type detected: {classification['claim_type']}
Recommended tool order: {', '.join(classification['priority_tools'])}

Start verifying. Use the recommended tool order unless your reasoning says otherwise.
"""

    messages = [
        {"role": "system",  "content": SYSTEM_PROMPT.format(tool_descriptions=_build_tool_descriptions())},
        {"role": "user",    "content": user_message}
    ]

    tool_results = []
    iteration = 0

    # Step 4: ReAct loop
    while iteration < MAX_AGENT_ITERATIONS:
        iteration += 1

        # Reason step: ask Groq what to do next
        try:
            response = await groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=messages,
                temperature=0.1,
                max_tokens=1024,
                response_format={"type": "json_object"}
            )
            raw = response.choices[0].message.content
            step = json.loads(raw)
        except Exception as e:
            yield {"status": "error", "message": f"Agent reasoning failed: {str(e)}"}
            return

        # Check if agent wants to finish
        if step.get("action") == "FINISH":
            verdict = {
                "verdict":     step.get("verdict", "UNCERTAIN"),
                "risk_level":  step.get("risk_level", "MEDIUM"),
                "confidence":  step.get("confidence", 0.5),
                "correction":  step.get("correction", ""),
                "explanation": step.get("explanation", ""),
                "sources":     step.get("sources", []),
                "claim_type":  classification["claim_type"],
                "iterations":  iteration
            }
            await cache_verdict(selected_text, verdict)
            yield {"status": "done", "verdict": verdict}
            return

        # Act step: call the chosen tool
        tool_name   = step.get("action", "")
        tool_input  = step.get("action_input", selected_text)
        confidence  = step.get("confidence_so_far", 0.0)

        yield {
            "status":  "acting",
            "message": f"Calling {tool_name.replace('_', ' ')}...",
            "tool":    tool_name,
            "confidence_so_far": confidence
        }

        tool_result = await call_tool(tool_name, tool_input)
        tool_results.append(tool_result)

        # Observe: append tool result to message history
        messages.append({"role": "assistant", "content": raw})
        messages.append({
            "role":    "user",
            "content": f"Tool result for {tool_name}:\n{json.dumps(tool_result, indent=2)}\n\nContinue. If confidence >= {CONFIDENCE_THRESHOLD}, call FINISH."
        })

        yield {
            "status":  "observing",
            "message": f"Processed {tool_name} result",
            "confidence_so_far": confidence
        }

        # Early stop if confidence threshold met
        if confidence >= CONFIDENCE_THRESHOLD:
            messages.append({
                "role":    "user",
                "content": f"Confidence {confidence} >= {CONFIDENCE_THRESHOLD}. Generate final verdict now. Action must be FINISH."
            })

    # Max iterations reached — force finish
    yield {"status": "max_iterations", "message": "Finalizing with available evidence..."}
    try:
        response = await groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages + [{"role": "user", "content": "You must FINISH now. Generate the best verdict you can from all gathered evidence."}],
            temperature=0.1,
            max_tokens=1024,
            response_format={"type": "json_object"}
        )
        step = json.loads(response.choices[0].message.content)
        verdict = {
            "verdict":     step.get("verdict", "UNCERTAIN"),
            "risk_level":  step.get("risk_level", "MEDIUM"),
            "confidence":  step.get("confidence", 0.5),
            "correction":  step.get("correction", "Insufficient evidence to fully verify."),
            "explanation": step.get("explanation", ""),
            "sources":     step.get("sources", []),
            "claim_type":  classification["claim_type"],
            "iterations":  iteration
        }
        await cache_verdict(selected_text, verdict)
        yield {"status": "done", "verdict": verdict}
    except Exception as e:
        yield {"status": "error", "message": str(e)}
```

---

## 7. Browser Extension

### 7.1 `extension/manifest.json`

```json
{
  "manifest_version": 3,
  "name": "Health Fact Checker",
  "version": "2.0.0",
  "description": "Highlight any medical claim for instant AI fact-checking",
  "permissions": [
    "storage",
    "activeTab"
  ],
  "host_permissions": [
    "http://localhost:8000/*",
    "https://your-backend-domain.com/*"
  ],
  "background": {
    "service_worker": "service-worker.js",
    "type": "module"
  },
  "content_scripts": [
    {
      "matches": ["<all_urls>"],
      "js": ["content.js"],
      "run_at": "document_idle"
    }
  ],
  "action": {
    "default_popup": "popup.html",
    "default_icon": {
      "16":  "icons/icon16.png",
      "48":  "icons/icon48.png",
      "128": "icons/icon128.png"
    }
  }
}
```

### 7.2 `extension/content.js`

This is the most important file. Read every comment carefully.

```javascript
/**
 * content.js — Health Fact Checker
 *
 * Responsibilities:
 *   1. Detect when user highlights text containing a health claim
 *   2. Show a micro-popup button anchored to the selection
 *   3. On click, expand the popup and stream the verdict from backend
 *
 * Critical constraints:
 *   - Zero DOM mutation on the host page (Shadow DOM only)
 *   - Works on sites with strict CSP (WebMD, Healthline, NEJM, etc.)
 *   - No external libraries — vanilla JS only
 *   - Bundle size: this file should stay under 15kb
 */

const BACKEND_URL = "http://localhost:8000";  // change to prod URL
const MIN_SELECTION_LENGTH = 15;
const HEALTH_TRIGGER_WORDS = [
  "cure", "treat", "prevent", "cancer", "diabetes", "vaccine", "drug",
  "vitamin", "supplement", "dose", "medication", "symptom", "disease",
  "infection", "antibody", "immune", "clinical", "study", "research",
  "mg", "proven", "natural", "toxic", "harmful", "safe", "effective"
];

// ─── Shadow DOM container ──────────────────────────────────────────────────

let hostEl = null;
let shadowRoot = null;
let currentPopup = null;

function ensureShadowHost() {
  if (hostEl) return;
  hostEl = document.createElement("div");
  hostEl.id = "hfc-host";
  // position: fixed so it floats above page content
  // pointer-events: none so it doesn't block page clicks by default
  hostEl.style.cssText = "position:fixed;top:0;left:0;width:0;height:0;z-index:2147483647;pointer-events:none;";
  document.body.appendChild(hostEl);
  shadowRoot = hostEl.attachShadow({ mode: "open" });

  // All styles live inside Shadow DOM — completely isolated from host page
  const style = document.createElement("style");
  style.textContent = `
    .hfc-btn {
      position: fixed;
      background: #1a73e8;
      color: #fff;
      border: none;
      border-radius: 6px;
      padding: 5px 10px;
      font-size: 12px;
      font-family: -apple-system, sans-serif;
      cursor: pointer;
      pointer-events: all;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
      white-space: nowrap;
      transition: background 0.15s;
      z-index: 1;
    }
    .hfc-btn:hover { background: #1557b0; }

    .hfc-card {
      position: fixed;
      background: #fff;
      border: 1px solid #e0e0e0;
      border-radius: 10px;
      padding: 14px 16px;
      font-family: -apple-system, sans-serif;
      font-size: 13px;
      color: #202124;
      min-width: 280px;
      max-width: 360px;
      pointer-events: all;
      z-index: 2;
    }
    @media (prefers-color-scheme: dark) {
      .hfc-card { background: #1e1e1e; border-color: #333; color: #e0e0e0; }
    }

    .hfc-status {
      color: #666;
      font-size: 12px;
      margin-bottom: 8px;
      min-height: 18px;
    }
    .hfc-verdict-badge {
      display: inline-block;
      padding: 3px 10px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
      margin-bottom: 8px;
    }
    .hfc-CRITICAL { background: #fce8e6; color: #c5221f; }
    .hfc-HIGH     { background: #fef3e2; color: #b45309; }
    .hfc-MEDIUM   { background: #fef9e7; color: #92400e; }
    .hfc-LOW      { background: #e6f4ea; color: #137333; }

    .hfc-confidence-bar {
      height: 4px;
      background: #e0e0e0;
      border-radius: 2px;
      margin: 6px 0;
      overflow: hidden;
    }
    .hfc-confidence-fill {
      height: 100%;
      border-radius: 2px;
      background: #1a73e8;
      transition: width 0.4s ease;
    }
    .hfc-correction {
      font-size: 12px;
      color: #333;
      line-height: 1.5;
      margin: 8px 0;
    }
    @media (prefers-color-scheme: dark) {
      .hfc-correction { color: #ccc; }
      .hfc-status { color: #888; }
    }
    .hfc-sources {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      margin-top: 8px;
    }
    .hfc-source-pill {
      background: #e8f0fe;
      color: #1a73e8;
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 10px;
      text-decoration: none;
      pointer-events: all;
    }
    .hfc-source-pill:hover { background: #d2e3fc; }
    .hfc-close {
      position: absolute;
      top: 8px;
      right: 10px;
      background: none;
      border: none;
      font-size: 16px;
      cursor: pointer;
      color: #666;
      pointer-events: all;
      line-height: 1;
    }
    .hfc-spinner {
      display: inline-block;
      width: 12px;
      height: 12px;
      border: 2px solid #e0e0e0;
      border-top-color: #1a73e8;
      border-radius: 50%;
      animation: hfc-spin 0.6s linear infinite;
      margin-right: 6px;
      vertical-align: middle;
    }
    @keyframes hfc-spin { to { transform: rotate(360deg); } }
  `;
  shadowRoot.appendChild(style);
}

// ─── Health claim detector ──────────────────────────────────────────────────

function isHealthRelated(text) {
  const lower = text.toLowerCase();
  return HEALTH_TRIGGER_WORDS.some(word => lower.includes(word));
}

function getSurroundingContext(selection) {
  /**
   * Extract ±500 chars of surrounding text from the DOM.
   * Uses the Range API — no fetch, no network, reads from live DOM.
   */
  try {
    const range = selection.getRangeAt(0);
    const container = range.commonAncestorContainer;
    const parent = container.nodeType === 3 ? container.parentElement : container;
    const fullText = parent.innerText || parent.textContent || "";
    const selectedText = selection.toString();
    const idx = fullText.indexOf(selectedText);
    if (idx === -1) return fullText.slice(0, 500);
    const start = Math.max(0, idx - 250);
    const end   = Math.min(fullText.length, idx + selectedText.length + 250);
    return fullText.slice(start, end);
  } catch {
    return "";
  }
}

// ─── Popup builder ─────────────────────────────────────────────────────────

function removeCurrentPopup() {
  if (currentPopup && shadowRoot.contains(currentPopup)) {
    shadowRoot.removeChild(currentPopup);
  }
  currentPopup = null;
}

function showMicroButton(x, y, onVerify) {
  ensureShadowHost();
  removeCurrentPopup();

  const btn = document.createElement("button");
  btn.className = "hfc-btn";
  btn.textContent = "✓ Verify claim";
  btn.style.left = `${Math.min(x, window.innerWidth - 160)}px`;
  btn.style.top  = `${y + 8}px`;

  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    onVerify();
  });

  hostEl.style.pointerEvents = "none"; // allow pass-through except on the button
  shadowRoot.appendChild(btn);
  currentPopup = btn;
}

function showLoadingCard(x, y, selectedText) {
  ensureShadowHost();
  removeCurrentPopup();

  const card = document.createElement("div");
  card.className = "hfc-card";
  card.style.left = `${Math.min(x, window.innerWidth - 380)}px`;
  card.style.top  = `${Math.min(y + 8, window.innerHeight - 300)}px`;

  card.innerHTML = `
    <button class="hfc-close">×</button>
    <div style="font-size:12px;color:#666;margin-bottom:8px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:280px;">
      "${selectedText.slice(0, 60)}${selectedText.length > 60 ? '...' : ''}"
    </div>
    <div class="hfc-status">
      <span class="hfc-spinner"></span>
      <span id="hfc-status-text">Analyzing claim...</span>
    </div>
    <div class="hfc-confidence-bar">
      <div class="hfc-confidence-fill" id="hfc-conf-fill" style="width:5%"></div>
    </div>
  `;

  card.querySelector(".hfc-close").addEventListener("click", removeCurrentPopup);
  shadowRoot.appendChild(card);
  currentPopup = card;
  return card;
}

function updateStatus(card, message, confidence) {
  const statusEl = card.querySelector("#hfc-status-text");
  const confFill = card.querySelector("#hfc-conf-fill");
  if (statusEl) statusEl.textContent = message;
  if (confFill && confidence) confFill.style.width = `${Math.round(confidence * 100)}%`;
}

function renderVerdict(card, verdict) {
  const riskColor = {
    CRITICAL: "#c5221f",
    HIGH:     "#b45309",
    MEDIUM:   "#92400e",
    LOW:      "#137333"
  };

  const sourcePills = (verdict.sources || [])
    .slice(0, 3)
    .map(s => `<a class="hfc-source-pill" href="${s.url}" target="_blank">${s.name}</a>`)
    .join("");

  card.innerHTML = `
    <button class="hfc-close">×</button>
    <div>
      <span class="hfc-verdict-badge hfc-${verdict.risk_level}">
        ${verdict.risk_level} — ${verdict.verdict}
      </span>
    </div>
    <div class="hfc-confidence-bar">
      <div class="hfc-confidence-fill" style="width:${Math.round((verdict.confidence || 0) * 100)}%"></div>
    </div>
    <div style="font-size:11px;color:#888;margin-bottom:6px;">
      Confidence: ${Math.round((verdict.confidence || 0) * 100)}%
    </div>
    <div class="hfc-correction">${verdict.correction || ""}</div>
    <div class="hfc-sources">${sourcePills}</div>
  `;
  card.querySelector(".hfc-close").addEventListener("click", removeCurrentPopup);
}

// ─── SSE stream handler ────────────────────────────────────────────────────

async function streamVerdict(payload, card, x, y) {
  /**
   * Connects to the backend SSE endpoint.
   * Updates the card UI as each status event arrives.
   * Renders final verdict when "done" event received.
   *
   * Uses fetch + ReadableStream — works in all MV3 service workers
   * and content scripts. No EventSource needed (doesn't support POST).
   */
  try {
    const response = await fetch(`${BACKEND_URL}/verify/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      updateStatus(card, `Server error: ${response.status}`, 0);
      return;
    }

    const reader  = response.body.getReader();
    const decoder = new TextDecoder();
    let   buffer  = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop(); // keep incomplete last line

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        try {
          const event = JSON.parse(line.slice(6));
          if (!currentPopup) return; // user closed popup — stop

          if (event.status === "done") {
            renderVerdict(card, event.verdict);
            // Log to service worker for dashboard stats
            chrome.runtime.sendMessage({ type: "VERDICT_LOGGED", verdict: event.verdict });
            return;
          }
          if (event.status === "error") {
            updateStatus(card, `Error: ${event.message}`, 0);
            return;
          }
          // Update progress
          updateStatus(card, event.message || "Processing...", event.confidence_so_far || 0);
        } catch {
          // malformed JSON line — skip
        }
      }
    }
  } catch (err) {
    if (currentPopup) updateStatus(card, "Connection failed. Is the backend running?", 0);
  }
}

// ─── Main selection listener ──────────────────────────────────────────────

let selectionTimeout = null;

document.addEventListener("mouseup", (e) => {
  // Debounce — wait 200ms after mouseup to read stable selection
  clearTimeout(selectionTimeout);
  selectionTimeout = setTimeout(() => handleSelectionEnd(e), 200);
});

document.addEventListener("touchend", (e) => {
  clearTimeout(selectionTimeout);
  selectionTimeout = setTimeout(() => handleSelectionEnd(e), 300);
});

function handleSelectionEnd(e) {
  // Don't trigger inside our own Shadow DOM
  if (e.target === hostEl || (shadowRoot && shadowRoot.contains(e.target))) return;

  const selection = window.getSelection();
  if (!selection || selection.isCollapsed) {
    // User clicked somewhere without selecting — dismiss micro-button
    // but NOT the card (they might be clicking a source link)
    if (currentPopup && currentPopup.className === "hfc-btn") {
      removeCurrentPopup();
    }
    return;
  }

  const selectedText = selection.toString().trim();
  if (selectedText.length < MIN_SELECTION_LENGTH) return;
  if (!isHealthRelated(selectedText)) return;

  // Get position for popup anchor
  const rect = selection.getRangeAt(0).getBoundingClientRect();
  const x = rect.left + window.scrollX;
  const y = rect.bottom + window.scrollY;

  const surrounding = getSurroundingContext(selection);

  showMicroButton(rect.right, rect.bottom, () => {
    const card = showLoadingCard(rect.left, rect.bottom, selectedText);

    const payload = {
      selected_text:       selectedText,
      surrounding_context: surrounding,
      page_title:          document.title,
      page_url:            window.location.href
    };

    streamVerdict(payload, card, rect.left, rect.bottom);
  });
}

// Dismiss popup on Escape
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") removeCurrentPopup();
});
```

### 7.3 `extension/service-worker.js`

```javascript
/**
 * service-worker.js
 * Responsibilities:
 *   - Maintain session stats for the dashboard
 *   - Handle messages from content script
 *   - No AI logic here — purely administrative
 */

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "VERDICT_LOGGED") {
    logVerdict(msg.verdict);
  }
});

async function logVerdict(verdict) {
  const data = await chrome.storage.local.get(["stats"]);
  const stats = data.stats || { total: 0, critical: 0, high: 0, medium: 0, low: 0 };
  stats.total++;
  const level = (verdict.risk_level || "low").toLowerCase();
  if (stats[level] !== undefined) stats[level]++;
  await chrome.storage.local.set({ stats });
}
```

---

## 8. API Layer (FastAPI)

### 8.1 `backend/main.py`

```python
"""
FastAPI server — exposes the agent as an SSE streaming endpoint.
Run: uvicorn backend.main:app --reload --port 8000
"""
import json
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from backend.config import ALLOWED_ORIGINS
from backend.agent.orchestrator import run_agent
from backend.cache.claim_cache import init_cache
from backend.sdgforge_hook import log_sdgforge_impact

app = FastAPI(title="Health Fact Checker API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["POST", "GET"],
    allow_headers=["*"]
)

@app.on_event("startup")
async def startup():
    await init_cache()

class VerifyRequest(BaseModel):
    selected_text:       str
    surrounding_context: str = ""
    page_title:          str = ""
    page_url:            str = ""

@app.post("/verify/stream")
async def verify_stream(req: VerifyRequest):
    """
    SSE endpoint. Streams agent progress events then final verdict.
    The extension reads this with fetch + ReadableStream.
    """
    async def event_generator():
        async for event in run_agent(
            selected_text       = req.selected_text,
            surrounding_context = req.surrounding_context,
            page_title          = req.page_title,
            page_url            = req.page_url
        ):
            yield f"data: {json.dumps(event)}\n\n"
            await asyncio.sleep(0)   # yield control to event loop

            # After final verdict, fire SDGforge hook (non-blocking)
            if event.get("status") == "done":
                asyncio.create_task(
                    log_sdgforge_impact(event.get("verdict", {}))
                )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"   # critical for Nginx — disables buffering
        }
    )

@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0"}
```

---

## 9. Claim Deduplication & Cache

### 9.1 `backend/cache/claim_cache.py`

```python
"""
SQLite-based claim deduplication cache.
Key: SHA256 hash of normalized claim text.
TTL: 24 hours (configurable in config.py).

Why SQLite: zero dependencies, sufficient for hackathon scale,
persistent across backend restarts.
"""
import hashlib
import json
import sqlite3
import asyncio
from datetime import datetime, timedelta
from backend.config import CACHE_DB_PATH, CACHE_TTL_HOURS

_db: sqlite3.Connection = None

async def init_cache():
    global _db
    _db = sqlite3.connect(CACHE_DB_PATH, check_same_thread=False)
    _db.execute("""
        CREATE TABLE IF NOT EXISTS claim_verdicts (
            claim_hash  TEXT PRIMARY KEY,
            claim_text  TEXT,
            verdict     TEXT,
            created_at  TEXT
        )
    """)
    _db.execute("CREATE INDEX IF NOT EXISTS idx_created ON claim_verdicts(created_at)")
    _db.commit()

def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())

def _hash_claim(text: str) -> str:
    return hashlib.sha256(_normalize(text).encode()).hexdigest()

async def get_cached_verdict(claim_text: str) -> dict | None:
    if _db is None:
        return None
    h = _hash_claim(claim_text)
    cutoff = (datetime.utcnow() - timedelta(hours=CACHE_TTL_HOURS)).isoformat()
    row = _db.execute(
        "SELECT verdict FROM claim_verdicts WHERE claim_hash=? AND created_at>?",
        (h, cutoff)
    ).fetchone()
    if row:
        return json.loads(row[0])
    return None

async def cache_verdict(claim_text: str, verdict: dict):
    if _db is None:
        return
    h = _hash_claim(claim_text)
    _db.execute(
        "INSERT OR REPLACE INTO claim_verdicts VALUES (?, ?, ?, ?)",
        (h, claim_text[:500], json.dumps(verdict), datetime.utcnow().isoformat())
    )
    _db.commit()
```

---

## 10. SDGforge Integration

### 10.1 `backend/sdgforge_hook.py`

```python
"""
Logs every verified claim as an SDG 3 impact event to the SDGforge platform.
Non-blocking — called with asyncio.create_task so it never slows down the response.
If SDGforge is unreachable, silently fails (no user impact).
"""
import aiohttp
from datetime import datetime, timezone
from backend.config import SDGFORGE_API, SDGFORGE_TOKEN

SDG_3_GOAL_ID = "3"   # Good Health and Well-Being

async def log_sdgforge_impact(verdict: dict):
    if not SDGFORGE_TOKEN or not SDGFORGE_API:
        return

    payload = {
        "sdg_goal":        SDG_3_GOAL_ID,
        "event_type":      "misinformation_check",
        "verdict":         verdict.get("verdict"),
        "risk_level":      verdict.get("risk_level"),
        "confidence":      verdict.get("confidence"),
        "claim_type":      verdict.get("claim_type"),
        "from_cache":      verdict.get("from_cache", False),
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "impact_metric":   "health_claims_verified"
    }

    try:
        async with aiohttp.ClientSession() as session:
            await session.post(
                f"{SDGFORGE_API}/api/impact/log",
                json=payload,
                headers={"Authorization": f"Bearer {SDGFORGE_TOKEN}"},
                timeout=aiohttp.ClientTimeout(total=3)
            )
    except Exception:
        pass   # silent fail — never interrupt the user flow
```

---

## 11. Environment & Config

### `.env` file (create in project root, never commit to git)

```env
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here
OPENFDA_KEY=                        # optional — leave empty for public rate limit
SDGFORGE_API_URL=http://localhost:8001
SDGFORGE_TOKEN=your_sdgforge_jwt_here
CACHE_DB_PATH=./cache/claims.db
```

### `.gitignore` additions

```
.env
cache/claims.db
__pycache__/
*.pyc
```

---

## 12. Build Order & Milestones

### Milestone 1 — Backend API running (2–3 hours)

1. Reorganize files into `backend/phases/` structure
2. Create `backend/main.py` with FastAPI
3. Wrap `simple_analyzer.py` phases as async functions
4. Test: `curl -X POST http://localhost:8000/verify/stream -H "Content-Type: application/json" -d '{"selected_text":"vitamin C cures cancer"}'`
5. Verify SSE events stream to terminal

### Milestone 2 — Extension thin client working (2–3 hours)

1. Write `extension/manifest.json`
2. Write `extension/content.js` — selection listener + Shadow DOM popup
3. Load extension in Chrome: `chrome://extensions` → Developer mode → Load unpacked
4. Test on a plain website first (not WebMD) — highlight any health-related text
5. Confirm micro-button appears and POST reaches the backend

### Milestone 3 — Full agent loop (3–4 hours)

1. Write `backend/agent/claim_classifier.py`
2. Write `backend/agent/tools.py` — wrap phases as tools
3. Write `backend/agent/orchestrator.py` — ReAct loop
4. Write three MCP servers in `backend/mcp/`
5. Test: drug query, health myth, disease claim — verify different tool sequences fire

### Milestone 4 — Cache + SDGforge hook (1 hour)

1. Write `backend/cache/claim_cache.py`
2. Write `backend/sdgforge_hook.py`
3. Test cache: send the same claim twice — second call should return instantly
4. Verify SDGforge receives impact log events

### Milestone 5 — Polish + demo prep (2 hours)

1. Test on strict-CSP sites: WebMD, Healthline, Wikipedia medical pages
2. Test drug queries with drug names
3. Verify verdict card renders all risk levels
4. Record demo video: highlight "vaccines cause autism" on a health site

---

## 13. Testing Checklist

### Backend tests

```bash
# Test basic detection
curl -N -X POST http://localhost:8000/verify/stream \
  -H "Content-Type: application/json" \
  -d '{"selected_text": "vitamin C cures cancer", "page_title": "Test", "page_url": "http://test.com"}'

# Test drug query
curl -N -X POST http://localhost:8000/verify/stream \
  -H "Content-Type: application/json" \
  -d '{"selected_text": "aspirin interactions with warfarin are safe", "page_title": "Test", "page_url": "http://test.com"}'

# Test cache hit (run same claim twice — second should have from_cache: true)
# Test health endpoint
curl http://localhost:8000/health
```

### Extension tests

| Test | Expected result |
|---|---|
| Highlight "vitamin C cures cancer" on any page | Micro-button appears |
| Click "Verify claim" | Loading card shows with spinner and status updates |
| Wait for result | Verdict card with CRITICAL/HIGH badge, correction text, source pills |
| Highlight text on WebMD (strict CSP) | Micro-button still appears (Shadow DOM not blocked) |
| Highlight non-health text ("the weather is nice") | Nothing happens (keyword filter fires) |
| Highlight text under 15 chars | Nothing happens (length filter fires) |
| Press Escape | Popup dismisses |
| Same claim twice | Second result returns faster (cache hit) |
| Backend offline | Card shows "Connection failed" message |

---

## 14. Known Gotchas

### The CSP problem is real on specific sites

Wikipedia, WebMD, and government health sites (CDC, NIH) use strict CSP. Test your extension on these sites specifically — not just on plain HTML pages. Shadow DOM solves the injection problem but watch for:
- Sites that override `window.getSelection` (extremely rare, basically none)
- SPAs (React/Next.js health portals) that update the DOM after selection — your `mouseup` listener still fires correctly since it reads selection at event time

### Groq rate limits

The free tier of Groq's API has rate limits. During the demo, if you run many claims quickly, you may hit a 429. Add a simple retry with 1-second backoff in `orchestrator.py` and consider caching aggressively to reduce calls.

### FastAPI SSE and Nginx

If you deploy behind Nginx, SSE buffering will silently break streaming — the user sees nothing until the whole response completes, then everything arrives at once. The response header `X-Accel-Buffering: no` in `main.py` disables this. Add `proxy_buffering off;` to your Nginx config as a backup.

### `phase4`, `phase5`, `phase6` async compatibility

Your existing phase files likely use synchronous code (`requests` library, blocking file I/O). The FastAPI async endpoint needs all `await`able calls. Wrap any synchronous phase function with `asyncio.to_thread()` in `tools.py`:

```python
import asyncio
result = await asyncio.to_thread(sync_phase4_function, claim)
```

This runs the sync function in a thread pool without blocking the event loop.

### Extension `fetch` and `localhost`

Chrome extensions can make `fetch` calls to `localhost` in development. In production, you must either deploy your backend to HTTPS and add the domain to `host_permissions` in `manifest.json`, or use a service like ngrok during demo.

### Shadow DOM `position: fixed` coordinates

The micro-button and card use `position: fixed` with coordinates derived from `getBoundingClientRect()`. On pages with CSS `transform` on an ancestor element, `getBoundingClientRect()` returns coordinates relative to the transformed container, not the viewport. This is rare but watch for it on pages with parallax scrolling effects. Fallback: use `clientX`/`clientY` from the `mouseup` event directly.

---

*End of build instructions. All code above is production-ready for hackathon scope. Do not add complexity beyond this document until all milestones pass.*