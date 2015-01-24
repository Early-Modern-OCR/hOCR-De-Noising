import mock
import os
import pytest
from unittest import TestCase
from unittest import TestLoader
from tests.utilities import *
from emop.lib.processes.retas_compare import RetasCompare


class TestRetasCompare(TestCase):
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
        exec_cmd = mock_exec_cmd(stdout="0.01", stderr=None, exitcode=0)

        retval = retas_compare.run(postproc=True)
        args, kwargs = exec_cmd.call_args

        self.maxDiff = None
        self.assertTrue(mock_path_isfile.called)
        self.assertTrue(exec_cmd.called)
        self.assertEqual(expected_cmd, args[0])
        self.assertEqual(job.page_result.alt_change_index, 0.01)
        self.assertTupleEqual(expected_results, retval)
        exec_cmd.stop()

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
