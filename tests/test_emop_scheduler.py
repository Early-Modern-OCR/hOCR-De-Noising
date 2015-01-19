from unittest import TestCase
from unittest import TestLoader
from tests.utilities import default_settings
from emop.lib.emop_scheduler import EmopScheduler
from emop.lib.schedulers.emop_slurm import EmopSLURM


class TestEmopScheduler(TestCase):
    def setUp(self):
        self.settings = default_settings()

    def test_get_scheduler_instance_slurm(self):
        self.settings.scheduler = "slurm"
        scheduler = EmopScheduler.get_scheduler_instance(name="slurm", settings=self.settings)
        assert isinstance(scheduler, EmopSLURM), "scheduler is not an instance of EmopSLURM"


def suite():
    return TestLoader().loadTestsFromTestCase(TestEmopScheduler)
