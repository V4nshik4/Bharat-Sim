import unittest
from unittest.mock import patch

from worker.tests import appium_smoke_journey as journey


class SupportedRoutePreflightTests(unittest.TestCase):
    def test_preflight_requires_a_default_route(self):
        commands = [
            "", "", "", "", "", "",  # airplane/mobile data, service, GSM, Wi-Fi setup
            "default via 10.0.2.2 dev rmnet_data0",
            "Active default network: CELLULAR; NET_CAPABILITY_INTERNET",
            "gsm voice state: home\ngsm data state: home",
        ]
        with patch.object(journey, "adb", side_effect=commands) as adb_call, patch.object(journey.time, "sleep"):
            journey.prepare_supported_transport()
        self.assertEqual(adb_call.call_count, 9)

    def test_preflight_fails_with_diagnostics_when_no_route_exists(self):
        commands = [
            "", "", "", "", "", "",  # setup commands
            "", "No active default network", "gsm voice state: home\ngsm data state: home",
        ]
        with (
            patch.object(journey, "adb", side_effect=commands),
            patch.object(journey.time, "sleep"),
            patch.object(journey.time, "monotonic", side_effect=[0, *range(0, 23)]),
        ):
            with self.assertRaisesRegex(RuntimeError, "no verified cellular/Ethernet default route") as error:
                journey.prepare_supported_transport()
        self.assertIn("route=", str(error.exception))
        self.assertIn("connectivity=", str(error.exception))


if __name__ == "__main__":
    unittest.main()
