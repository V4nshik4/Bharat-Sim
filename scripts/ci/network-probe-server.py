#!/usr/bin/env python3
"""Disposable CI-only HTTP payload server for measuring real emulator traffic."""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

PAYLOAD_SIZE = 2_000_000
PAYLOAD = (b"BharatSim controlled network probe payload\n" * ((PAYLOAD_SIZE // 42) + 1))[:PAYLOAD_SIZE]


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self) -> None:
        parsed = urlsplit(self.path)
        if parsed.path == "/health":
            body = b"ok\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        params = parse_qs(parsed.query)
        if parsed.path != "/payload" or params.get("bytes") != [str(PAYLOAD_SIZE)]:
            self.send_error(404, "Only the fixed 2,000,000-byte test payload is available")
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(PAYLOAD)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Connection", "close")
        self.end_headers()
        try:
            self.wfile.write(PAYLOAD)
            self.wfile.flush()
            print(f"served_bytes={len(PAYLOAD)} client={self.client_address[0]}", flush=True)
        except (BrokenPipeError, ConnectionResetError):
            print(f"client_disconnected={self.client_address[0]}", flush=True)

    def log_message(self, format: str, *args: object) -> None:
        print(f"probe_server {self.client_address[0]} {format % args}", flush=True)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 8001), Handler)
    server.daemon_threads = True
    print(f"listening=0.0.0.0:8001 payload_bytes={PAYLOAD_SIZE}", flush=True)
    server.serve_forever()
