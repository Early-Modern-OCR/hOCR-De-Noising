import os
from unittest import TestCase
from unittest import TestLoader
from emop.lib.utilities import get_temp_dir


class TestUtilities(TestCase):
    def setUp(self):
        pass

    def test_get_temp_dir_none(self):
        if os.environ.get("TMPDIR"):
            del os.environ["TMPDIR"]
        self.assertEqual(get_temp_dir(), None)

    def test_get_temp_dir_exists(self):
        os.environ["TMPDIR"] = "/dne"
        self.assertEqual(get_temp_dir(), "/dne")


def suite():
    return TestLoader().loadTestsFromTestCase(TestUtilities)
