"""
Confidence Predictor — scores how reliable the agent's response is.

Combines 3 signals:
  wiki_score     (0.0-1.0)  — how relevant the knowledge base result was
  intent_conf    (0.0-1.0)  — how confidently the intent was classified
  coverage_score (0.0-1.0)  — how many query keywords appear in wiki results

Final score thresholds:
  >= 0.70  HIGH    — answer directly
  0.45-0.69  MEDIUM  — answer with a disclaimer
  < 0.45   LOW    — ask clarifying question or escalate
"""


def _coverage_score(query: str, wiki_results: list[dict]) -> float:
    """Fraction of meaningful query words found in wiki results."""
    stopwords = {
        "i", "me", "my", "the", "a", "an", "is", "it", "in", "on", "at",
        "to", "do", "how", "what", "can", "for", "of", "and", "or", "not",
        "be", "this", "that", "with", "from", "was", "are",
    }
    words = [w for w in query.lower().split() if w not in stopwords and len(w) > 2]
    if not words:
        return 0.5

    combined = " ".join(
        r.get("content", "") + " " + r.get("topic", "") for r in wiki_results
    ).lower()

    matched = sum(1 for w in words if w in combined)
    return round(matched / len(words), 3)


def compute(
    wiki_score: float,
    intent_confidence: float,
    wiki_results: list[dict],
    query: str,
) -> dict:
    """
    Compute composite confidence score.

    Args:
        wiki_score:        Top BM25 relevance score from wiki search (0-1)
        intent_confidence: Confidence from intent router (0-1)
        wiki_results:      List of wiki search result dicts
        query:             Original user query string

    Returns:
        {
          "score": float,           # 0.0-1.0 composite score
          "level": str,             # "HIGH" | "MEDIUM" | "LOW"
          "wiki_score": float,
          "intent_confidence": float,
          "coverage_score": float,
          "should_escalate": bool,
          "disclaimer": str,        # empty string if HIGH
        }
    """
    coverage = _coverage_score(query, wiki_results)

    # Weighted composite
    score = (
        0.45 * wiki_score
        + 0.35 * intent_confidence
        + 0.20 * coverage
    )
    score = round(min(max(score, 0.0), 1.0), 3)

    if score >= 0.70:
        level = "HIGH"
        disclaimer = ""
        escalate = False
    elif score >= 0.45:
        level = "MEDIUM"
        disclaimer = (
            "Note: I'm moderately confident in this answer. "
            "Please verify with the official portal or your team lead if in doubt."
        )
        escalate = False
    else:
        level = "LOW"
        disclaimer = (
            "I'm not fully confident in this answer for your specific situation. "
            "I recommend contacting the relevant support team directly."
        )
        escalate = True

    return {
        "score":              score,
        "level":              level,
        "wiki_score":         round(wiki_score, 3),
        "intent_confidence":  round(intent_confidence, 3),
        "coverage_score":     round(coverage, 3),
        "should_escalate":    escalate,
        "disclaimer":         disclaimer,
    }


if __name__ == "__main__":
    # Simulate test cases
    test_cases = [
        {
            "label": "Strong match — VPN reset",
            "wiki_score": 1.00, "intent_conf": 0.85,
            "query": "How do I reset my VPN password?",
            "wiki_results": [{"content": "VPN password reset IT portal", "topic": "IT Policy > VPN Access"}],
        },
        {
            "label": "Partial match — leave balance",
            "wiki_score": 0.60, "intent_conf": 0.85,
            "query": "Can I check my leave balance on mobile?",
            "wiki_results": [{"content": "leave management HRMS portal casual sick earned", "topic": "ERP > HCM > Leave"}],
        },
        {
            "label": "Weak match — unrelated question",
            "wiki_score": 0.10, "intent_conf": 0.50,
            "query": "What is the best programming language?",
            "wiki_results": [{"content": "software install license approved catalog", "topic": "IT Policy"}],
        },
    ]

    print("--- Confidence Predictor Tests ---\n")
    for tc in test_cases:
        result = compute(tc["wiki_score"], tc["intent_conf"], tc["wiki_results"], tc["query"])
        print(f"Case: {tc['label']}")
        print(f"  Score: {result['score']:.3f}  Level: {result['level']}")
        print(f"  Wiki={result['wiki_score']:.2f}  Intent={result['intent_confidence']:.2f}  Coverage={result['coverage_score']:.2f}")
        if result["disclaimer"]:
            print(f"  Disclaimer: {result['disclaimer'][:70]}...")
        print()
