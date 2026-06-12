"""Tests for the LangGraph triage graph (runs the real compiled graph, offline)."""

from fastapi.testclient import TestClient

from app.graph import run_triage
from app.main import app

client = TestClient(app)


def test_health_mock():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["mode"] == "mock"
    assert r.json()["framework"] == "langgraph"


def test_normal_ticket_takes_retrieve_respond_path():
    r = client.post("/api/v1/triage", json={"message": "I forgot my password"})
    assert r.status_code == 200
    body = r.json()
    assert body["category"] == "password"
    assert body["escalated"] is False
    assert body["path"] == ["classify", "retrieve", "respond"]


def test_urgent_ticket_takes_escalate_path():
    r = client.post("/api/v1/triage", json={"message": "Production is down, urgent!"})
    body = r.json()
    assert body["severity"] == "high"
    assert body["escalated"] is True
    assert body["path"] == ["classify", "escalate"]


def test_graph_invoked_directly():
    # The compiled StateGraph can be invoked outside FastAPI too.
    result = run_triage("vpn won't connect")
    assert result["category"] == "vpn"
    assert "VPN" in result["answer"]


def test_validation_rejects_empty():
    assert client.post("/api/v1/triage", json={"message": ""}).status_code == 422
