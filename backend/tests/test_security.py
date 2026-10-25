import io
import os
import zipfile

from fastapi.testclient import TestClient

from app.main import app, validate_apk_archive

client = TestClient(app)


def make_zip(entries):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, value in entries:
            archive.writestr(name, value)
    return stream.getvalue()


def test_valid_apk_like_archive_passes_manifest_and_bounds(tmp_path):
    path = tmp_path / "valid.apk"
    path.write_bytes(make_zip([("AndroidManifest.xml", b"manifest"), ("classes.dex", b"dex")]))
    validate_apk_archive(path)


def test_arbitrary_zip_without_android_manifest_is_rejected(tmp_path):
    path = tmp_path / "not-apk.apk"
    path.write_bytes(make_zip([("notes.txt", b"not an apk")]))
    try:
        validate_apk_archive(path)
        assert False, "expected invalid APK rejection"
    except Exception as exc:
        assert "AndroidManifest.xml" in str(exc)


def test_api_key_gate_rejects_missing_key(monkeypatch):
    monkeypatch.setenv("BHARATSIM_REQUIRE_API_KEY", "true")
    monkeypatch.setenv("BHARATSIM_API_KEY", "a" * 40)
    response = client.get("/api/v1/personas")
    assert response.status_code == 401


def test_api_key_gate_accepts_correct_key(monkeypatch):
    monkeypatch.setenv("BHARATSIM_REQUIRE_API_KEY", "true")
    monkeypatch.setenv("BHARATSIM_API_KEY", "b" * 40)
    response = client.get("/api/v1/personas", headers={"X-BharatSim-API-Key": "b" * 40})
    assert response.status_code == 200


def test_api_key_gate_fails_closed_without_configured_key(monkeypatch):
    monkeypatch.setenv("BHARATSIM_REQUIRE_API_KEY", "true")
    monkeypatch.delenv("BHARATSIM_API_KEY", raising=False)
    response = client.get("/api/v1/personas")
    assert response.status_code == 503
