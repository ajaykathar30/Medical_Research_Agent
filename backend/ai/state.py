from typing import TypedDict,List, Annotated,Literal,Optional
from pydantic import BaseModel , Field
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph.message import add_messages


class ResearchState(TypedDict):
    query: str
    refined_query: str
    relevant: bool                 # NEW: is the query in-scope?
    needs_retrieval: bool
    topic_cached: bool
    retrieved_chunks: List[str]
    messages: Annotated[list[BaseMessage], add_messages]
    answer: str


class DeciderRes(BaseModel):
    relevant: bool = Field(
        description="True if the request is within scope for a biomedical research "
        "assistant — diseases, drugs, clinical trials, drug safety, biomedical "
        "literature, or mechanisms. False for greetings, small talk, or off-topic asks."
    )
    needs_retrieval: bool = Field(
        description="True ONLY if answering requires fetching external biomedical "
        "evidence not already present in the conversation. Set False if the query is "
        "off-topic, a greeting, or fully answerable from the existing conversation "
        "(e.g. summarizing, rephrasing, or reasoning over a previous answer). Set True "
        "when the user asks for new facts, papers, trials, or safety data."
    )
    refined_query: str = Field(
        description="A clear, self-contained restatement of what the user is asking "
        "right now, with references resolved using the conversation history (e.g. "
        "rewrite 'tell me more about that one' into the explicit drug/disease/trial it "
        "refers to). If the query is off-topic, just restate it as-is."
    )