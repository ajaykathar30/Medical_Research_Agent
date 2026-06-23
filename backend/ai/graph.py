# graph.py
from langgraph.graph import StateGraph, START, END
from .state import ResearchState
from .nodes import decider_node, ingestion_node, retrieval_node, answer_node


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