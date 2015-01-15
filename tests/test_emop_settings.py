import os
import pytest
from unittest import TestCase
from unittest import TestLoader
from tests.utilities import default_settings


class TestEmopSettings(TestCase):
    def setUp(self):
        self.settings = default_settings()

    def test_config_path(self):
        config_file = 'config.ini.example'
        assert os.path.basename(self.settings.config_path) == config_file

#    def test_emop_home(self):
#        emop_home_orig = None
#        if os.environ.get("EMOP_HOME"):
#            emop_home_orig = os.environ["EMOP_HOME"]
#            del os.environ["EMOP_HOME"]


def suite():
    return TestLoader().loadTestsFromTestCase(TestEmopSettings)
