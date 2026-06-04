import asyncio
from langgraph.checkpoint.memory import InMemorySaver
from graph import build_graph


async def main():
    graph = build_graph(checkpointer=InMemorySaver())

    # use a topic you HAVEN'T queried before, so run 1 is a genuine miss
    q = "What are the most reported adverse events for ibuprofen?"

    print("\n========== RUN 1 — expect: cache MISS → ingestion ==========")
    r1 = await graph.ainvoke({"query": q}, config={"configurable": {"thread_id": "miss"}})
    print("\nANSWER 1:\n", r1["answer"][:300])

    print("\n========== RUN 2 — same topic, NEW thread → expect: cache HIT → retrieval ==========")
    r2 = await graph.ainvoke({"query": q}, config={"configurable": {"thread_id": "hit"}})
    print("\nANSWER 2:\n", r2["answer"][:300])


asyncio.run(main())