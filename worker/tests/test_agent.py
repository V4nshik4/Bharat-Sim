import unittest
import urllib.request

from worker.agent import NoRedirectHandler


class WorkerRedirectSecurityTests(unittest.TestCase):
    def test_credential_bearing_requests_are_not_redirected(self):
        handler = NoRedirectHandler()
        request = urllib.request.Request("https://bharatsim.example/internal/worker/claim")
        redirected = handler.redirect_request(
            request, None, 302, "Found", {"Location": "https://attacker.example/steal"}, 
            "https://attacker.example/steal",
        )
        self.assertIsNone(redirected)


if __name__ == "__main__":
    unittest.main()
