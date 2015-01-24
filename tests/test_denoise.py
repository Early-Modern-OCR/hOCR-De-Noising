import mock
import os
import pytest
from unittest import TestCase
from unittest import TestLoader
from tests.utilities import *
from emop.lib.processes.denoise import Denoise


class TestDenoise(TestCase):
    @mock.patch("emop.lib.processes.denoise.os.path.isfile")
    def test_run(self, mock_path_isfile):
        settings = default_settings()
        settings.denoise_home = "/foo/lib/denoise"
        job = mock_emop_job(settings)
        denoise = Denoise(job)

        mock_path_isfile.return_value = True

        expected_cmd = [
            "python", "/foo/lib/denoise/deNoise_Post.py",
            "-p", denoise.xml_file_dir, "-n", denoise.xml_filename
        ]
        results = mock_results_tuple()
        expected_results = results(None, None, 0)
        exec_cmd = mock_exec_cmd(stdout="NOISEMEASURE: 1.0", stderr=None, exitcode=0)

        retval = denoise.run()
        args, kwargs = exec_cmd.call_args

        self.assertTrue(mock_path_isfile.called)
        self.assertTrue(exec_cmd.called)
        self.assertEqual(expected_cmd, args[0])
        self.assertEqual(job.postproc_result.pp_noisemsr, "1.0")
        self.assertTupleEqual(expected_results, retval)
        exec_cmd.stop()

    def test_should_run_false(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.postproc_result.pp_noisemsr_exists = True
        denoise = Denoise(job)

        self.assertFalse(denoise.should_run())

    def test_should_run_true(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.postproc_result.pp_noisemsr_exists = False
        denoise = Denoise(job)

        self.assertTrue(denoise.should_run())


def suite():
    return TestLoader().loadTestsFromTestCase(TestDenoise)
