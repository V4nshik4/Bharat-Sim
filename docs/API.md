# API contract (v0.1)

Base URL: `http://localhost:8000`

- `GET /health/live` — process liveness.
- `GET /health/ready` — database readiness and explicit worker configuration state.
- `GET /api/v1/capabilities` — reports supported and not-yet-supported capabilities.
- `GET /api/v1/personas` — available device/network persona definitions.
- `POST /api/v1/plan` — JSON body with `persona_ids`, `critical_flows`, and `max_scenarios`; returns risk-ordered scenarios.
- `POST /api/v1/runs` — multipart form fields `persona_id` and optional `apk`; validates and fingerprints APK, then records the run.
- `GET /api/v1/runs` — recent run metadata.
- `GET /api/v1/runs/{id}` — run detail.
- `POST /api/v1/analyze/logs` — JSON body `{ "text": "...", "persona_id": "budget-android" }`; returns evidence-linked marker findings and heuristic score.
- `GET /api/v1/analyses` — persisted analyses.

All current endpoints are development APIs. Authentication and public deployment hardening remain required before accepting untrusted users at scale.
