import mock
import os
import pytest
from unittest import TestCase
from unittest import TestLoader
from tests.utilities import *
from emop.lib.processes.juxta_compare import JuxtaCompare


class TestJuxtaCompare(TestCase):
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
        exec_cmd = mock_exec_cmd(stdout="0.01", stderr=None, exitcode=0)

        retval = juxta_compare.run(postproc=True)
        args, kwargs = exec_cmd.call_args

        self.maxDiff = None
        self.assertTrue(mock_path_isfile.called)
        self.assertTrue(exec_cmd.called)
        self.assertEqual(expected_cmd, args[0])
        self.assertEqual(job.page_result.juxta_change_index, 0.01)
        self.assertTupleEqual(expected_results, retval)


def suite():
    return TestLoader().loadTestsFromTestCase(TestJuxtaCompare)
