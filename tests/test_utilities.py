import os
from unittest import TestCase
from unittest import TestLoader
from emop.lib.utilities import get_temp_dir


class TestUtilities(TestCase):
    def setUp(self):
        pass

    def test_get_temp_dir(self):
        self.assertEqual(get_temp_dir(), None)
        os.environ["TMPDIR"] = "/dne"
        self.assertEqual(get_temp_dir(), "/dne")

def suite():
    return TestLoader().loadTestsFromTestCase(TestUtilities)
