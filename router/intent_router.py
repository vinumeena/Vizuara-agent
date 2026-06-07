"""
Intent Router — classifies incoming queries into one of 7 intents.
Uses keyword rules first (fast, free), then falls back to Claude for ambiguous cases.
"""

import os
import re
import json
from dotenv import load_dotenv

load_dotenv()

INTENTS = [
    "IT_SUPPORT",       # technical issues, software, hardware, access
    "HR_QUERY",         # leave, payroll, policy, onboarding, benefits
    "PRODUCT_ERP",      # Ramco ERP / HCM usage questions
    "PROJECT_MGMT",     # project tracking, milestones, resources
    "GENERAL_CHAT",     # greetings, thanks, casual messages
    "ESCALATE",         # explicit request for human/manager
    "OUT_OF_SCOPE",     # unrelated to supported domains
]

# Keyword rules — ordered by specificity (checked top to bottom, first match wins)
_RULES: list[tuple[str, list[str]]] = [
    ("ESCALATE", [
        "speak to human", "talk to agent", "need a person", "escalate",
        "manager please", "real person", "human agent", "talk to someone",
    ]),
    ("HR_QUERY", [
        "leave", "payslip", "salary", "appraisal", "performance", "onboard",
        "maternity", "paternity", "hr", "payroll", "pf ", "reimbursement",
        "expense claim", "work from home", "wfh", "referral", "resignation",
        "notice period", "travel policy", "increment", "bonus",
    ]),
    ("IT_SUPPORT", [
        "vpn", "password", "laptop", "printer", "software", "install",
        "access denied", "network", "email", "outlook", "teams not working",
        "onedrive", "sharepoint", "mfa", "multi-factor", "it helpdesk",
        "ticket", "slow", "not syncing", "virus", "usb",
    ]),
    ("PRODUCT_ERP", [
        "ramco erp", "purchase order", "invoice", "accounts payable",
        "general ledger", "month-end", "payroll setup", "hcm", "cost center",
        "workflow", "approval", "3-way match", "grn", "blanket po",
        "fixed assets", "depreciation", "bank reconciliation", "timesheet",
        "erp", "procurement", "vendor",
    ]),
    ("PROJECT_MGMT", [
        "milestone", "project", "gantt", "resource", "billable", "timesheet",
        "project manager", "sprint", "deliverable", "deadline",
    ]),
    ("GENERAL_CHAT", [
        "hello", "hi ", "hey ", "good morning", "good afternoon",
        "thank you", "thanks", "how are you", "bye", "see you",
    ]),
]


def _keyword_classify(query: str) -> tuple[str, float] | None:
    q = query.lower()
    for intent, keywords in _RULES:
        for kw in keywords:
            if kw in q:
                return intent, 0.85
    return None


def _llm_classify(query: str) -> tuple[str, float]:
    """Claude-based fallback classification."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        prompt = (
            f"Classify this user query into exactly one of these categories:\n"
            f"{', '.join(INTENTS)}\n\n"
            f"Definitions:\n"
            f"- IT_SUPPORT: technical problems, software, hardware, network, VPN, email\n"
            f"- HR_QUERY: leave, payroll, HR policies, onboarding, benefits, expenses\n"
            f"- PRODUCT_ERP: Ramco ERP or HCM product usage, features, configuration\n"
            f"- PROJECT_MGMT: project tracking, milestones, resources, timesheets\n"
            f"- GENERAL_CHAT: greetings, thanks, casual small talk\n"
            f"- ESCALATE: user wants to speak to a human agent or manager\n"
            f"- OUT_OF_SCOPE: unrelated to any supported domain\n\n"
            f"Query: {query}\n\n"
            f"Reply with a JSON object only: {{\"intent\": \"<CATEGORY>\", \"confidence\": <0.0-1.0>}}"
        )
        resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=60,
            messages=[{"role": "user", "content": prompt}],
        )
        text = resp.content[0].text.strip()
        # Extract JSON even if wrapped in markdown
        match = re.search(r'\{.*?\}', text, re.DOTALL)
        if match:
            data = json.loads(match.group())
            intent = data.get("intent", "OUT_OF_SCOPE").upper()
            if intent not in INTENTS:
                intent = "OUT_OF_SCOPE"
            confidence = float(data.get("confidence", 0.7))
            return intent, confidence
    except Exception as e:
        print(f"[IntentRouter] LLM fallback error: {e}")
    return "OUT_OF_SCOPE", 0.5


def classify(query: str) -> dict:
    """
    Classify a query and return intent + confidence.

    Returns:
        {
          "intent": "IT_SUPPORT",
          "confidence": 0.85,
          "method": "keyword" | "llm"
        }
    """
    # Fast keyword path
    result = _keyword_classify(query)
    if result:
        intent, confidence = result
        return {"intent": intent, "confidence": confidence, "method": "keyword"}

    # LLM fallback for ambiguous queries
    intent, confidence = _llm_classify(query)
    return {"intent": intent, "confidence": confidence, "method": "llm"}


if __name__ == "__main__":
    test_queries = [
        "How do I reset my VPN password?",
        "What is the maternity leave policy?",
        "How do I run month-end closing in Ramco Finance?",
        "Can I create a project milestone?",
        "I need to speak to a human agent please",
        "Hello, good morning!",
        "What is the capital of France?",
        "My payslip shows wrong PF deduction",
        "Invoice matching is failing in AP module",
        "How do I install VS Code on my laptop?",
    ]
    print("--- Intent Router Tests ---\n")
    for q in test_queries:
        result = classify(q)
        print(f"Q: {q[:60]}")
        print(f"   Intent: {result['intent']:<15} Confidence: {result['confidence']:.2f}  Method: {result['method']}")
        print()
