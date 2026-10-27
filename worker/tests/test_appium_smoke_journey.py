from unittest.mock import patch

import pytest

from worker.tests import appium_smoke_journey as journey


def test_cellular_preflight_requires_active_cellular_route():
    commands = [
        "", "", "", "", "", "",  # airplane/mobile data, service, GSM, Wi-Fi setup
        "default via 10.0.2.2 dev rmnet_data0",
        "Active default network: CELLULAR; NET_CAPABILITY_INTERNET",
        "gsm voice state: home\ngsm data state: home",
    ]
    with patch.object(journey, "adb", side_effect=commands) as adb_call, patch.object(journey.time, "sleep"):
        journey.prepare_cellular_transport()
    assert adb_call.call_count == 9


def test_cellular_preflight_fails_with_diagnostics_when_no_route_exists():
    commands = [
        "", "", "", "", "", "",  # setup commands
        "", "No active default network", "gsm voice state: home\ngsm data state: home",
    ]
    with (
        patch.object(journey, "adb", side_effect=commands),
        patch.object(journey.time, "sleep"),
        patch.object(journey.time, "monotonic", side_effect=[0, *range(0, 23)]),
    ):
        with pytest.raises(RuntimeError, match="no verified cellular default route") as error:
            journey.prepare_cellular_transport()
    assert "route=" in str(error.value)
    assert "connectivity=" in str(error.value)
