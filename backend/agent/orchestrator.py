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
                model="llama-3.3-70b-versatile",
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
            model="llama-3.3-70b-versatile",
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
