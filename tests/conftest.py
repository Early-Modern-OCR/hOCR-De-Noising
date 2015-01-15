import pytest
import os


@pytest.fixture(scope="session", autouse=True)
def setup_env_vars():
    test_root = os.path.dirname(__file__)
    app_root = os.path.abspath(os.path.join(test_root, '..'))
    os.environ['DENOISE_HOME'] = os.path.join(app_root, 'lib/denoise')
    os.environ['SEASR_HOME'] = os.path.join(app_root, 'lib/seasr')
    os.environ['JUXTA_HOME'] = os.path.join(app_root, 'lib/juxta-cl')
    os.environ['RETAS_HOME'] = os.path.join(app_root, 'lib/retas')
