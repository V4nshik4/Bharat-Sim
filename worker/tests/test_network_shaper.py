import unittest

from worker.network_shaper import IFACE_RE


class NetworkShaperGuardTests(unittest.TestCase):
    def test_accepts_dedicated_test_veth_names(self):
        self.assertTrue(IFACE_RE.fullmatch("veth-bs-run01"))
        self.assertTrue(IFACE_RE.fullmatch("veth-bs-a"))

    def test_rejects_host_and_arbitrary_interfaces(self):
        for interface in ("eth0", "wlan0", "lo", "docker0", "veth0", "veth-bs-"):
            with self.subTest(interface=interface):
                self.assertFalse(IFACE_RE.fullmatch(interface))


if __name__ == "__main__":
    unittest.main()
