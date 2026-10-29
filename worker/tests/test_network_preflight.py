import unittest

from worker.tests.appium_smoke_journey import has_supported_active_transport


class ActiveAndroidTransportTests(unittest.TestCase):
    def test_accepts_active_cellular_network(self):
        self.assertTrue(has_supported_active_transport(
            "Cellular active networks: {100}\nWiFi active networks: {}"
        ))

    def test_accepts_active_ethernet_network(self):
        self.assertTrue(has_supported_active_transport(
            "Ethernet active networks: {101}\nWiFi active networks: {}"
        ))

    def test_rejects_empty_supported_networks(self):
        self.assertFalse(has_supported_active_transport(
            "Cellular active networks: {}\nEthernet active networks: {}\nWiFi active networks: {100}"
        ))

    def test_rejects_wifi_only(self):
        self.assertFalse(has_supported_active_transport(
            "WiFi active networks: {100}\nCellular active networks: {}\nEthernet active networks: {}"
        ))


if __name__ == "__main__":
    unittest.main()
