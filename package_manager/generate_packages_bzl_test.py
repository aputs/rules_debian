import unittest
import os
import json

from package_manager.generate_packages_bzl import resolve_packages


class TestGeneratePackagesBzl(unittest.TestCase):
    def setUp(self):
        current_dir = os.path.dirname(__file__)
        self.filename = os.path.join(current_dir, "testdata", "Packages.json")

    def test_resolve_packages(self):
        resolved = resolve_packages("test_bundle", [self.filename])
        self.assertIn("newmail", resolved)


if __name__ == "__main__":

    unittest.main()
