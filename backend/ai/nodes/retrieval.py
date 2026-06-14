import asyncio
from ..state import ResearchState
from ..vectorstore import vectorstore

RETRIEVAL_K = 4
TOTAL_CHAR_BUDGET = 8800  # total chars across all chunks

# weights: first result gets the most, last gets the least
CHUNK_WEIGHTS = [4, 3, 2, 1]  # must have at least RETRIEVAL_K entries


def _compute_limits(k: int, budget: int) -> list[int]:
    weights = CHUNK_WEIGHTS[:k]
    total_weight = sum(weights)
    return [int(budget * w / total_weight) for w in weights]


async def retrieval_node(state: ResearchState) -> dict:
    query = state["refined_query"]

    docs = await asyncio.to_thread(
        lambda: vectorstore.max_marginal_relevance_search(
            query, k=RETRIEVAL_K, fetch_k=15, lambda_mult=0.5
        )
    )

    limits = _compute_limits(len(docs), TOTAL_CHAR_BUDGET)

    chunks = []
    for d, char_limit in zip(docs, limits):
        m = d.metadata
        header = f"[{m.get('source','source')}] {m.get('title') or m.get('source_id') or ''}".strip()

        body = d.page_content[:char_limit].rstrip()
        if len(d.page_content) > char_limit:
            body += "…"

        chunk = f"{header}\n{body}"
        if m.get("url"):
            chunk += f"\nSource: {m['url']}"
        chunks.append(chunk)

    return {"retrieved_chunks": chunks}