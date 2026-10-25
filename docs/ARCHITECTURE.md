# BharatSim architecture

## Current implementation

The repository currently provides a FastAPI service, a React/Vite dashboard, deterministic persona profiles, a risk-ordering heuristic, SQLite persistence, APK upload metadata and a deterministic log marker analyzer.

### Data flow

1. The browser fetches personas and submits an APK with a persona selection.
2. The API validates the extension, checks the ZIP signature/archive, enforces a size limit, stores the file under a generated identifier and calculates SHA-256.
3. The run is persisted as `awaiting_worker` unless a worker URL is configured. This version does not yet dispatch to that worker.
4. Developers can paste logcat text. The analyzer detects known markers, retains line references, fingerprints signals and returns cautious next steps.
5. The score is a disclosed heuristic over detected signals only; it is not a population estimate.

## Execution worker (not implemented yet)

The next architecture milestone is a separately deployed worker that owns Android SDK/ADB and disposable emulator instances. The worker should accept signed/authorized jobs, verify the APK hash, install and launch it, execute scripted flows, collect logcat/ANR/thread and resource metrics, and report structured artifacts. It must not execute untrusted APKs in the API process.

Worker requirements:
- ephemeral emulator or physical device with clean snapshot per run;
- strict CPU, memory, disk, wall-clock and log-size limits;
- restricted network egress and no access to developer credentials;
- explicit applied/unsupported status for each network and resource constraint;
- immutable run IDs, APK hashes, timestamps, persona version and artifacts;
- cleanup after success, timeout or failure;
- a worker integration contract and authentication before enabling dispatch.

## Network shaping

Linux `tc/netem` can emulate latency, jitter, loss and rate limits on a controlled host network, but does not automatically shape traffic inside every Android Emulator topology. Validate the path with a known test endpoint and record measured/applied conditions. Do not display a profile as applied merely because the UI selected it.

## Security

APK files and logs are untrusted inputs. The current API checks archive shape and size but does not perform malware analysis and is not a secure execution sandbox. Before public deployment, add authentication, quotas, retention/cleanup, malware handling, private object storage, upload scanning and isolated worker execution. Never send logs to a hosted AI service without explicit consent.
