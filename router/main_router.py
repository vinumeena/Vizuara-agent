"""
Main Router — orchestrates the full pipeline end-to-end.

Flow:
  query → intent_router → context_builder → Claude API
       → confidence_predictor → routing decision → logged response
"""

import os
import sys
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

# Allow running from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

import anthropic
from router.intent_router   import classify
from context.context_builder import build_context
from confidence.predictor    import compute as compute_confidence

LOG_PATH = Path(__file__).parent.parent / "logs" / "query_log.jsonl"
LOG_PATH.parent.mkdir(exist_ok=True)

ESCALATION_MESSAGE = (
    "I understand you'd like to speak with a team member directly. "
    "Please reach out through one of these channels:\n"
    "- IT Support: itsupport@vizuara-demo.com | Ext. 1100\n"
    "- HR Helpdesk: hr@vizuara-demo.com | Ext. 1200\n"
    "- General Support: helpdesk@vizuara-demo.com\n"
    "A team member will get back to you within 2 business hours."
)

OUT_OF_SCOPE_MESSAGE = (
    "I'm Vizuara, the Ramco Systems assistant. I'm set up to help with:\n"
    "- IT support and technical issues\n"
    "- HR policies, leave, and payroll queries\n"
    "- Ramco ERP product guidance\n"
    "- Project management questions\n\n"
    "Your question seems to be outside these areas. "
    "Is there anything work-related I can help you with?"
)


def _call_claude(system_prompt: str, messages: list[dict]) -> tuple[str, int]:
    """Call Claude API and return (response_text, tokens_used)."""
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )
    text = resp.content[0].text.strip()
    tokens = resp.usage.input_tokens + resp.usage.output_tokens
    return text, tokens


def _log(record: dict):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def process(
    user_query: str,
    user_id: str = "anonymous",
    conversation_history: list[dict] | None = None,
) -> dict:
    """
    Process a user query through the full pipeline.

    Returns:
        {
          "response":          str,
          "intent":            str,
          "intent_confidence": float,
          "confidence":        dict,
          "latency_ms":        int,
          "tokens_used":       int,
          "routed_to":         str,
        }
    """
    start = time.time()

    # ── 1. Intent classification ──────────────────────────────────────────────
    intent_result = classify(user_query)
    intent     = intent_result["intent"]
    intent_conf = intent_result["confidence"]

    # ── 2. Hard routing — no Claude needed ───────────────────────────────────
    if intent == "ESCALATE":
        latency_ms = int((time.time() - start) * 1000)
        result = {
            "response":          ESCALATION_MESSAGE,
            "intent":            intent,
            "intent_confidence": intent_conf,
            "confidence":        {"score": 1.0, "level": "HIGH", "wiki_score": 0.0,
                                  "intent_confidence": intent_conf, "coverage_score": 0.0,
                                  "should_escalate": False, "disclaimer": ""},
            "latency_ms":        latency_ms,
            "tokens_used":       0,
            "routed_to":         "escalation_handler",
        }
        _log({**result, "query": user_query, "user_id": user_id,
              "timestamp": datetime.now(timezone.utc).isoformat()})
        return result

    if intent == "OUT_OF_SCOPE":
        latency_ms = int((time.time() - start) * 1000)
        result = {
            "response":          OUT_OF_SCOPE_MESSAGE,
            "intent":            intent,
            "intent_confidence": intent_conf,
            "confidence":        {"score": 0.0, "level": "LOW", "wiki_score": 0.0,
                                  "intent_confidence": intent_conf, "coverage_score": 0.0,
                                  "should_escalate": True, "disclaimer": ""},
            "latency_ms":        latency_ms,
            "tokens_used":       0,
            "routed_to":         "out_of_scope_handler",
        }
        _log({**result, "query": user_query, "user_id": user_id,
              "timestamp": datetime.now(timezone.utc).isoformat()})
        return result

    # ── 3. Build context ──────────────────────────────────────────────────────
    ctx = build_context(
        user_query=user_query,
        intent=intent,
        user_id=user_id,
        conversation_history=conversation_history,
    )

    # ── 4. Compute confidence BEFORE calling Claude ───────────────────────────
    confidence = compute_confidence(
        wiki_score=ctx["wiki_score"],
        intent_confidence=intent_conf,
        wiki_results=ctx["wiki_results"],
        query=user_query,
    )

    # ── 5. Call Claude ────────────────────────────────────────────────────────
    try:
        response_text, tokens_used = _call_claude(
            ctx["system_prompt"], ctx["messages"]
        )
    except Exception as e:
        response_text = f"I'm having trouble processing your request right now. Please try again or contact support. (Error: {e})"
        tokens_used = 0

    # ── 6. Append disclaimer for low/medium confidence ────────────────────────
    if confidence["disclaimer"]:
        response_text = response_text + "\n\n---\n" + confidence["disclaimer"]

    latency_ms = int((time.time() - start) * 1000)

    result = {
        "response":          response_text,
        "intent":            intent,
        "intent_confidence": intent_conf,
        "confidence":        confidence,
        "latency_ms":        latency_ms,
        "tokens_used":       tokens_used,
        "routed_to":         "claude_api",
    }

    # ── 7. Log everything ─────────────────────────────────────────────────────
    _log({
        "timestamp":         datetime.now(timezone.utc).isoformat(),
        "user_id":           user_id,
        "query":             user_query,
        "intent":            intent,
        "intent_confidence": intent_conf,
        "confidence_score":  confidence["score"],
        "confidence_level":  confidence["level"],
        "wiki_score":        ctx["wiki_score"],
        "tokens_used":       tokens_used,
        "latency_ms":        latency_ms,
        "routed_to":         "claude_api",
    })

    return result


if __name__ == "__main__":
    test_queries = [
        ("How do I reset my VPN password?",                "vinoodhini_d"),
        ("What is the maternity leave policy at Ramco?",   "arjun_mehta"),
        ("How do I generate a purchase order in Ramco ERP?", "priya_suresh"),
        ("I need to speak to a human agent please",        "karthik_r"),
        ("What is the capital of France?",                 "deepa_nair"),
    ]

    print("=" * 60)
    print("VIZUARA MAIN ROUTER — End-to-End Test")
    print("=" * 60)

    for query, uid in test_queries:
        print(f"\nQuery   : {query}")
        result = process(query, uid)
        print(f"Intent  : {result['intent']} ({result['intent_confidence']:.2f})")
        print(f"Confidence: {result['confidence']['score']:.3f} [{result['confidence']['level']}]")
        print(f"Latency : {result['latency_ms']}ms  Tokens: {result['tokens_used']}")
        preview = result['response'][:120].encode('ascii', 'replace').decode('ascii')
        print(f"Response: {preview}...")
        print("-" * 60)
