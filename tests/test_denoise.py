import mock
import os
import pytest
from unittest import TestCase
from unittest import TestLoader
from tests.utilities import *
from emop.lib.processes.denoise import Denoise


class TestDenoise(TestCase):
    def setUp(self):
        self.popen_patcher = mock.patch("emop.lib.utilities.subprocess32.Popen")
        self.mock_popen = self.popen_patcher.start()
        self.mock_rv = mock.Mock()
        self.mock_rv.communicate.return_value = ["", ""]
        self.mock_rv.returncode = 0
        self.mock_popen.return_value = self.mock_rv

    def tearDown(self):
        self.popen_patcher.stop()

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
        self.mock_rv.communicate.return_value[0] = "NOISEMEASURE: 1.0"

        retval = denoise.run()
        args, kwargs = self.mock_popen.call_args

        self.assertTrue(mock_path_isfile.called)
        self.assertTrue(self.mock_popen.called)
        self.assertEqual(expected_cmd, args[0])
        self.assertEqual(job.postproc_result.pp_noisemsr, "1.0")
        self.assertTupleEqual(expected_results, retval)

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
