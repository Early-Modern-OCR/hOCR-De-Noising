import os
from emop.lib.emop_settings import EmopSettings


def default_settings():
    test_root = os.path.dirname(__file__)
    app_root = os.path.abspath(os.path.join(test_root, '..'))
    config_path = os.path.join(app_root, 'config.ini.example')
    settings = EmopSettings(config_path)
    return settings
