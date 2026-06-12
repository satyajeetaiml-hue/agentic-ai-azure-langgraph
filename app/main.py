"""LangGraph — IT Support Triage Graph (FastAPI service).

Runs a real LangGraph StateGraph. Works offline (mock mode); set Azure OpenAI
env vars to polish answers with a model. Run:  uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app.graph import TriageRequest, TriageResponse, get_settings, run_triage

settings = get_settings()
app = FastAPI(title="LangGraph — Support Triage Graph", version="0.1.0")


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "framework": "langgraph", "mode": "azure" if settings.use_azure else "mock"}


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {
        "service": "agentic-ai-azure-langgraph",
        "endpoint": "/api/v1/triage",
        "mode": "azure" if settings.use_azure else "mock",
        "docs": "/docs",
    }


@app.post("/api/v1/triage", response_model=TriageResponse, tags=["langgraph"])
def triage(payload: TriageRequest) -> TriageResponse:
    result = run_triage(payload.message)
    return TriageResponse(
        answer=result["answer"],
        category=result["category"],
        severity=result["severity"],
        escalated=result["escalated"],
        path=result["path"],
        mode="azure" if settings.use_azure else "mock",
    )
