#!/usr/bin/env python3
"""Apply/verify/clear outbound Linux netem shaping on a dedicated test veth only.

This intentionally refuses arbitrary host interfaces. Create a disposable
network namespace and a dedicated interface named veth-bs-<suffix> first.
The script shapes egress on that interface only; it does not claim to shape
Android emulator traffic unless that traffic is routed through the interface.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys


IFACE_RE = re.compile(r"^veth-bs-[a-z0-9]{1,12}$")


def run(args: list[str], timeout: int = 10) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("apply", "verify", "clear"))
    parser.add_argument("--interface", required=True, help="dedicated veth named veth-bs-<suffix>")
    parser.add_argument("--latency-ms", type=float, default=180)
    parser.add_argument("--jitter-ms", type=float, default=30)
    parser.add_argument("--loss-pct", type=float, default=2)
    parser.add_argument("--rate-kbit", type=int, default=1200)
    args = parser.parse_args()

    if not IFACE_RE.fullmatch(args.interface):
        parser.error("refusing arbitrary interfaces; use a dedicated veth-bs-<suffix> test interface")
    if os.getenv("BHARATSIM_ENABLE_NETEM") != "true":
        parser.error("set BHARATSIM_ENABLE_NETEM=true only in an isolated test network namespace")
    if os.geteuid() != 0:
        parser.error("tc shaping requires root; run only inside the isolated test network namespace")
    if shutil.which("tc") is None or shutil.which("ip") is None:
        parser.error("iproute2 tools 'ip' and 'tc' must be installed")
    if args.latency_ms < 0 or args.latency_ms > 5000:
        parser.error("--latency-ms must be between 0 and 5000")
    if args.jitter_ms < 0 or args.jitter_ms > 2000:
        parser.error("--jitter-ms must be between 0 and 2000")
    if not 0 <= args.loss_pct <= 30:
        parser.error("--loss-pct must be between 0 and 30")
    if not 16 <= args.rate_kbit <= 1000000:
        parser.error("--rate-kbit must be between 16 and 1000000")

    link = run(["ip", "link", "show", "dev", args.interface])
    if link.returncode != 0:
        parser.error("dedicated test interface does not exist")

    if args.action == "apply":
        command = ["tc", "qdisc", "replace", "dev", args.interface, "root", "netem"]
        if args.latency_ms > 0:
            command += ["delay", f"{args.latency_ms:g}ms", f"{args.jitter_ms:g}ms"]
        if args.loss_pct > 0:
            command += ["loss", f"{args.loss_pct:g}%"]
        command += ["rate", f"{args.rate_kbit}kbit"]
        applied = run(command)
        if applied.returncode != 0:
            print(json.dumps({"status": "apply_failed", "stderr": applied.stderr[-1500:]}))
            return 1

    if args.action == "clear":
        cleared = run(["tc", "qdisc", "del", "dev", args.interface, "root"])
        if cleared.returncode != 0:
            print(json.dumps({"status": "clear_failed", "stderr": cleared.stderr[-1500:]}))
            return 1

    measured = run(["tc", "-s", "qdisc", "show", "dev", args.interface])
    if measured.returncode != 0:
        print(json.dumps({"status": "verify_failed", "stderr": measured.stderr[-1500:]}))
        return 1
    output = measured.stdout.strip()
    has_netem = "netem" in output
    expected = args.action != "clear"
    matched = (has_netem == expected)
    print(json.dumps({
        "status": ("qdisc_present" if has_netem else "qdisc_absent") if matched else "verification_mismatch",
        "action": args.action,
        "interface": args.interface,
        "scope": "outbound interface traffic only",
        "requested": {"latency_ms": args.latency_ms, "jitter_ms": args.jitter_ms, "loss_pct": args.loss_pct, "rate_kbit": args.rate_kbit} if args.action == "apply" else None,
        "observed_qdisc": output,
        "netem_present": has_netem,
        "verification_scope": "Presence check only. Requested latency, jitter, loss and rate values are not parsed back from tc output.",
        "warning": "This does not prove Android traffic traverses this interface; verify routing and a known endpoint separately.",
    }, indent=2))
    return 0 if matched else 2


if __name__ == "__main__":
    sys.exit(main())
