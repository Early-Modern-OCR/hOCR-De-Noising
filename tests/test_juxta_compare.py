import mock
import os
import pytest
from unittest import TestCase
from unittest import TestLoader
from tests.utilities import *
from emop.lib.processes.juxta_compare import JuxtaCompare


class TestJuxtaCompare(TestCase):
    def setUp(self):
        self.popen_patcher = mock.patch("emop.lib.utilities.subprocess32.Popen")
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
        settings.juxta_home = "/foo/lib/juxta-cl"
        job = mock_emop_job(settings)
        job.page.ground_truth_file = "/dne/gt.txt"
        juxta_compare = JuxtaCompare(job)

        mock_path_isfile.return_value = True

        expected_cmd = [
            "java", "-Xms128M", "-Xmx128M", "-jar", "/foo/lib/juxta-cl/juxta-cl.jar",
            "-diff", "/dh/dne/gt.txt", job.alto_txt_file,
            "-algorithm", "jaro_winkler", "-hyphen", "none"
        ]
        results = mock_results_tuple()
        expected_results = results(None, None, 0)
        self.mock_rv.communicate.return_value[0] = "0.01"

        retval = juxta_compare.run(postproc=True)
        args, kwargs = self.mock_popen.call_args

        self.maxDiff = None
        self.assertTrue(mock_path_isfile.called)
        self.assertTrue(self.mock_popen.called)
        self.assertEqual(expected_cmd, args[0])
        self.assertEqual(job.page_result.juxta_change_index, 0.01)
        self.assertTupleEqual(expected_results, retval)

    def test_should_run_false(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.page_result.juxta_change_index_exists = True
        juxta_compare = JuxtaCompare(job)

        self.assertFalse(juxta_compare.should_run())

    def test_should_run_true(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.page_result.juxta_change_index_exists = False
        juxta_compare = JuxtaCompare(job)

        self.assertTrue(juxta_compare.should_run())


def suite():
    return TestLoader().loadTestsFromTestCase(TestJuxtaCompare)
