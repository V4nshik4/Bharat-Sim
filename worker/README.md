# Android execution worker prototype

This is a local worker prototype, not yet connected to the FastAPI job queue. It performs real ADB install/launch/logcat collection when run explicitly on a disposable Android Emulator or test device.

## Safety first

Do not run unknown APKs on a personal phone, a host with secrets, or a production emulator. APKs can be malicious. Use a disposable emulator/VM with no sensitive accounts, restricted network egress and a clean snapshot. This script requires explicit opt-in and an explicit device serial; it never runs arbitrary shell commands from an APK or request payload.

## Prerequisites

- Android SDK platform-tools (`adb`) on PATH.
- Android SDK build-tools (`aapt`) on PATH.
- A disposable emulator/device already booted and visible to ADB.
- Python 3.10+.

## Run

```bash
export BHARATSIM_ENABLE_LOCAL_APK_EXECUTION=true
export ANDROID_SERIAL=emulator-5554
python runner.py /absolute/path/to/authorized-test.apk --duration 20 --out ./artifacts
```

The output is a JSON report and raw logcat text. It includes the APK SHA-256, package name, command return codes, timestamps and an explicit execution state. It marks a run failed when install/launch fails; collection errors are not treated as app crashes. This is a minimal smoke runner: it does not yet automate meaningful app flows, collect full ANR traces or apply network shaping.

Before connecting this worker to an API, add authenticated job/result callbacks, job leases, per-run isolation, strict quotas, artifact upload, cancellation, cleanup, worker heartbeats and signed/authorized dispatch.