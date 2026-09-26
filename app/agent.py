"""
A minimal agent layer: decides whether a question should be answered by
looking up structured inventory data (a 'tool call') or by retrieving and
reasoning over unstructured documents (RAG).

This is intentionally a simple keyword router rather than a framework
(LangChain agents, native function-calling).

"""

from app.inventory import lookup_inventory, INVENTORY
from app.retrieval import retrieve
from app.llm import generate_answer

INVENTORY_KEYWORDS = ["stock", "inventory", "how many", "units", "reorder", "available"]


def _wants_inventory_lookup(question: str) -> bool:
    q = question.lower()
    return any(keyword in q for keyword in INVENTORY_KEYWORDS)


def _find_item_in_question(question: str) -> str | None:
    q = question.lower()
    for item_name in INVENTORY:
        if item_name.lower() in q:
            return item_name
    return None


def answer_question(question: str) -> dict:
    """
       Top-level entry point used by the API. Routes to a tool call or RAG,
       and returns both the answer and which path was taken (useful for
       demoing the routing logic live).
    """

    if _wants_inventory_lookup(question):
        item = _find_item_in_question(question)
        if item:
            result = lookup_inventory(item)
            if result:
                answer = (
                    f"{result['item']}: {result['stock_units']} units in stock "
                    f"(reorder level: {result['reorder_level']}). "
                    f"{'This is below reorder level.' if result['needs_reorder'] else 'Stock is healthy.'}"
                )
                return {"answer": answer, "route": "inventory_tool", "sources": []}
        # Fall through to RAG if we couldn't confidently resolve an item name

    chunks = retrieve(question, top_k=4)
    context = "\n\n".join(c["text"] for c in chunks)
    answer = generate_answer(question, context)
    sources = [{"doc_id": c["doc_id"], "doc_type": c["doc_type"], "score": c["score"]} for c in chunks]
    return {"answer": answer, "route": "rag", "sources": sources}
