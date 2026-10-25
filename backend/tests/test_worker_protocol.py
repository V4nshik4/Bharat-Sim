import io
import os
import zipfile

from fastapi.testclient import TestClient

from app import main


def apk_bytes():
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("AndroidManifest.xml", b"test manifest")
        archive.writestr("classes.dex", b"test dex")
    return stream.getvalue()


def prepare_isolated_db(monkeypatch, tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    upload_dir = data_dir / "uploads"
    upload_dir.mkdir()
    monkeypatch.setattr(main, "DB_PATH", data_dir / "test.sqlite3")
    monkeypatch.setattr(main, "DATA_DIR", data_dir)
    monkeypatch.setattr(main, "UPLOAD_DIR", upload_dir)
    monkeypatch.setenv("BHARATSIM_REQUIRE_API_KEY", "false")
    monkeypatch.setenv("BHARATSIM_WORKER_TOKEN", "worker-test-secret-" + "x" * 40)
    main.init_db()
    return TestClient(main.app)


def test_worker_claim_requires_worker_token(monkeypatch, tmp_path):
    client = prepare_isolated_db(monkeypatch, tmp_path)
    response = client.post("/internal/worker/claim", json={"worker_id": "test-worker"})
    assert response.status_code == 401


def test_worker_claim_download_and_result_round_trip(monkeypatch, tmp_path):
    client = prepare_isolated_db(monkeypatch, tmp_path)
    token = os.environ["BHARATSIM_WORKER_TOKEN"]
    headers = {"X-BharatSim-Worker-Token": token}

    apk_content = apk_bytes()
    created = client.post(
        "/api/v1/runs",
        data={"persona_id": "baseline"},
        files={"apk": ("tiny-test.apk", apk_content, "application/vnd.android.package-archive")},
    )
    assert created.status_code == 200
    run = created.json()
    assert run["status"] == "queued"
    run_id = run["id"]

    claimed = client.post("/internal/worker/claim", headers=headers, json={"worker_id": "ci-worker-1"})
    assert claimed.status_code == 200
    job = claimed.json()["job"]
    assert job["id"] == run_id
    assert job["attempt"] == 1

    downloaded = client.get(
        f"/internal/worker/runs/{run_id}/apk",
        headers={**headers, "X-BharatSim-Lease-Token": job["lease_token"]},
    )
    assert downloaded.status_code == 200
    assert downloaded.content == apk_content

    report = {
        "status": "completed",
        "schema_version": "1.0",
        "apk_sha256": run["apk"]["sha256"],
        "steps": [{"name": "test-fixture", "return_code": 0}],
        "limitations": ["This is a protocol test fixture, not a real emulator run."],
    }
    submitted = client.post(
        f"/internal/worker/runs/{run_id}/result",
        headers=headers,
        json={"lease_token": job["lease_token"], "status": "completed", "result": report},
    )
    assert submitted.status_code == 200
    assert submitted.json()["evidence_saved"] is True

    fetched = client.get(f"/api/v1/runs/{run_id}").json()
    assert fetched["status"] == "completed"
    assert fetched["result"]["schema_version"] == "1.0"
    assert client.get("/api/v1/workers").json()["online_count"] == 1

    stale = client.post(
        f"/internal/worker/runs/{run_id}/result",
        headers=headers,
        json={"lease_token": job["lease_token"], "status": "completed", "result": report},
    )
    assert stale.status_code == 409


def test_worker_cannot_claim_success_without_completed_report(monkeypatch, tmp_path):
    client = prepare_isolated_db(monkeypatch, tmp_path)
    token = os.environ["BHARATSIM_WORKER_TOKEN"]
    headers = {"X-BharatSim-Worker-Token": token}
    created = client.post(
        "/api/v1/runs",
        data={"persona_id": "baseline"},
        files={"apk": ("tiny-test.apk", apk_bytes(), "application/vnd.android.package-archive")},
    )
    run_id = created.json()["id"]
    job = client.post("/internal/worker/claim", headers=headers, json={"worker_id": "ci-worker-2"}).json()["job"]
    response = client.post(
        f"/internal/worker/runs/{run_id}/result",
        headers=headers,
        json={"lease_token": job["lease_token"], "status": "completed", "result": {"status": "failed"}},
    )
    assert response.status_code == 422
