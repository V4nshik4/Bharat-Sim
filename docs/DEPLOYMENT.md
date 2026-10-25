# Local deployment with Docker Compose

This stack builds the FastAPI API and the React dashboard, persists API data in a named volume, and proxies API paths through nginx so the frontend uses same-origin requests. It binds the web port to loopback by default and is intended for local evaluation—not public multi-user APK execution.

## Start locally

Install Docker Engine and the Compose plugin. From the repository root:

    docker compose up --build -d
    docker compose ps
    curl http://127.0.0.1:8080/health/ready

Open http://127.0.0.1:8080. API docs are available at http://127.0.0.1:8080/docs. To use another local port, set BHARATSIM_PORT before running Compose.

To stop while preserving the named data volume:

    docker compose down

To delete all local persisted data too:

    docker compose down -v

## Optional local worker

The Compose stack does not run an Android emulator. Provision a disposable emulator separately and configure a random BHARATSIM_WORKER_TOKEN in the shell before starting the API. Use the same token on the worker. Start worker/agent.py on a host that can reach the published loopback port, with an explicit ANDROID_SERIAL and BHARATSIM_ENABLE_LOCAL_APK_EXECUTION=true. For loopback-only local testing, set BHARATSIM_API_URL=http://127.0.0.1:8080 and BHARATSIM_ALLOW_INSECURE_HTTP=true in the worker environment.

Do not use plain HTTP for remote workers. Use HTTPS and a restricted network path for any remote deployment.

## Production deployment blockers

Do not expose this stack directly to the public internet. Before public use, implement real user authentication and run ownership, rate limits and quotas, private artifact storage and retention, strict worker VM isolation, egress restrictions, audit logging, backups, monitoring, and a reviewed TLS/reverse-proxy configuration. The shared worker token protects machine-to-machine endpoints; it is not user authentication. The local Compose UI binds to 127.0.0.1 by design.
