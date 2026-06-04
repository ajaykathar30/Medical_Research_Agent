import json
import asyncio
import time
from datetime import datetime, timezone
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document

from ..state import ResearchState
from ..mcp_client import get_mcp_client
from ..vectorstore import vectorstore
from ..config import llm

INGEST_PROMPT = """## Role
You are the evidence-gathering component of a biomedical research assistant. Your ONLY \
job is to call the right tools to collect source material. You never answer the user's \
question yourself.

## Goal
Select the minimal set of tools needed to fully cover what the query asks, and call each \
with precise arguments. Gather enough to support a good answer, but never call a tool \
whose data the query doesn't actually need.

## Available tools
- search_literature → published research, findings, mechanisms, reviews, "what's known about…"
- search_trials → clinical trials, drug pipeline, recruiting/ongoing studies, phases, sponsors
- get_adverse_events → ONLY when the query asks about side effects, adverse reactions, or safety
- get_drug_label → ONLY when the query asks about approved uses, dosing, or warnings/contraindications
SRTICTLY - Request at most 3 results per tool while 1-2 is sufficient for most of the cases

## Task
1. Identify the key entities in the query — the condition/disease and the drug/intervention.
2. Choose which tool(s) the query genuinely requires:
   - Use search_literature and/or search_trials for research and pipeline questions.
   - Use get_adverse_events or get_drug_label ONLY if the query explicitly concerns safety, \
approval, dosing, or warnings.
3. Call multiple tools only when the query truly spans areas; otherwise call just one.
4. Pass clean, specific arguments to each tool — map the drug to the intervention field and \
the disease to the condition field, rather than dumping the whole query into one field.

Do NOT answer the question. Only call tools to gather evidence.

"""

def _extract(result) -> list:
    """Normalize any tool result into a list of parsed objects."""
    if isinstance(result, str):                       # plain JSON string
        try:
            result = json.loads(result)
        except json.JSONDecodeError:
            return []

    # MCP content blocks: [{'type':'text','text':'<json>'}, ...]  <-- your case
    if (isinstance(result, list) and result
            and isinstance(result[0], dict) and "text" in result[0]):
        items = []
        for b in result:
            if b.get("type") == "text":
                try:
                    items.append(json.loads(b["text"]))
                except json.JSONDecodeError:
                    pass
        return items

    if isinstance(result, dict):                      # {"result":[...]} or a single object
        return result["result"] if isinstance(result.get("result"), list) else [result]

    if isinstance(result, list):                      # already a list of objects
        return result

    return []


def _to_documents(source: str, items: list, topic: str) -> list[Document]:
    now = datetime.now(timezone.utc).isoformat()
    src = source.lower()
    docs: list[Document] = []

    for item in items:
        if not isinstance(item, dict):
            continue

        if "literature" in src:
            content = f"{item.get('title','')}\n\n{item.get('abstract','')}".strip()
            if not content:
                continue
            docs.append(Document(page_content=content, metadata={
                "source": "literature", "source_id": item.get("pmid"),
                "title": item.get("title"), "url": item.get("url"),
                "year": item.get("year"), "topic": topic, "fetched_at": now,
            }))

        elif "trial" in src:
            content = (f"{item.get('title','')}\n\n{item.get('summary','')}\n"
                       f"Status: {item.get('status')} | Phases: {item.get('phases')} | "
                       f"Sponsor: {item.get('lead_sponsor')}").strip()
            docs.append(Document(page_content=content, metadata={
                "source": "trials", "source_id": item.get("nct_id"),
                "title": item.get("title"), "url": item.get("url"),
                "status": item.get("status"), "topic": topic, "fetched_at": now,
            }))

        elif "adverse" in src:
            reactions = item.get("top_reactions", [])
            lines = [f"{r['reaction']}: {r['count']} reports" for r in reactions]
            content = (f"Reported adverse events for {item.get('drug')}:\n"
                       + "\n".join(lines) + f"\n\n{item.get('disclaimer','')}")
            docs.append(Document(page_content=content, metadata={
                "source": "safety", "source_id": item.get("drug"),
                "topic": topic, "fetched_at": now,
            }))

        elif "label" in src and item.get("found"):
            parts = [f"{k}: {item[k]}" for k in
                     ("indications", "boxed_warning", "warnings",
                      "contraindications", "dosage", "adverse_reactions")
                     if item.get(k)]
            content = f"FDA label for {item.get('drug')}:\n" + "\n\n".join(parts)
            docs.append(Document(page_content=content, metadata={
                "source": "label", "source_id": item.get("drug"),
                "topic": topic, "fetched_at": now,
            }))

    return docs


async def ingestion_node(state: ResearchState) -> dict:
    query = state["refined_query"]
    t0 = time.perf_counter()

    # --- phase 1: connect to MCP + load tools ---
    client = await get_mcp_client()
    tools = await client.get_tools()
    tools_by_name = {t.name: t for t in tools}
    llm_with_tools = llm.bind_tools(tools)
    t1 = time.perf_counter()
    print(f"[TIME] mcp connect + get_tools : {t1 - t0:6.2f}s")

    # --- phase 2: LLM picks the tools ---
    response = await llm_with_tools.ainvoke([
        SystemMessage(content=INGEST_PROMPT),
        HumanMessage(content=query),
    ])
    t2 = time.perf_counter()
    print(f"[TIME] llm tool-selection     : {t2 - t1:6.2f}s")

    if not response.tool_calls:
        print("!! model selected no tools")
        return {}

    # --- phase 3: execute the tool calls (the fetches) ---
    all_docs: list[Document] = []
    for call in response.tool_calls:
        ts = time.perf_counter()
        tool = tools_by_name[call["name"]]
        result = await tool.ainvoke(call["args"])
        te = time.perf_counter()
        print(f"[TIME]   tool {call['name']:<20}: {te - ts:6.2f}s")

        items = _extract(result)
        docs = _to_documents(call["name"], items, topic=query)
        print("BUILT", len(docs), "docs for", call["name"])
        all_docs.extend(docs)
    t3 = time.perf_counter()
    print(f"[TIME] all tool fetches       : {t3 - t2:6.2f}s")

    # --- phase 4: embed + store ---
    print("TOTAL docs to store:", len(all_docs))
    if all_docs:
        await asyncio.to_thread(vectorstore.add_documents, all_docs)
    t4 = time.perf_counter()
    print(f"[TIME] embed + store ({len(all_docs)} docs) : {t4 - t3:6.2f}s")

    print(f"[TIME] >>> ingestion TOTAL    : {t4 - t0:6.2f}s")
    return {}
