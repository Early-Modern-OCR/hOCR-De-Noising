import mock
import os
from emop.lib.emop_settings import EmopSettings
from emop.lib.utilities import exec_cmd

def default_config_path():
    test_root = os.path.dirname(__file__)
    app_root = os.path.abspath(os.path.join(test_root, '..'))
    config_path = os.path.join(app_root, 'config.ini.example')
    return config_path

def default_settings():
    settings = EmopSettings(default_config_path())
    return settings

def mock_exec_cmd(stdout, stderr, exitcode):
    popen_patcher = mock.patch("emop.lib.utilities.subprocess.Popen")
    mock_popen = popen_patcher.start()
    mock_rv = mock.Mock()
    mock_rv.communicate.return_value = [stdout, stderr]
    mock_rv.returncode = exitcode
    mock_popen.return_value = mock_rv
    return mock_popen
