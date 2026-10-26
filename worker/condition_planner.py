#!/usr/bin/env python3
"""Condition planner for BharatSim persona simulation on Android targets.

Translates authored persona targets and device serial information into a
structured, evidence-backed condition plan. Classifies every condition truthfully
as supported, control_plane_verifiable, report_only, or unsupported.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PlannedCondition:
    name: str
    requested: bool
    target_value: Any
    classification: str
    reason: str
    mechanism: str | None = None
    parameters: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "requested": self.requested,
            "target_value": self.target_value,
            "classification": self.classification,
            "reason": self.reason,
            "mechanism": self.mechanism,
            "parameters": self.parameters,
        }


@dataclass
class ConditionPlan:
    persona_id: str
    target_serial: str
    is_emulator: bool
    conditions: list[PlannedCondition]

    def get_condition(self, name: str) -> PlannedCondition | None:
        for c in self.conditions:
            if c.name == name:
                return c
        return None

    def to_dict(self) -> dict[str, Any]:
        return {
            "persona_id": self.persona_id,
            "target_serial": self.target_serial,
            "is_emulator": self.is_emulator,
            "conditions": [c.to_dict() for c in self.conditions],
            "supported": [c.name for c in self.conditions if c.classification == "supported"],
            "control_plane_verifiable": [
                c.name for c in self.conditions if c.classification == "control_plane_verifiable"
            ],
            "unsupported": [c.name for c in self.conditions if c.classification == "unsupported"],
            "report_only": [c.name for c in self.conditions if c.classification == "report_only"],
        }


def is_emulator_serial(serial: str) -> bool:
    """Check if the provided device serial conforms to the Android Emulator naming pattern."""
    return bool(re.fullmatch(r"emulator-\d+", serial.strip()))


def plan_conditions(profile: dict[str, Any] | None, serial: str) -> ConditionPlan:
    """Plan and classify persona condition application for an Android target device.

    Args:
        profile: The persona dictionary containing network, battery, memory, and storage targets.
        serial: The ADB serial of the target device.

    Returns:
        A structured ConditionPlan with explicit capability classifications.
    """
    profile = profile or {}
    persona_id = str(profile.get("id") or "unknown")
    is_emu = is_emulator_serial(serial)
    conditions: list[PlannedCondition] = []

    # 1. Network latency
    latency_val = profile.get("latency_ms")
    if latency_val is not None:
        try:
            latency_int = int(latency_val)
            if is_emu:
                conditions.append(
                    PlannedCondition(
                        name="network_latency",
                        requested=True,
                        target_value=latency_int,
                        classification="supported",
                        reason="Android emulator console supports network delay simulation with status readback",
                        mechanism="adb emu network delay <latency_ms> with emu network status readback verification",
                        parameters={"latency_ms": latency_int},
                    )
                )
            else:
                conditions.append(
                    PlannedCondition(
                        name="network_latency",
                        requested=True,
                        target_value=latency_int,
                        classification="unsupported",
                        reason="Target is not an Android Emulator serial; emulator console network delay is unsupported on physical devices",
                    )
                )
        except (ValueError, TypeError):
            conditions.append(
                PlannedCondition(
                    name="network_latency",
                    requested=True,
                    target_value=latency_val,
                    classification="unsupported",
                    reason="Invalid latency_ms value in persona profile",
                )
            )
    else:
        conditions.append(
            PlannedCondition(
                name="network_latency",
                requested=False,
                target_value=None,
                classification="not_requested",
                reason="Latency not specified in persona profile",
            )
        )

    # 2. Download bandwidth
    down_val = profile.get("down_kbps")
    if down_val is not None:
        try:
            down_int = int(down_val)
            if is_emu:
                conditions.append(
                    PlannedCondition(
                        name="download_bandwidth",
                        requested=True,
                        target_value=down_int,
                        classification="supported",
                        reason="Android emulator console supports download speed shaping with status readback",
                        mechanism="adb emu network speed <up>:<down> with emu network status readback verification",
                        parameters={"down_kbps": down_int},
                    )
                )
            else:
                conditions.append(
                    PlannedCondition(
                        name="download_bandwidth",
                        requested=True,
                        target_value=down_int,
                        classification="unsupported",
                        reason="Target is not an Android Emulator serial; emulator console speed shaping is unsupported on physical devices",
                    )
                )
        except (ValueError, TypeError):
            conditions.append(
                PlannedCondition(
                    name="download_bandwidth",
                    requested=True,
                    target_value=down_val,
                    classification="unsupported",
                    reason="Invalid down_kbps value in persona profile",
                )
            )
    else:
        conditions.append(
            PlannedCondition(
                name="download_bandwidth",
                requested=False,
                target_value=None,
                classification="not_requested",
                reason="Download bandwidth not specified in persona profile",
            )
        )

    # 3. Upload bandwidth
    up_val = profile.get("up_kbps")
    if up_val is not None:
        try:
            up_int = int(up_val)
            if is_emu:
                conditions.append(
                    PlannedCondition(
                        name="upload_bandwidth",
                        requested=True,
                        target_value=up_int,
                        classification="control_plane_verifiable",
                        reason="Upload bandwidth can be applied and verified on the emulator control plane, but data-plane throughput is unverified without active probe",
                        mechanism="adb emu network speed <up>:<down> with emu network status readback verification",
                        parameters={"up_kbps": up_int},
                    )
                )
            else:
                conditions.append(
                    PlannedCondition(
                        name="upload_bandwidth",
                        requested=True,
                        target_value=up_int,
                        classification="unsupported",
                        reason="Target is not an Android Emulator serial",
                    )
                )
        except (ValueError, TypeError):
            conditions.append(
                PlannedCondition(
                    name="upload_bandwidth",
                    requested=True,
                    target_value=up_val,
                    classification="unsupported",
                    reason="Invalid up_kbps value in persona profile",
                )
            )
    else:
        conditions.append(
            PlannedCondition(
                name="upload_bandwidth",
                requested=False,
                target_value=None,
                classification="not_requested",
                reason="Upload bandwidth not specified in persona profile",
            )
        )

    # 4. Packet loss
    loss_val = profile.get("packet_loss_pct")
    if loss_val is not None:
        try:
            loss_float = float(loss_val)
            if loss_float > 0:
                conditions.append(
                    PlannedCondition(
                        name="packet_loss",
                        requested=True,
                        target_value=loss_float,
                        classification="unsupported",
                        reason="Android emulator console does not support packet loss simulation",
                    )
                )
            else:
                conditions.append(
                    PlannedCondition(
                        name="packet_loss",
                        requested=False,
                        target_value=0.0,
                        classification="not_requested",
                        reason="Zero packet loss requested (no shaping needed)",
                    )
                )
        except (ValueError, TypeError):
            conditions.append(
                PlannedCondition(
                    name="packet_loss",
                    requested=True,
                    target_value=loss_val,
                    classification="unsupported",
                    reason="Invalid packet_loss_pct value in persona profile",
                )
            )
    else:
        conditions.append(
            PlannedCondition(
                name="packet_loss",
                requested=False,
                target_value=0.0,
                classification="not_requested",
                reason="Packet loss not specified in persona profile",
            )
        )

    # 5. Battery saver
    battery_saver_val = profile.get("battery_saver")
    if battery_saver_val is True:
        if is_emu:
            conditions.append(
                PlannedCondition(
                    name="battery_saver",
                    requested=True,
                    target_value=True,
                    classification="supported",
                    reason="Android emulator supports low_power mode when simulated as unplugged",
                    mechanism="adb shell cmd battery unplug and settings put global low_power 1 with dumpsys battery and settings get readback",
                )
            )
        else:
            conditions.append(
                PlannedCondition(
                    name="battery_saver",
                    requested=True,
                    target_value=True,
                    classification="unsupported",
                    reason="Target is not an Android Emulator serial; battery saver simulation is restricted to disposable emulator targets",
                )
            )
    else:
        conditions.append(
            PlannedCondition(
                name="battery_saver",
                requested=False,
                target_value=False,
                classification="not_requested",
                reason="Battery saver mode not requested in persona profile",
            )
        )

    # 6. Storage pressure
    storage_val = profile.get("storage_free_mb")
    if storage_val is not None:
        try:
            storage_int = int(storage_val)
            if storage_int > 0:
                if is_emu:
                    conditions.append(
                        PlannedCondition(
                            name="storage_pressure",
                            requested=True,
                            target_value=storage_int,
                            classification="supported",
                            reason="Disposable emulator supports safe bounded temporary file allocation in /data/local/tmp",
                            mechanism="bounded temporary file allocation in /data/local/tmp with safety reserve check and verified removal",
                            parameters={
                                "target_free_mb": storage_int,
                                "safety_reserve_mb": 100,
                                "max_allocation_mb": 2048,
                                "temp_file_path": "/data/local/tmp/bharatsim_storage_pressure.tmp",
                            },
                        )
                    )
                else:
                    conditions.append(
                        PlannedCondition(
                            name="storage_pressure",
                            requested=True,
                            target_value=storage_int,
                            classification="unsupported",
                            reason="Target is not an Android Emulator serial; storage pressure simulation is restricted to disposable emulator targets",
                        )
                    )
            else:
                conditions.append(
                    PlannedCondition(
                        name="storage_pressure",
                        requested=False,
                        target_value=storage_int,
                        classification="not_requested",
                        reason="Zero or negative storage target provided",
                    )
                )
        except (ValueError, TypeError):
            conditions.append(
                PlannedCondition(
                    name="storage_pressure",
                    requested=True,
                    target_value=storage_val,
                    classification="unsupported",
                    reason="Invalid storage_free_mb value in persona profile",
                )
            )
    else:
        conditions.append(
            PlannedCondition(
                name="storage_pressure",
                requested=False,
                target_value=None,
                classification="not_requested",
                reason="Storage free budget not specified in persona profile",
            )
        )

    # 7. RAM constraint
    ram_val = profile.get("ram_mb")
    if ram_val is not None:
        try:
            ram_int = int(ram_val)
            conditions.append(
                PlannedCondition(
                    name="ram_constraint",
                    requested=True,
                    target_value=ram_int,
                    classification="report_only",
                    reason="Dynamic RAM restriction is not supported by Android runtime; actual device memory will be reported from /proc/meminfo for comparison",
                    mechanism="adb shell cat /proc/meminfo readback",
                    parameters={"target_ram_mb": ram_int},
                )
            )
        except (ValueError, TypeError):
            conditions.append(
                PlannedCondition(
                    name="ram_constraint",
                    requested=True,
                    target_value=ram_val,
                    classification="unsupported",
                    reason="Invalid ram_mb value in persona profile",
                )
            )
    else:
        conditions.append(
            PlannedCondition(
                name="ram_constraint",
                requested=False,
                target_value=None,
                classification="not_requested",
                reason="RAM target not specified in persona profile",
            )
        )

    # 8. CPU constraint
    conditions.append(
        PlannedCondition(
            name="cpu_constraint",
            requested=False,
            target_value=None,
            classification="unsupported",
            reason="Persona does not define CPU constraints and no safe, reproducible CPU throttling mechanism exists for the emulator",
        )
    )

    return ConditionPlan(
        persona_id=persona_id,
        target_serial=serial,
        is_emulator=is_emu,
        conditions=conditions,
    )
