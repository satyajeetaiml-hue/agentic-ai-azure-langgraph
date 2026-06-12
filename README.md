# LangGraph on Azure — Support Triage Graph

[![CI](https://github.com/satyajeetaiml-hue/agentic-ai-azure-langgraph/actions/workflows/ci.yml/badge.svg)](https://github.com/satyajeetaiml-hue/agentic-ai-azure-langgraph/actions/workflows/ci.yml)

> Companion project to the *Agentic AI on Azure — Enterprise Master Class*, showing the
> **LangGraph** framework alongside the Microsoft Agent Framework labs.
> Course hub: [azure-agentic-ai-masterclass](https://github.com/satyajeetaiml-hue/azure-agentic-ai-masterclass).

> ▶️ **Run in VS Code — no Azure needed.** `pip install -r requirements.txt`, then `uvicorn app.main:app --reload` and open http://127.0.0.1:8000/docs. The LangGraph graph runs **for real** offline; Azure OpenAI is optional.

---

## 🎯 What it shows
How to build an agent as a **graph** with [LangGraph](https://langchain-ai.github.io/langgraph/):
typed shared **state**, **nodes**, and **conditional edges** — the graph executes for real even
without an LLM, and optionally calls **Azure OpenAI** to polish the answer.

## 🧩 The graph
```
START → classify → ┌─ (high severity) → escalate ─┐
                   └─ (normal)        → retrieve → respond → END
```
- **classify** — assess severity + category
- **retrieve** — pull the KB article for the category (a "tool" node)
- **respond** — finalize the answer (optionally rephrased by Azure OpenAI)
- **escalate** — route urgent tickets to a human (guardrail branch)

The response includes the `path` of nodes actually visited, so you can see the routing.

## 🚀 Quick start
```bash
python -m venv .venv && .\.venv\Scripts\Activate.ps1   # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
```bash
curl -X POST http://127.0.0.1:8000/api/v1/triage \
  -H "Content-Type: application/json" \
  -d '{"message": "Production is down, urgent!"}'      # -> escalate path
curl -X POST http://127.0.0.1:8000/api/v1/triage \
  -H "Content-Type: application/json" \
  -d '{"message": "I forgot my password"}'             # -> retrieve → respond
```
Run tests: `pytest -q`

## ☁️ Optional: Azure OpenAI
Set `AZURE_OPENAI_ENDPOINT` + `AZURE_OPENAI_API_KEY` (+ deployment) in `.env`. The `respond` node then
uses `langchain-openai`'s `AzureChatOpenAI` to rephrase the grounded answer. `GET /health` reports
`"mode": "azure"`. Without it, the graph still runs end-to-end.

## 🏗️ How it maps to the course
This is the **graph-based orchestration** counterpart to
[Weeks 6–7 (multi-agent)](https://github.com/satyajeetaiml-hue/agentic-ai-azure-week06-07-multi-agent).
LangGraph and the Microsoft Agent Framework solve similar problems (stateful, branching agent flows) with
different APIs — compare the two.

## 🧰 Tech stack
LangGraph, LangChain Core, `langchain-openai` (Azure OpenAI), FastAPI, Pydantic v2.

## 📁 Structure
```
app/graph.py    # StateGraph: state, nodes, conditional edges, compiled graph
app/main.py     # FastAPI app + POST /api/v1/triage
tests/test_app.py
```

## 📄 License
MIT — see [`LICENSE`](LICENSE).
