from flexmock import flexmock
import mock
import os
import pytest
from unittest import TestCase
from unittest import TestLoader
from tests.utilities import *
from emop.lib.processes.tesseract import Tesseract


class TestTesseract(TestCase):
    def setUp(self):
        self.popen_patcher = mock.patch("emop.lib.utilities.subprocess32.Popen")
        self.mock_popen = self.popen_patcher.start()
        self.mock_rv = mock.Mock()
        self.mock_rv.communicate.return_value = ["", ""]
        self.mock_rv.returncode = 0
        self.mock_popen.return_value = self.mock_rv

    def tearDown(self):
        self.popen_patcher.stop()

    @mock.patch("emop.lib.processes.tesseract.os.path.isfile")
    @mock.patch("emop.lib.processes.tesseract.os.path.isdir")
    @mock.patch("emop.lib.processes.tesseract.os.rename")
    @mock.patch("emop.lib.processes.tesseract.mkdirs_exists_ok")
    def test_run(self, mock_mkdirs_exists_ok, mock_os_rename, mock_path_isdir, mock_path_isfile):
        settings = default_settings()
        settings.emop_home = "/foo"
        job = mock_emop_job(settings)
        tesseract = Tesseract(job)

        mock_path_isfile.return_value = True
        mock_path_isdir.return_value = False

        expected_cmd = [
            "tesseract", job.image_path, tesseract.output_filename,
            "-l", job.font.name, tesseract.cfg
        ]
        results = mock_results_tuple()
        expected_results = results(None, None, 0)
        self.mock_rv.communicate.return_value[0] = ""

        retval = tesseract.run()
        args, kwargs = self.mock_popen.call_args

        self.assertTrue(mock_path_isfile.called)
        self.assertTrue(mock_path_isdir.called)
        self.assertTrue(mock_mkdirs_exists_ok.called)
        self.assertTrue(self.mock_popen.called)
        self.assertEqual(expected_cmd, args[0])
        # self.assertTrue(mock_os_rename.called)
        self.assertTupleEqual(expected_results, retval)

    def test_should_run_false(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.page_result.ocr_text_path_exists = True
        job.page_result.ocr_xml_path_exists = True
        tesseract = Tesseract(job)

        self.assertFalse(tesseract.should_run())

    def test_should_run_true_ocr_text_path_missing(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.page_result.ocr_text_path_exists = False
        job.page_result.ocr_xml_path_exists = True
        tesseract = Tesseract(job)

        self.assertTrue(tesseract.should_run())

    def test_should_run_true_ocr_xml_path_missing(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.page_result.ocr_text_path_exists = True
        job.page_result.ocr_xml_path_exists = False
        tesseract = Tesseract(job)

        self.assertTrue(tesseract.should_run())

    def test_should_run_true_all_values_missing(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.page_result.ocr_text_path_exists = False
        job.page_result.ocr_xml_path_exists = False
        tesseract = Tesseract(job)

        self.assertTrue(tesseract.should_run())


def suite():
    return TestLoader().loadTestsFromTestCase(TestTesseract)
