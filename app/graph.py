"""LangGraph — IT Support Triage Graph.

A real **LangGraph** ``StateGraph`` that demonstrates nodes, conditional edges, and
shared state. It runs **fully offline** (the nodes are plain Python), and optionally
uses **Azure OpenAI** (via ``langchain-openai``) to polish the final answer.

Graph:
    START → classify → (escalate | retrieve) → respond → END
                         └────────────────────────────────┘
"""

from __future__ import annotations

from functools import lru_cache
from typing import TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ── settings ────────────────────────────────────────────────────────────
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-4o"
    azure_openai_api_version: str = "2024-10-21"

    @property
    def use_azure(self) -> bool:
        return bool(self.azure_openai_endpoint and self.azure_openai_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()


# ── schemas ─────────────────────────────────────────────────────────────
class TriageRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Incoming support ticket / user message.")


class TriageResponse(BaseModel):
    answer: str
    category: str
    severity: str
    escalated: bool
    path: list[str] = Field(..., description="Graph nodes visited, in order.")
    mode: str


# ── knowledge / rules ───────────────────────────────────────────────────
KB = {
    "vpn": "Reset your VPN client, then reconnect with your corporate credentials.",
    "password": "Use the self-service portal to reset your password; locked accounts auto-unlock in 30 min.",
    "email": "Restart Outlook and re-add the account; check service health if many users are affected.",
}
ESCALATE_SIGNALS = ("urgent", "down", "outage", "breach", "production", "asap")


# ── graph state + nodes ─────────────────────────────────────────────────
class GraphState(TypedDict):
    message: str
    category: str
    severity: str
    escalated: bool
    answer: str
    path: list[str]


def classify_node(state: GraphState) -> dict:
    msg = state["message"].lower()
    severity = "high" if any(s in msg for s in ESCALATE_SIGNALS) else "normal"
    category = next((k for k in KB if k in msg), "general")
    return {"severity": severity, "category": category, "path": [*state["path"], "classify"]}


def route_after_classify(state: GraphState) -> str:
    return "escalate" if state["severity"] == "high" else "retrieve"


def retrieve_node(state: GraphState) -> dict:
    return {"answer": KB.get(state["category"], ""), "path": [*state["path"], "retrieve"]}


def respond_node(state: GraphState) -> dict:
    base = state["answer"] or "I couldn't find a KB article; routing to the helpdesk queue."
    return {"answer": _maybe_azure(base, state["message"]), "escalated": False,
            "path": [*state["path"], "respond"]}


def escalate_node(state: GraphState) -> dict:
    return {"answer": "Escalating to a human engineer (time-sensitive).", "escalated": True,
            "path": [*state["path"], "escalate"]}


@lru_cache
def build_graph():
    """Compile the StateGraph once and reuse it."""
    g = StateGraph(GraphState)
    g.add_node("classify", classify_node)
    g.add_node("retrieve", retrieve_node)
    g.add_node("respond", respond_node)
    g.add_node("escalate", escalate_node)

    g.add_edge(START, "classify")
    g.add_conditional_edges("classify", route_after_classify,
                            {"escalate": "escalate", "retrieve": "retrieve"})
    g.add_edge("retrieve", "respond")
    g.add_edge("respond", END)
    g.add_edge("escalate", END)
    return g.compile()


def run_triage(message: str) -> GraphState:
    initial: GraphState = {
        "message": message, "category": "", "severity": "",
        "escalated": False, "answer": "", "path": [],
    }
    return build_graph().invoke(initial)


def _maybe_azure(text: str, message: str) -> str:
    """Optionally rephrase the answer with Azure OpenAI (lazy-imported)."""
    s = get_settings()
    if not s.use_azure:
        return text
    from langchain_openai import AzureChatOpenAI

    llm = AzureChatOpenAI(
        azure_endpoint=s.azure_openai_endpoint,
        api_key=s.azure_openai_api_key,
        azure_deployment=s.azure_openai_deployment,
        api_version=s.azure_openai_api_version,
        temperature=0,
    )
    resp = llm.invoke(
        f"You are an IT helpdesk agent. Rephrase this answer politely and concisely "
        f"for the user's message '{message}':\n\n{text}"
    )
    return resp.content
