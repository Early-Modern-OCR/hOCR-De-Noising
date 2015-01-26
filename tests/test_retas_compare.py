import mock
import os
import pytest
from unittest import TestCase
from unittest import TestLoader
from tests.utilities import *
from emop.lib.processes.retas_compare import RetasCompare


class TestRetasCompare(TestCase):
    def setUp(self):
        self.popen_patcher = mock.patch("emop.lib.utilities.subprocess.Popen")
        self.mock_popen = self.popen_patcher.start()
        self.mock_rv = mock.Mock()
        self.mock_rv.communicate.return_value = ["", ""]
        self.mock_rv.returncode = 0
        self.mock_popen.return_value = self.mock_rv

    def tearDown(self):
        self.popen_patcher.stop()

    @mock.patch("emop.lib.processes.page_corrector.os.path.isfile")
    def test_run(self, mock_path_isfile):
        settings = default_settings()
        settings.retas_home = "/foo/lib/retas"
        job = mock_emop_job(settings)
        job.page.ground_truth_file = "/dne/gt.txt"
        retas_compare = RetasCompare(job)

        mock_path_isfile.return_value = True

        expected_cmd = [
            "java", "-Xms128M", "-Xmx128M", "-jar", "/foo/lib/retas/retas.jar",
            "/dh/dne/gt.txt", job.alto_txt_file,
            "-opt", "/foo/lib/retas/config.txt"
        ]
        results = mock_results_tuple()
        expected_results = results(None, None, 0)
        self.mock_rv.communicate.return_value[0] = "0.01"

        retval = retas_compare.run(postproc=True)
        args, kwargs = self.mock_popen.call_args

        self.maxDiff = None
        self.assertTrue(mock_path_isfile.called)
        self.assertTrue(self.mock_popen.called)
        self.assertEqual(expected_cmd, args[0])
        self.assertEqual(job.page_result.alt_change_index, 0.01)
        self.assertTupleEqual(expected_results, retval)

    def test_should_run_false(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.page_result.alt_change_index_exists = True
        retas_compare = RetasCompare(job)

        self.assertFalse(retas_compare.should_run())

    def test_should_run_true(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.page_result.alt_change_index_exists = False
        retas_compare = RetasCompare(job)

        self.assertTrue(retas_compare.should_run())


def suite():
    return TestLoader().loadTestsFromTestCase(TestRetasCompare)
