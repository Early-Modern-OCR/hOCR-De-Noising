import os
from unittest import TestCase
from unittest import TestLoader
from tests.utilities import default_settings, mock_exec_cmd
from emop.lib.schedulers.emop_slurm import EmopSLURM


class TestEmopSLURM(TestCase):
    def setUp(self):
        self.settings = default_settings()
        self.settings.avg_page_runtime = 60
        self.settings.max_job_runtime = 3600
        self.settings.scheduler_logfile = "/dne/log.out"

    def clear_job_id_env(self):
        if os.environ.get("SLURM_JOB_ID"):
            del os.environ["SLURM_JOB_ID"]

    def test_current_job_count(self):
        scheduler = EmopSLURM(self.settings)
        expected_cmd = [
            "squeue", "-r", "--noheader", "-p", "idhmc", "-n", "emop-controller"
        ]
        mock_stdout = ("       0001                 idhmc emop-controller treydock  R    0:01:00      1 c0101\n"
                       "       0002                 idhmc emop-controller treydock  R    0:01:00      1 c0102\n")
        exec_cmd = mock_exec_cmd(stdout=mock_stdout, stderr=None, exitcode=0)
        retval = scheduler.current_job_count()
        args, kwargs = exec_cmd.call_args
        self.assertTrue(exec_cmd.called)
        self.assertEqual(expected_cmd, args[0])
        self.assertEqual(retval, 2)

    def test_submit_job(self):
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
        exec_cmd = mock_exec_cmd(stdout="1", stderr=None, exitcode=0)
        retval = scheduler.submit_job('0001', '1')
        args, kwargs = exec_cmd.call_args
        PROC_ID = os.environ.get('PROC_ID')
        EMOP_CONFIG_PATH = os.environ.get('EMOP_CONFIG_PATH')
        self.assertTrue(exec_cmd.called)
        self.assertEqual(expected_cmd, args[0])
        self.assertEqual(PROC_ID, '0001')
        self.assertEqual(EMOP_CONFIG_PATH, self.settings.config_path)
        self.assertTrue(retval)

    def test_submit_job_failed(self):
        scheduler = EmopSLURM(self.settings)
        exec_cmd = mock_exec_cmd(stdout="1", stderr=None, exitcode=1)
        retval = scheduler.submit_job('0001', '1')
        self.assertFalse(retval)

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

    # Tests below are for functions inherited from EmopScheduler

    def test_is_job_environment_true(self):
        scheduler = EmopSLURM(self.settings)
        os.environ["SLURM_JOB_ID"] = '0001'
        retval = scheduler.is_job_environment()
        self.assertTrue(retval)

    def test_is_job_environment_false(self):
        scheduler = EmopSLURM(self.settings)
        self.clear_job_id_env()
        retval = scheduler.is_job_environment()
        self.assertFalse(retval)

    def test_get_name(self):
        scheduler = EmopSLURM(self.settings)
        self.assertEqual("SLURM", scheduler.get_name())

    def test_get_job_id_not_set(self):
        scheduler = EmopSLURM(self.settings)
        self.clear_job_id_env()
        actual = scheduler.get_job_id()
        self.assertEqual(None, actual)

    def test_get_job_id(self):
        scheduler = EmopSLURM(self.settings)
        os.environ["SLURM_JOB_ID"] = '0001'
        actual = scheduler.get_job_id()
        self.assertEqual('0001', actual)


def suite():
    return TestLoader().loadTestsFromTestCase(TestEmopSLURM)
