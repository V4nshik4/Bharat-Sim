# Roadmap to a credible hackathon MVP

## Implemented in this draft
- [x] Repository scaffold and setup instructions.
- [x] Four named persona definitions.
- [x] Deterministic risk-ranked test planner.
- [x] APK upload validation, size cap and SHA-256 fingerprint.
- [x] SQLite persistence for runs and log analyses.
- [x] Crash, ANR, memory, network, StrictMode and storage log markers.
- [x] Stable fingerprints, source-line evidence and cautious recommendations.
- [x] Transparent heuristic BharatScore and explicit limitations.
- [x] Responsive dashboard for personas, run records, log analysis and JSON export.
- [x] API tests and architecture/API documentation.

## Must do before claiming full execution support
- [ ] Implement and deploy a sandboxed Android worker; connect job dispatch and authenticated result callbacks.
- [ ] Install/launch real APKs and capture actual device logs, exit reasons, ANRs and resource metrics.
- [ ] Add reproducible UI flows using UI Automator/Appium and test app-specific interactions.
- [ ] Implement and verify network shaping; report measured vs requested network conditions.
- [ ] Implement resource pressure safely and report unsupported constraints rather than pretending to apply them.
- [ ] Add authenticated users, per-user job ownership, quotas, upload cleanup and security review.
- [ ] Run backend tests and frontend production build in CI; add browser-level tests.
- [ ] Add Sarvam translation integration with server-side secrets, consent, timeout, redaction and fallback. It is not wired yet.
- [ ] Add actual worker integration tests and repeatability tests on a clean machine.
- [ ] Deploy frontend/API/worker, verify public health endpoints and document the deployed commit.
- [ ] Review license obligations for any adopted open-source code and document model/service provenance.

## Demo truth policy
Never label an uploaded APK as tested until a worker reports execution evidence. Never fabricate crashes, network graphs or user-population impact estimates. Clearly distinguish actual measurements, heuristic scores and unverified assumptions.
