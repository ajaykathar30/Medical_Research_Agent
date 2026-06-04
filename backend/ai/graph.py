# graph.py
from langgraph.graph import StateGraph, START, END
from .state import ResearchState
from .nodes import decider_node, ingestion_node, retrieval_node, answer_node

from datetime import datetime, timezone, timedelta
from .vectorstore import vectorstore

CACHE_MAX_AGE_DAYS = 7
CACHE_DISTANCE_THRESHOLD = 0.35   # cosine distance; lower = closer match


def _topic_cached(query: str) -> bool:
    """True if we already have fresh, closely-matching chunks for this topic."""
    try:
        hits = vectorstore.similarity_search_with_score(query, k=1)
    except Exception:
        return False
    if not hits:
        return False
    doc, distance = hits[0]
    if distance > CACHE_DISTANCE_THRESHOLD:          # nothing closely matching → miss
        return False
    fetched_at = doc.metadata.get("fetched_at")
    if not fetched_at:
        return False
    try:
        ts = datetime.fromisoformat(fetched_at)
    except ValueError:
        return False
    return datetime.now(timezone.utc) - ts < timedelta(days=CACHE_MAX_AGE_DAYS)


def route_after_decider(state: ResearchState) -> str:
    if not state.get("relevant", True) or not state.get("needs_retrieval", False):
        return "answer"
    return "retrieval" if state.get("topic_cached", False) else "ingestion"

def build_graph(checkpointer=None):
    builder = StateGraph(ResearchState)

    builder.add_node("decider", decider_node)
    builder.add_node("ingestion", ingestion_node)
    builder.add_node("retrieval", retrieval_node)
    builder.add_node("answer", answer_node)

    builder.add_edge(START, "decider")
    builder.add_conditional_edges(
        "decider",
        route_after_decider,
        {"ingestion": "ingestion", "retrieval": "retrieval", "answer": "answer"},
    )
    builder.add_edge("ingestion", "retrieval")
    builder.add_edge("retrieval", "answer")
    builder.add_edge("answer", END)

    return builder.compile(checkpointer=checkpointer)

graph = build_graph()