# Open-source components and reuse policy

BharatSim is designed to compose existing tools rather than reimplement Android infrastructure.

Potential integrations (not all are wired into this draft):
- Android Debug Bridge (ADB) and Android Emulator — official Android SDK tools; use Google's current SDK license terms.
- UI Automator — Android UI automation framework.
- Appium — optional cross-platform automation server; review upstream license and plugin dependencies before adoption.
- Linux `tc/netem` — kernel traffic control primitives for latency, jitter, loss and rate shaping on a controlled network path.
- FastAPI, Pydantic, Uvicorn, SQLite, React, Vite and Lucide — listed as application dependencies; their respective upstream licenses govern distribution.
- Sarvam AI — optional hosted service integration planned for regional-language summaries; credentials must stay server-side and sensitive logs require user consent.

No third-party source code is copied into the repository by this document. Before adding any external implementation, record its upstream URL, exact version/commit, license, modifications, and attribution obligations. Re-check transitive dependency licenses before release.
