"""
LLM Wiki — BM25-based knowledge base search.
Loads product_knowledge.jsonl and chat_history.jsonl,
indexes them, and exposes a search function used by the context builder.
"""

import json
from pathlib import Path
from rank_bm25 import BM25Okapi

DATA_DIR = Path(__file__).parent.parent / "data"


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def _tokenize(text: str) -> list[str]:
    return text.lower().split()


class LLMWiki:
    def __init__(self):
        self.documents: list[dict] = []
        self.corpus_tokens: list[list[str]] = []
        self.bm25: BM25Okapi | None = None
        self._build_index()

    def _build_index(self):
        # Load product knowledge
        for rec in _load_jsonl(DATA_DIR / "product_knowledge.jsonl"):
            text = f"{rec.get('topic', '')} {rec.get('content', '')}"
            self.documents.append({
                "type":    "knowledge",
                "topic":   rec.get("topic", ""),
                "content": rec.get("content", ""),
                "text":    text,
            })

        # Load chat history (Q&A pairs as knowledge)
        for rec in _load_jsonl(DATA_DIR / "chat_history.jsonl"):
            text = f"{rec.get('user_query', '')} {rec.get('agent_reply', '')}"
            self.documents.append({
                "type":    "qa",
                "topic":   f"Q: {rec.get('user_query', '')[:60]}",
                "content": rec.get("agent_reply", ""),
                "text":    text,
            })

        if not self.documents:
            return

        self.corpus_tokens = [_tokenize(doc["text"]) for doc in self.documents]
        self.bm25 = BM25Okapi(self.corpus_tokens)
        print(f"[Wiki] Index built: {len(self.documents)} documents "
              f"({sum(1 for d in self.documents if d['type']=='knowledge')} knowledge, "
              f"{sum(1 for d in self.documents if d['type']=='qa')} Q&A)")

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Return top_k most relevant documents with BM25 scores."""
        if not self.bm25 or not self.documents:
            return []

        query_tokens = _tokenize(query)
        scores = self.bm25.get_scores(query_tokens)

        ranked = sorted(
            enumerate(scores), key=lambda x: x[1], reverse=True
        )[:top_k]

        results = []
        max_score = ranked[0][1] if ranked else 1.0
        for idx, score in ranked:
            if score <= 0:
                continue
            doc = self.documents[idx]
            results.append({
                "type":       doc["type"],
                "topic":      doc["topic"],
                "content":    doc["content"],
                "bm25_score": round(score, 4),
                "relevance":  round(score / max_score, 4) if max_score > 0 else 0.0,
            })
        return results

    def search_formatted(self, query: str, top_k: int = 5) -> str:
        """Returns search results as a formatted string for context injection."""
        results = self.search(query, top_k)
        if not results:
            return "No relevant knowledge found."
        parts = []
        for i, r in enumerate(results, 1):
            parts.append(f"[{i}] {r['topic']}\n{r['content']}")
        return "\n\n".join(parts)


# Module-level singleton — import and use directly
_wiki_instance: LLMWiki | None = None

def get_wiki() -> LLMWiki:
    global _wiki_instance
    if _wiki_instance is None:
        _wiki_instance = LLMWiki()
    return _wiki_instance


if __name__ == "__main__":
    wiki = LLMWiki()
    test_queries = [
        "How do I reset my VPN password?",
        "maternity leave policy",
        "purchase order approval workflow",
        "SharePoint deleted file recovery",
        "payroll PF deduction",
    ]
    print("\n--- Search Tests ---")
    for q in test_queries:
        results = wiki.search(q, top_k=2)
        print(f"\nQuery: {q}")
        for r in results:
            print(f"  [{r['relevance']:.2f}] {r['topic'][:70]}")
