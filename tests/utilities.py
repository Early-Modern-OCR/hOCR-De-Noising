import os
from emop.lib.emop_settings import EmopSettings

def default_config_path():
    test_root = os.path.dirname(__file__)
    app_root = os.path.abspath(os.path.join(test_root, '..'))
    config_path = os.path.join(app_root, 'config.ini.example')
    return config_path

def default_settings():
    settings = EmopSettings(default_config_path())
    return settings
