import asyncio
from ..state import ResearchState
from ..vectorstore import vectorstore

RETRIEVAL_K = 4          # was 6
CHUNK_CHAR_LIMIT = 1200   # cap each chunk's body in the context

async def retrieval_node(state: ResearchState) -> dict:
    query = state["refined_query"]

    # MMR: fetch a wider candidate pool (fetch_k), then keep k diverse, non-redundant ones
    docs = await asyncio.to_thread(
        lambda: vectorstore.max_marginal_relevance_search(
            query, k=RETRIEVAL_K, fetch_k=15, lambda_mult=0.5
        )
    )

    chunks = []
    for d in docs:
        m = d.metadata
        header = f"[{m.get('source','source')}] {m.get('title') or m.get('source_id') or ''}".strip()

        body = d.page_content[:CHUNK_CHAR_LIMIT].rstrip()
        if len(d.page_content) > CHUNK_CHAR_LIMIT:
            body += "…"

        chunk = f"{header}\n{body}"
        if m.get("url"):
            chunk += f"\nSource: {m['url']}"
        chunks.append(chunk)

    return {"retrieved_chunks": chunks}
