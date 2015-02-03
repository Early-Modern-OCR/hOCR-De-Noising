from flexmock import flexmock
import glob
import mock
import os
import tempfile
from unittest import TestCase
from unittest import TestLoader
from tests.utilities import *
from emop.lib.processes.page_corrector import PageCorrector


class TestPageCorrector(TestCase):
    def setUp(self):
        self.popen_patcher = mock.patch("emop.lib.utilities.subprocess32.Popen")
        self.mock_popen = self.popen_patcher.start()
        self.mock_rv = mock.Mock()
        self.mock_rv.communicate.return_value = ["", ""]
        self.mock_rv.returncode = 0
        self.mock_popen.return_value = self.mock_rv
        self.tmpdir = tempfile.mkdtemp()
        self.dbconf = os.path.join(self.tmpdir, "emop.properties")
        os.environ["TMPDIR"] = self.tmpdir
        self.settings = default_settings()
        self.seasr_home = os.path.join(self.settings.emop_home, "lib/seasr")
        self.dicts_dir = os.path.join(self.seasr_home, "dictionaries")
        self.dict_files = glob.glob("%s/*.dict" % self.dicts_dir)
        self.settings.seasr_home = self.seasr_home
        self.executable = os.path.join(self.seasr_home, "PageCorrector.jar")
        self.transformations = os.path.join(self.seasr_home, "rules/transformations.json")
        self.job = mock_emop_job(self.settings)

    def tearDown(self):
        self.popen_patcher.stop()
        os.rmdir(self.tmpdir)

    @mock.patch("emop.lib.processes.page_corrector.os.path.isfile")
    def test_run(self, mock_path_isfile):
        mock_path_isfile.return_value = True

        expected_cmd = flatten_list([
            "java", "-Xms128M", "-Xmx512M", "-jar", self.executable,
            "--dbconf", self.dbconf, "-t", self.transformations,
            "-o", self.job.output_dir, "--stats",
            "--alt", "2", "--max-transforms", "20", "--noiseCutoff", "0.5",
            "--dict", self.dict_files, "--", self.job.xml_file
        ])
        stdout = "{\"total\":1,\"ignored\":0,\"correct\":0,\"corrected\":1,\"unchanged\":0}"
        results = mock_results_tuple()
        expected_results = results(None, None, 0)
        self.mock_rv.communicate.return_value[0] = stdout

        page_corrector = PageCorrector(self.job)
        retval = page_corrector.run()
        args, kwargs = self.mock_popen.call_args

        self.maxDiff = None
        self.assertTrue(mock_path_isfile.called)
        self.assertTrue(self.mock_popen.called)
        self.assertEqual(expected_cmd, args[0])
        self.assertEqual(self.job.postproc_result.pp_health, stdout)
        self.assertTupleEqual(expected_results, retval)

    def test_run_with_dump(self):
        expected_cmd = flatten_list([
            "java", "-Xms128M", "-Xmx512M", "-jar", self.executable,
            "--dbconf", self.dbconf, "-t", self.transformations,
            "-o", self.job.output_dir, "--stats",
            "--alt", "2", "--max-transforms", "20", "--noiseCutoff", "0.5",
            "--dict", self.dict_files, "--dump", "--", self.job.xml_file
        ])

        page_corrector = PageCorrector(self.job)
        page_corrector.dump = True
        page_corrector.run()
        args, kwargs = self.mock_popen.call_args

        self.assertEqual(expected_cmd, args[0])

    def test_run_with_save(self):
        expected_cmd = flatten_list([
            "java", "-Xms128M", "-Xmx512M", "-jar", self.executable,
            "--dbconf", self.dbconf, "-t", self.transformations,
            "-o", self.job.output_dir, "--stats",
            "--alt", "2", "--max-transforms", "20", "--noiseCutoff", "0.5",
            "--dict", self.dict_files, "--save", "--", self.job.xml_file
        ])

        page_corrector = PageCorrector(self.job)
        page_corrector.save = True
        page_corrector.run()
        args, kwargs = self.mock_popen.call_args

        self.assertEqual(expected_cmd, args[0])

    def test_should_run_false(self):
        self.job.postproc_result.pp_health_exists = True
        self.job.page_result.corr_ocr_text_path_exists = True
        self.job.page_result.corr_ocr_xml_path_exists = True
        page_corrector = PageCorrector(self.job)

        self.assertFalse(page_corrector.should_run())

    def test_should_run_true_pp_health_missing(self):
        self.job.postproc_result.pp_health_exists = False
        self.job.page_result.corr_ocr_text_path_exists = True
        self.job.page_result.corr_ocr_xml_path_exists = True
        page_corrector = PageCorrector(self.job)

        self.assertTrue(page_corrector.should_run())

    def test_should_run_true_corr_ocr_text_path_missing(self):
        self.job.postproc_result.pp_health_exists = True
        self.job.page_result.corr_ocr_text_path_exists = False
        self.job.page_result.corr_ocr_xml_path_exists = True
        page_corrector = PageCorrector(self.job)

        self.assertTrue(page_corrector.should_run())

    def test_should_run_true_corr_ocr_xml_path_missing(self):
        self.job.postproc_result.pp_health_exists = True
        self.job.page_result.corr_ocr_text_path_exists = True
        self.job.page_result.corr_ocr_xml_path_exists = False
        page_corrector = PageCorrector(self.job)

        self.assertTrue(page_corrector.should_run())

    def test_should_run_true_all_values_missing(self):
        self.job.postproc_result.pp_health_exists = False
        self.job.page_result.corr_ocr_text_path_exists = False
        self.job.page_result.corr_ocr_xml_path_exists = False
        page_corrector = PageCorrector(self.job)

        self.assertTrue(page_corrector.should_run())


def suite():
    return TestLoader().loadTestsFromTestCase(TestPageCorrector)
