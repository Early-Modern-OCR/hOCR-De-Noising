from flexmock import flexmock
import mock
import os
import pytest
from unittest import TestCase
from unittest import TestLoader
from tests.utilities import *
from emop.lib.processes.multi_column_skew import MultiColumnSkew


class TestMultiColumnSkew(TestCase):
    def setUp(self):
        self.popen_patcher = mock.patch("emop.lib.utilities.subprocess.Popen")
        self.mock_popen = self.popen_patcher.start()
        self.mock_rv = mock.Mock()
        self.mock_rv.communicate.return_value = ["", ""]
        self.mock_rv.returncode = 0
        self.mock_popen.return_value = self.mock_rv

    def tearDown(self):
        self.popen_patcher.stop()

    def test_run(self):
        settings = default_settings()
        settings.emop_home = "/foo"
        job = mock_emop_job(settings)
        multi_column_skew = MultiColumnSkew(job)

        flexmock(os.path).should_receive("isfile").with_args(job.idhmc_xml_file).and_return(True)

        expected_cmd = [
            "python", "/foo/lib/MultiColumnSkew/multiColDetect.py", job.idhmc_xml_file
        ]
        results = mock_results_tuple()
        expected_results = results(None, None, 0)
        mock_stdout = "{\"skew_idx\": \"0.000000,2.400000,-0.200000,0.200000,\", \"multicol\": \"924.20,1436.72,1894.58\"}"
        self.mock_rv.communicate.return_value[0] = mock_stdout

        retval = multi_column_skew.run()
        args, kwargs = self.mock_popen.call_args

        self.assertTrue(self.mock_popen.called)
        self.assertEqual(expected_cmd, args[0])
        self.assertEqual(job.postproc_result.multicol, "924.20,1436.72,1894.58")
        self.assertEqual(job.postproc_result.skew_idx, "0.000000,2.400000,-0.200000,0.200000,")
        self.assertTupleEqual(expected_results, retval)

    def test_should_run_false(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.postproc_result.multicol_exists = True
        job.postproc_result.skew_idx_exists = True
        multi_column_skew = MultiColumnSkew(job)

        self.assertFalse(multi_column_skew.should_run())

    def test_should_run_true_if_multicol_missing(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.postproc_result.multicol_exists = False
        job.postproc_result.skew_idx_exists = True
        multi_column_skew = MultiColumnSkew(job)

        self.assertTrue(multi_column_skew.should_run())

    def test_should_run_true_if_skew_idx_missing(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.postproc_result.multicol_exists = True
        job.postproc_result.skew_idx_exists = False
        multi_column_skew = MultiColumnSkew(job)

        self.assertTrue(multi_column_skew.should_run())

    def test_should_run_true_if_all_values_missing(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.postproc_result.multicol_exists = False
        job.postproc_result.skew_idx_exists = False
        multi_column_skew = MultiColumnSkew(job)

        self.assertTrue(multi_column_skew.should_run())


def suite():
    return TestLoader().loadTestsFromTestCase(TestMultiColumnSkew)
