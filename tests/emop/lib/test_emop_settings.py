import os
from unittest import TestCase
from unittest import TestLoader
from emop.lib.emop_settings import EmopSettings


class TestEmopSettings(TestCase):
    def setUp(self):
        app_root = os.path.abspath(os.path.join(__file__, '../../../..'))
        config_path = os.path.join(app_root, 'config.ini.example')
        self.settings = EmopSettings(config_path)

    def test_config_path(self):
        config_file = 'config.ini.example'
        assert os.path.basename(self.settings.config_path) == config_file

#    def test_emop_home(self):
#        emop_home_orig = None
#        if os.environ.get("EMOP_HOME"):
#            emop_home_orig = os.environ["EMOP_HOME"]
#            del os.environ["EMOP_HOME"]


def suite():
    return TestLoader().loadTestsFromTestCase(EmopSettingsTest)
