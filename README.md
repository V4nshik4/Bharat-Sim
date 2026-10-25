# BharatSim 🇮🇳

**The Cheap Phone Test** — test Android apps under constrained device and unreliable-network conditions, and explain failures with traceable evidence.

> Status: early MVP scaffold. A successful analysis of uploaded logs is not the same as running an APK on an Android worker; the runner must explicitly report when that worker is unavailable.

## MVP capabilities
- Bharat personas for constrained device/network scenarios.
- Risk-ranked deterministic test plans.
- Safe APK upload with size/type checks and SHA-256 fingerprinting.
- Run/job API with persisted metadata and honest worker readiness.
- Log ingestion, crash/ANR signal detection, failure fingerprints, evidence-linked diagnostics, and transparent BharatScore.
- React/Vite dashboard for configuring personas, submitting APKs, and viewing API results.
- Optional Sarvam translation integration when credentials are configured; English fallback works without external AI credentials.

## Architecture
- `backend/`: FastAPI API, SQLite persistence, analysis engine, upload handling.
- `frontend/`: Vite + React dashboard.
- `tests/`: backend unit and API tests.
- `docs/`: architecture, API contract, validation and roadmap.

## Run locally
### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Open http://localhost:8000/docs and http://localhost:8000/health/ready.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Set `VITE_API_BASE_URL=http://localhost:8000` in `frontend/.env.local` if the API is not on the default origin. Never put private keys in `VITE_*` variables.

### Tests
```bash
cd backend
pip install -r requirements-dev.txt
pytest -q
```

## Important execution boundary
APK installation and interactive device execution require Android SDK/ADB and a provisioned emulator/physical-device worker. The API does not claim that an APK was executed unless a configured worker reports an actual run. Without one, it can analyze uploaded logs or report the run as awaiting a worker. Network shaping depends on host privileges and emulator topology; every constraint must be recorded as verified or unsupported.

## Security notes
Treat uploaded APKs as untrusted. Run execution in an isolated, disposable worker with no production secrets, restricted network egress, resource/time limits, and cleanup. Do not execute uploaded APKs in the API process. Do not upload sensitive crash logs to third-party AI services without consent.

## License
MIT — see `LICENSE`.