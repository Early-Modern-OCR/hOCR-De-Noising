import collections
import mock
import os
from emop.lib.emop_settings import EmopSettings
from emop.lib.emop_job import EmopJob
from emop.lib.emop_scheduler import EmopScheduler
from emop.lib.models.emop_batch_job import EmopBatchJob
from emop.lib.models.emop_font import EmopFont
from emop.lib.models.emop_page import EmopPage
from emop.lib.models.emop_work import EmopWork


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


def mock_scheduler_slurm():
    settings = default_settings()
    scheduler = EmopScheduler.get_scheduler_instance(name="slurm", settings=settings)
    return scheduler


def mock_batch_job():
    settings = default_settings()
    batch_job = EmopBatchJob(settings=settings)
    batch_job.id = 1
    batch_job.name = 'TEST Batch Job'
    batch_job.notes = ""
    batch_job.parameters = ""
    batch_job.job_type = "ocr"
    batch_job.ocr_engine = "tesseract"
    return batch_job


def mock_font():
    settings = default_settings()
    font = EmopFont(settings=settings)
    font.name = "TEST Font"
    return font


def mock_page():
    settings = default_settings()
    page = EmopPage(settings=settings)
    page.id = 1
    page.number = 1
    page.image_path = '/dne/image.tiff'
    page.gale_ocr_file = None
    page.ground_truth_file = None
    return page


def mock_work():
    settings = default_settings()
    work = EmopWork(settings=settings)
    work.id = 1
    work.organizational_unit = 1
    work.title = "TEST Work Title"
    work.ecco_id = None
    work.ecco_directory = None
    work.eebo_id = "1"
    work.eebo_directory = "/dne/work/1"
    return work


def mock_emop_job(settings=None):
    if not settings:
        settings = default_settings()
    batch_job = mock_batch_job()
    font = mock_font()
    page = mock_page()
    work = mock_work()
    scheduler = mock_scheduler_slurm()
    job = EmopJob(1, batch_job, font, page, work, settings, scheduler)
    return job


def mock_results_tuple():
    results = collections.namedtuple('Results', ['stdout', 'stderr', 'exitcode'])
    return results
