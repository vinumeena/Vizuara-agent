"""
Context Window Builder — assembles the optimal prompt context for Claude.
Applies a token budget: system > preferences > wiki > history > query.
"""

import json
from pathlib import Path
from wiki.llm_wiki import get_wiki

DATA_DIR = Path(__file__).parent.parent / "data"

MAX_CONTEXT_TOKENS = 6000   # leave ~2000 for Claude's response
AVG_CHARS_PER_TOKEN = 4     # rough estimate: 1 token ~ 4 characters

def _approx_tokens(text: str) -> int:
    return max(1, len(text) // AVG_CHARS_PER_TOKEN)


# ── System prompts per intent ─────────────────────────────────────────────────

SYSTEM_PROMPTS = {
    "IT_SUPPORT": (
        "You are Vizuara, an expert IT support assistant for Ramco Systems. "
        "Help employees resolve technical issues clearly and step-by-step. "
        "Be concise. If you cannot solve the issue, recommend raising a support ticket."
    ),
    "HR_QUERY": (
        "You are Vizuara, a friendly HR assistant for Ramco Systems. "
        "Answer HR policy questions accurately. Reference specific policies when available. "
        "If the question needs personal data you don't have, guide the user to the HRMS portal."
    ),
    "PRODUCT_ERP": (
        "You are Vizuara, a Ramco ERP product expert. "
        "Guide users through ERP features, configurations, and workflows with precision. "
        "Provide step-by-step navigation instructions when explaining how to use the system."
    ),
    "AVIATION_MRO": (
        "You are Vizuara, a Ramco Aviation Suite expert specialising in MRO, "
        "maintenance planning, airworthiness compliance, and inventory management. "
        "Use correct aviation terminology (ATA chapters, AD, SB, LLP, CRS, CAMO). "
        "Provide precise, regulation-aware guidance. Reference EASA/FAA/DGCA standards where relevant."
    ),
    "PROJECT_MGMT": (
        "You are Vizuara, a project management assistant for Ramco Systems. "
        "Help with project planning, milestone tracking, resource management, and timesheets."
    ),
    "GENERAL_CHAT": (
        "You are Vizuara, a helpful assistant for Ramco Systems employees. "
        "Respond warmly and helpfully. If the user has a work-related question, offer to assist."
    ),
    "ESCALATE": (
        "You are Vizuara. The user wants to be connected to a human agent. "
        "Acknowledge their request politely and provide escalation contact information."
    ),
    "OUT_OF_SCOPE": (
        "You are Vizuara, an assistant for Ramco Systems. "
        "This query is outside your supported topics. Politely let the user know and "
        "redirect them to relevant support channels for work-related needs."
    ),
}

DEFAULT_SYSTEM = (
    "You are Vizuara, an intelligent assistant for Ramco Systems employees. "
    "Answer questions about IT, HR, ERP products, and company policies."
)


def _load_user_preferences(user_id: str) -> dict:
    pref_path = DATA_DIR / "user_preferences.jsonl"
    if not pref_path.exists():
        return {}
    with open(pref_path, encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line.strip())
            if rec.get("user_id") == user_id:
                return rec.get("preferences", {})
    return {}


def _preferences_text(prefs: dict) -> str:
    if not prefs:
        return ""
    parts = []
    if prefs.get("tone"):
        parts.append(f"Use a {prefs['tone']} tone.")
    if prefs.get("response_format"):
        fmt = prefs["response_format"]
        if fmt == "step-by-step":
            parts.append("Structure your response as numbered steps.")
        elif fmt == "bullet-points":
            parts.append("Use bullet points in your response.")
        elif fmt == "concise":
            parts.append("Keep your response concise — 3-5 sentences max.")
    if prefs.get("detail_level") == "brief":
        parts.append("Be brief and direct.")
    return " ".join(parts)


def build_context(
    user_query: str,
    intent: str,
    user_id: str = "anonymous",
    conversation_history: list[dict] | None = None,
) -> dict:
    """
    Build the full context package for Claude.

    Returns:
        {
          "system_prompt": str,
          "messages": list of {"role": ..., "content": ...},
          "wiki_results": list,
          "wiki_score": float,
          "token_estimate": int,
        }
    """
    budget = MAX_CONTEXT_TOKENS

    # ── 1. System prompt ──────────────────────────────────────────────────────
    system_prompt = SYSTEM_PROMPTS.get(intent, DEFAULT_SYSTEM)

    # ── 2. User preferences ───────────────────────────────────────────────────
    prefs = _load_user_preferences(user_id)
    pref_text = _preferences_text(prefs)
    if pref_text:
        system_prompt = system_prompt + " " + pref_text

    budget -= _approx_tokens(system_prompt)

    # ── 3. Wiki search results ────────────────────────────────────────────────
    wiki = get_wiki()
    wiki_results = wiki.search(user_query, top_k=4)
    top_wiki_score = wiki_results[0]["relevance"] if wiki_results else 0.0

    wiki_texts = []
    for r in wiki_results:
        chunk = f"[Knowledge: {r['topic']}]\n{r['content']}"
        if _approx_tokens("\n".join(wiki_texts) + chunk) < (budget // 2):
            wiki_texts.append(chunk)

    wiki_context = "\n\n".join(wiki_texts)
    budget -= _approx_tokens(wiki_context)

    # ── 4. Conversation history (last 5 turns) ────────────────────────────────
    history = conversation_history or []
    trimmed_history = []
    history_budget = min(budget // 3, 800)
    used = 0
    for turn in reversed(history[-5:]):
        turn_tokens = _approx_tokens(turn.get("content", ""))
        if used + turn_tokens > history_budget:
            break
        trimmed_history.insert(0, turn)
        used += turn_tokens

    # ── 5. Assemble messages list ─────────────────────────────────────────────
    messages: list[dict] = []

    # Inject wiki context as a system-style user message if available
    if wiki_context:
        messages.append({
            "role": "user",
            "content": (
                f"[Reference Knowledge — use this to answer accurately]\n\n"
                f"{wiki_context}\n\n"
                f"[End of Reference Knowledge]"
            ),
        })
        messages.append({
            "role": "assistant",
            "content": "Understood. I'll use this knowledge to answer your question accurately.",
        })

    # Add trimmed conversation history
    messages.extend(trimmed_history)

    # Add current user query
    messages.append({"role": "user", "content": user_query})

    token_estimate = _approx_tokens(system_prompt) + sum(
        _approx_tokens(m["content"]) for m in messages
    )

    return {
        "system_prompt":  system_prompt,
        "messages":       messages,
        "wiki_results":   wiki_results,
        "wiki_score":     top_wiki_score,
        "token_estimate": token_estimate,
    }


if __name__ == "__main__":
    test_cases = [
        ("How do I reset my VPN password?",              "IT_SUPPORT",   "vinoodhini_d"),
        ("What is the maternity leave policy?",           "HR_QUERY",     "arjun_mehta"),
        ("How do I generate a purchase order in Ramco?", "PRODUCT_ERP",  "priya_suresh"),
    ]
    for query, intent, uid in test_cases:
        ctx = build_context(query, intent, uid)
        print(f"\nQuery  : {query}")
        print(f"Intent : {intent}")
        print(f"System : {ctx['system_prompt'][:80]}...")
        print(f"Wiki   : {len(ctx['wiki_results'])} results, top score={ctx['wiki_score']:.2f}")
        print(f"Msgs   : {len(ctx['messages'])} messages")
        print(f"Tokens : ~{ctx['token_estimate']}")
