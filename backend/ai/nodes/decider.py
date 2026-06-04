import os
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from ..state import ResearchState, DeciderRes
from ..vectorstore import vectorstore
from ..config import llm

load_dotenv()

CACHE_DISTANCE_THRESHOLD = 0.5    # cosine distance; lower = closer. TUNE THIS (see note)
CACHE_MAX_AGE_DAYS = 7


def _topic_cached(query: str) -> bool:
    """True if we already have fresh, closely-matching chunks for this topic."""
    try:
        hits = vectorstore.similarity_search_with_score(query, k=1)
    except Exception:
        return False
    if not hits:
        return False
    doc, distance = hits[0]
    print("CACHE CHECK distance:", distance)        # temporary — see how close it is
    if distance > CACHE_DISTANCE_THRESHOLD:
        return False
    fetched_at = doc.metadata.get("fetched_at")
    if not fetched_at:
        return False
    try:
        ts = datetime.fromisoformat(fetched_at)
    except ValueError:
        return False
    return datetime.now(timezone.utc) - ts < timedelta(days=CACHE_MAX_AGE_DAYS)


DECIDER_SYSTEM_PROMPT = """You are the routing step of a biomedical research assistant \
that can search PubMed, ClinicalTrials.gov, openFDA, and ChEMBL.

Given the conversation so far and the user's CURRENT query, decide three things:

1. relevant — is the query within the assistant's biomedical scope?
2. needs_retrieval — does answering require NEW biomedical evidence, or can it be answered \
from the conversation that already exists?
3. refined_query — restate what the user is asking as a clear, standalone query, resolving \
any references (like "that drug" or "those trials") using the history.

Use the conversation history carefully: a follow-up that only summarizes, rephrases, or \
reasons over a previous answer does NOT need retrieval. A follow-up asking for new specifics \
(papers, trials, safety data, mechanisms) DOES need retrieval. If the query is not \
biomedical, set relevant=false and needs_retrieval=false."""


def decider_node(state: ResearchState) -> dict:
    structured_llm = llm.with_structured_output(DeciderRes)
    history = state.get("messages", [])
    result: DeciderRes = structured_llm.invoke(
        [SystemMessage(content=DECIDER_SYSTEM_PROMPT)]
        + history
        + [HumanMessage(content=f"Current user query:\n{state['query']}")]
    )

    needs_retrieval = result.needs_retrieval and result.relevant

    # cache check only matters when we actually need evidence
    topic_cached = needs_retrieval and _topic_cached(result.refined_query)

    return {
        "relevant": result.relevant,
        "needs_retrieval": needs_retrieval,
        "topic_cached": topic_cached,
        "refined_query": result.refined_query,
    }
