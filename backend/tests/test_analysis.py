from app.main import analyze_log_text, failure_fingerprint


def test_detects_crash_network_and_memory_signals():
    text = "\n".join([
        "FATAL EXCEPTION: main",
        "java.lang.OutOfMemoryError: Failed to allocate 1024 bytes",
        "java.net.SocketTimeoutException: timeout",
    ])
    result = analyze_log_text(text, "budget-android")
    assert {f["kind"] for f in result["findings"]} == {"crash", "oom", "network"}
    assert result["summary"]["critical"] == 2
    assert result["bharat_score"]["value"] == 30
    assert all(f["evidence"][0]["line"] > 0 for f in result["findings"])


def test_clean_logs_have_full_heuristic_score_but_are_not_proof():
    result = analyze_log_text("Activity resumed\nFrame rendered", "baseline")
    assert result["findings"] == []
    assert result["bharat_score"]["value"] == 100
    assert any("does not prove" in x for x in result["limitations"])


def test_fingerprint_is_stable_and_normalizes_numbers():
    assert failure_fingerprint("request 123 failed") == failure_fingerprint("request 456 failed")


def test_invalid_persona_rejected():
    try:
        analyze_log_text("FATAL EXCEPTION", "unknown")
        assert False, "expected ValueError"
    except ValueError:
        pass
