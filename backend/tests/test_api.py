from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_and_capabilities_are_honest():
    assert client.get("/health/live").json()["status"] == "alive"
    ready = client.get("/health/ready").json()
    assert ready["execution_capability"] == "external-worker-required"
    caps = client.get("/api/v1/capabilities").json()
    assert caps["log_analysis"] is True
    assert caps["network_shaping"] is False


def test_personas_and_plan():
    personas = client.get("/api/v1/personas").json()["items"]
    assert len(personas) >= 4
    response = client.post("/api/v1/plan", json={
        "persona_ids": ["baseline", "edge-village"],
        "critical_flows": ["cold start", "payment retry"],
        "max_scenarios": 3,
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["scenarios"]) == 3
    assert data["scenarios"][0]["risk_score"] >= data["scenarios"][-1]["risk_score"]


def test_log_analysis_persists_report():
    response = client.post("/api/v1/analyze/logs", json={
        "text": "FATAL EXCEPTION: main\njava.net.SocketTimeoutException: timeout",
        "persona_id": "budget-android",
    })
    assert response.status_code == 200
    assert response.json()["summary"]["finding_count"] == 2
    assert client.get("/api/v1/analyses").status_code == 200


def test_unknown_persona_rejected():
    response = client.post("/api/v1/analyze/logs", json={"text": "hello", "persona_id": "missing"})
    assert response.status_code == 422
