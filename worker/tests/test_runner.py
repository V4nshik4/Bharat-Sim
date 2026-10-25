import unittest

from worker.runner import valid_package_name


class PackageNameValidationTests(unittest.TestCase):
    def test_accepts_android_style_package_names(self):
        for value in ("com.example.app", "org.example_2.client", "a.b", "com.Example.App"):
            with self.subTest(value=value):
                self.assertTrue(valid_package_name(value))

    def test_rejects_shell_metacharacters_and_malformed_names(self):
        for value in (
            "com.example;id",
            "com.example$(id)",
            "com.example && reboot",
            "com.example app",
            "com",
            ".example.app",
            "com..app",
            "com.example/",
            "",
        ):
            with self.subTest(value=value):
                self.assertFalse(valid_package_name(value))


if __name__ == "__main__":
    unittest.main()
