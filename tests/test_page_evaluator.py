import mock
import os
import pytest
from unittest import TestCase
from unittest import TestLoader
from tests.utilities import *
from emop.lib.processes.page_evaluator import PageEvaluator


class TestPageEvaluator(TestCase):
    def setUp(self):
        self.popen_patcher = mock.patch("emop.lib.utilities.subprocess.Popen")
        self.mock_popen = self.popen_patcher.start()
        self.mock_rv = mock.Mock()
        self.mock_rv.communicate.return_value = ["", ""]
        self.mock_rv.returncode = 0
        self.mock_popen.return_value = self.mock_rv

    def tearDown(self):
        self.popen_patcher.stop()

    @mock.patch("emop.lib.processes.page_evaluator.os.path.isfile")
    def test_run(self, mock_path_isfile):
        settings = default_settings()
        settings.seasr_home = "/foo/lib/seasr"
        job = mock_emop_job(settings)
        page_evaluator = PageEvaluator(job)

        mock_path_isfile.return_value = True

        expected_cmd = [
            "java", "-Xms128M", "-Xmx128M", "-jar", "/foo/lib/seasr/PageEvaluator.jar",
            "-q", job.xml_file
        ]
        results = mock_results_tuple()
        expected_results = results(None, None, 0)
        self.mock_rv.communicate.return_value[0] = "0.05,0.1"

        retval = page_evaluator.run()
        args, kwargs = self.mock_popen.call_args

        print args
        self.assertTrue(mock_path_isfile.called)
        self.assertTrue(self.mock_popen.called)
        self.assertEqual(expected_cmd, args[0])
        self.assertEqual(job.postproc_result.pp_ecorr, "0.05")
        self.assertEqual(job.postproc_result.pp_pg_quality, "0.1")
        self.assertTupleEqual(expected_results, retval)

    def test_should_run_false(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.postproc_result.pp_ecorr_exists = True
        job.postproc_result.pp_pg_quality_exists = True
        page_evaluator = PageEvaluator(job)

        self.assertFalse(page_evaluator.should_run())

    def test_should_run_true_if_pp_ecorr_missing(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.postproc_result.pp_ecorr_exists = False
        job.postproc_result.pp_pg_quality_exists = True
        page_evaluator = PageEvaluator(job)

        self.assertTrue(page_evaluator.should_run())

    def test_should_run_true_if_pp_pg_quality_missing(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.postproc_result.pp_ecorr_exists = True
        job.postproc_result.pp_pg_quality_exists = False
        page_evaluator = PageEvaluator(job)

        self.assertTrue(page_evaluator.should_run())

    def test_should_run_true_if_all_values_missing(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.postproc_result.pp_ecorr_exists = False
        job.postproc_result.pp_pg_quality_exists = False
        page_evaluator = PageEvaluator(job)

        self.assertTrue(page_evaluator.should_run())


def suite():
    return TestLoader().loadTestsFromTestCase(TestPageEvaluator)
