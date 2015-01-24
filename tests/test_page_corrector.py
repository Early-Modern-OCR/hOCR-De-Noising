from flexmock import flexmock
import mock
import os
import pytest
from unittest import TestCase
from unittest import TestLoader
from tests.utilities import *
from emop.lib.processes.page_corrector import PageCorrector


class TestPageCorrector(TestCase):
    @pytest.fixture(autouse=True)
    def setup_files(self, tmpdir):
        self.tmpdir = tmpdir
        os.environ["TMPDIR"] = str(self.tmpdir)
        self.dbconf = str(tmpdir.join("emop.properties"))
        self.dicts_dir = tmpdir.mkdir("dictionaries")
        self.test_dict = self.dicts_dir.join("en.dict")

    @mock.patch("emop.lib.processes.page_corrector.os.path.isfile")
    def test_run(self, mock_path_isfile):
        settings = default_settings()
        settings.seasr_home = "/foo/lib/seasr"
        job = mock_emop_job(settings)
        page_corrector = PageCorrector(job)
        page_corrector.dicts_dir = str(self.dicts_dir)

        with open(str(self.test_dict), "w") as outfile:
            outfile.write(" ")

        mock_path_isfile.return_value = True

        expected_cmd = [
            "java", "-Xms128M", "-Xmx512M", "-jar", "/foo/lib/seasr/PageCorrector.jar",
            "--dbconf", self.dbconf, "-t", "/foo/lib/seasr/rules/transformations.json",
            "-o", job.output_dir, "--stats",
            "--alt", "2", "--max-transforms", "20", "--noiseCutoff", "0.5",
            "--dict", str(self.test_dict), "--", job.xml_file
        ]
        stdout = "{\"total\":1,\"ignored\":0,\"correct\":0,\"corrected\":1,\"unchanged\":0}"
        results = mock_results_tuple()
        expected_results = results(None, None, 0)
        exec_cmd = mock_exec_cmd(stdout=stdout, stderr=None, exitcode=0)

        retval = page_corrector.run()
        args, kwargs = exec_cmd.call_args

        self.maxDiff = None
        self.assertTrue(mock_path_isfile.called)
        self.assertTrue(exec_cmd.called)
        self.assertEqual(expected_cmd, args[0])
        self.assertEqual(job.postproc_result.pp_health, stdout)
        self.assertTupleEqual(expected_results, retval)
        exec_cmd.stop()

    def test_should_run_false(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.postproc_result.pp_health_exists = True
        job.page_result.corr_ocr_text_path_exists = True
        job.page_result.corr_ocr_xml_path_exists = True
        page_corrector = PageCorrector(job)

        self.assertFalse(page_corrector.should_run())

    def test_should_run_true_pp_health_missing(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.postproc_result.pp_health_exists = False
        job.page_result.corr_ocr_text_path_exists = True
        job.page_result.corr_ocr_xml_path_exists = True
        page_corrector = PageCorrector(job)

        self.assertTrue(page_corrector.should_run())

    def test_should_run_true_corr_ocr_text_path_missing(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.postproc_result.pp_health_exists = True
        job.page_result.corr_ocr_text_path_exists = False
        job.page_result.corr_ocr_xml_path_exists = True
        page_corrector = PageCorrector(job)

        self.assertTrue(page_corrector.should_run())

    def test_should_run_true_corr_ocr_xml_path_missing(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.postproc_result.pp_health_exists = True
        job.page_result.corr_ocr_text_path_exists = True
        job.page_result.corr_ocr_xml_path_exists = False
        page_corrector = PageCorrector(job)

        self.assertTrue(page_corrector.should_run())

    def test_should_run_true_all_values_missing(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.postproc_result.pp_health_exists = False
        job.page_result.corr_ocr_text_path_exists = False
        job.page_result.corr_ocr_xml_path_exists = False
        page_corrector = PageCorrector(job)

        self.assertTrue(page_corrector.should_run())


def suite():
    return TestLoader().loadTestsFromTestCase(TestPageCorrector)
