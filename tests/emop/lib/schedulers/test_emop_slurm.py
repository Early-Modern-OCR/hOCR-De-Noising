from unittest import TestCase
from unittest import TestLoader
from tests.utilities import default_settings
from emop.lib.emop_base import EmopBase
from emop.lib.schedulers.emop_slurm import EmopSLURM


class TestEmopSLURM(TestCase):
    def setUp(self):
        self.settings = default_settings()
        self.settings.avg_page_runtime = 60
        self.settings.max_job_runtime = 3600
        self.settings.scheduler_logfile = "/dne/log.out"

#    def test_sets_env_proc_id(self):
#        scheduler = EmopSLURM(self.settings)
#        scheduler.submit_job('0001', '1')
#        PROC_ID = os.environ.get('PROC_ID')
#        self.assertEqual(PROC_ID, '0001')

#    def test_sets_env_emop_config_path(self):
#        scheduler = EmopSLURM(self.settings)
#        scheduler.submit_job('0001', '1')
#        EMOP_CONFIG_PATH = os.environ.get('EMOP_CONFIG_PATH')
#        self.assertEqual(EMOP_CONFIG_PATH, self.settings.config_path)

    def test_get_submit_cmd(self):
        scheduler = EmopSLURM(self.settings)
        expected_cmd = [
            "sbatch", "--parsable",
            "-p", "idhmc",
            "-J", "emop-controller",
            "-o", "/dne/log.out",
            "--mem-per-cpu", "4000",
            "--cpus-per-task", "1",
            "emop.slrm"
        ]
        actual_cmd = scheduler.get_submit_cmd('1')
        self.assertEqual(expected_cmd, actual_cmd)

    def test_get_submit_cmd_walltime(self):
        self.settings.scheduler_set_walltime = True
        scheduler = EmopSLURM(self.settings)
        expected_cmd = [
            "sbatch", "--parsable",
            "-p", "idhmc",
            "-J", "emop-controller",
            "-o", "/dne/log.out",
            "--mem-per-cpu", "4000",
            "--cpus-per-task", "1",
            "--time", "4",
            "emop.slrm"
        ]
        actual_cmd = scheduler.get_submit_cmd('1')
        self.assertEqual(expected_cmd, actual_cmd)

    def test_get_submit_cmd_extra_args(self):
        self.settings.scheduler_extra_args = ['--account', 'foo']
        scheduler = EmopSLURM(self.settings)
        expected_cmd = [
            "sbatch", "--parsable",
            "-p", "idhmc",
            "-J", "emop-controller",
            "-o", "/dne/log.out",
            "--mem-per-cpu", "4000",
            "--cpus-per-task", "1",
            ["--account", "foo"],
            "emop.slrm"
        ]
        actual_cmd = scheduler.get_submit_cmd('1')
        self.assertEqual(expected_cmd, actual_cmd)

    def test_options(self):
        self.assertEqual(self.settings.avg_page_runtime, 60)
        self.assertEqual(self.settings.max_job_runtime, 3600)

    def test_walltime_max_runtime(self):
        scheduler = EmopSLURM(self.settings)
        walltime = scheduler.walltime(61)
        self.assertEqual(walltime, 3600)

    def test_walltime_400pct_1(self):
        scheduler = EmopSLURM(self.settings)
        walltime = scheduler.walltime(15)
        self.assertEqual(walltime, 3600)

    def test_walltime_400pct_2(self):
        scheduler = EmopSLURM(self.settings)
        walltime = scheduler.walltime(14)
        self.assertEqual(walltime, 3360)

    def test_walltime_200pct_1(self):
        scheduler = EmopSLURM(self.settings)
        walltime = scheduler.walltime(30)
        self.assertEqual(walltime, 3600)

    def test_walltime_200pct_2(self):
        scheduler = EmopSLURM(self.settings)
        walltime = scheduler.walltime(29)
        self.assertEqual(walltime, 3480)

    def test_walltime_150pct_1(self):
        scheduler = EmopSLURM(self.settings)
        walltime = scheduler.walltime(40)
        self.assertEqual(walltime, 3600)

    def test_walltime_150pct_2(self):
        scheduler = EmopSLURM(self.settings)
        walltime = scheduler.walltime(39)
        self.assertEqual(walltime, 3510)


def suite():
    return TestLoader().loadTestsFromTestCase(EmopSLURMTest)
