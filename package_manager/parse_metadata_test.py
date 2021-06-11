import unittest
import os

from package_manager.parse_metadata import parse_package_metadata, opengzfile


class TestParseMetadata(unittest.TestCase):
    def setUp(self):
        current_dir = os.path.dirname(__file__)
        self.filename = os.path.join(current_dir, "testdata", "Packages.txt")
        self.gzfilename = os.path.join(current_dir, "testdata", "Packages.gz")
        self.mirror_url = "http://debian.org"
        self.package_prefix = "http://dummy/prefix/"
        with open(self.filename, "rb") as f:
            self.debian_repo_metadata = self.repo_data(
                parse_package_metadata(f, self.mirror_url, "20170701", "")
            )
        with open(self.filename, "rb") as f:
            self.arbitrary_repo_metadata = self.repo_data(
                parse_package_metadata(f, "", "", self.package_prefix)
            )

    def repo_data(self, entries):
        data = {}
        for entry in entries:
            data[entry["package"]] = entry
        return data

    def test_open_missingfile(self):
        with self.assertRaises(FileNotFoundError):
            with opengzfile("fasf") as f:
                f.read()

    def test_read_gzippedfile(self):
        with opengzfile(self.gzfilename, "rb") as f:
            assert next(parse_package_metadata(f, self.mirror_url, "20170701", ""))

    def test_read_textfile(self):
        with opengzfile(self.filename, "rb") as f:
            assert next(parse_package_metadata(f, self.mirror_url, "20170701", ""))

    def test_debian_repo_url_rewrite(self):
        """Relative url should have gotten rewritten with absolute url"""

        self.assertEqual(
            self.debian_repo_metadata["libnewlib-dev"]["filename"],
            self.mirror_url
            + "/debian/20170701/"
            + "pool/main/n/newlib/libnewlib-dev_2.1.0+git20140818.1a8323b-2_all.deb",
        )

    def test_arbitrary_repo_url_rewrite(self):
        """Relative url should have gotten rewritten with absolute url using the given package prefix"""
        self.assertEqual(
            self.arbitrary_repo_metadata["libnewlib-dev"]["filename"],
            self.package_prefix
            + "pool/main/n/newlib/libnewlib-dev_2.1.0+git20140818.1a8323b-2_all.deb",
        )

    def test_get_all_packages(self):
        """Parser should identify all packages"""
        expected_packages = [
            "libnewlib-dev",
            "libnewlib-doc",
            "newlib-source",
            "newmail",
            "zzuf",
        ]
        self.assertEqual(
            expected_packages.sort(), list(self.debian_repo_metadata.keys()).sort()
        )

    def test_multiline_key(self):
        """Multiline keys should be properly parsed"""
        expected_tags = "interface::commandline, mail::notification, role::program,scope::utility, works-with::mail"
        self.assertEqual(expected_tags, self.debian_repo_metadata["newmail"]["tag"])


if __name__ == "__main__":

    unittest.main()
