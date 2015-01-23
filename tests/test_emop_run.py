from flexmock import flexmock
import mock
import os
import pytest
from unittest import TestCase
from unittest import TestLoader
from tests.utilities import *
from emop.emop_run import EmopRun
import emop.lib.utilities
from emop.lib.processes.tesseract import Tesseract
from emop.lib.processes.xml_to_text import XML_To_Text
from emop.lib.processes.denoise import Denoise
from emop.lib.processes.multi_column_skew import MultiColumnSkew
from emop.lib.processes.page_evaluator import PageEvaluator
from emop.lib.processes.page_corrector import PageCorrector
from emop.lib.processes.juxta_compare import JuxtaCompare
from emop.lib.processes.retas_compare import RetasCompare


class TestEmopRun(TestCase):
    def setUp(self):
        os.environ["SLURM_JOB_ID"] = "2"
        self.run = EmopRun(config_path=default_config_path(), proc_id='0001')

    @pytest.fixture(autouse=True)
    def setup_files(self, tmpdir):
        self.tmpdir = tmpdir
        os.environ["TMPDIR"] = str(self.tmpdir)

    def test_append_result_failed(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        self.run.payload.save_output = mock.MagicMock()
        self.run.append_result(job=job, results="Test", failed=True)

        payload_save_args, payload_save_kwargs = self.run.payload.save_output.call_args
        actual_failed_results = payload_save_kwargs['data']['job_queues']['failed']
        actual_completed_results = payload_save_kwargs['data']['job_queues']['completed']

        expected_failed = {"id": job.id, "results": "SLURM JOB 2: Test"}
        self.assertEqual(1, len(actual_failed_results))
        self.assertEqual(0, len(actual_completed_results))
        self.assertEqual(expected_failed, actual_failed_results[0])
        self.assertTrue(self.run.payload.save_output.called)

    def test_append_result_completed(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        self.run.payload.save_output = mock.MagicMock()
        self.run.append_result(job=job, results=None)

        payload_save_args, payload_save_kwargs = self.run.payload.save_output.call_args
        actual_failed_results = payload_save_kwargs['data']['job_queues']['failed']
        actual_completed_results = payload_save_kwargs['data']['job_queues']['completed']

        expected_completed = [job.id]
        self.assertEqual(0, len(actual_failed_results))
        self.assertEqual(1, len(actual_completed_results))
        self.assertItemsEqual(expected_completed, actual_completed_results)
        self.assertTrue(self.run.payload.save_output.called)

    def test_get_results(self):
        self.run.jobs_completed.append(1)
        self.run.jobs_failed.append({"id": 2, "results": "test"})
        self.run.page_results.append({"batch_id": 1, "page_id": 2})
        self.run.postproc_results.append({"batch_job_id": 1, "page_id": 2})
        expected_value = {
            "job_queues": {
                "completed": [1],
                "failed": [{"id": 2, "results": "test"}]
            },
            "page_results": [{"batch_id": 1, "page_id": 2}],
            "postproc_results": [{"batch_job_id": 1, "page_id": 2}],
        }
        actual_value = self.run.get_results()
        self.assertEqual(expected_value, actual_value)

    def test_do_process_page_corrector(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        page_corrector = PageCorrector(job=job)
        page_corrector.run = mock.MagicMock()
        results = mock_results_tuple()
        page_corrector.should_run = mock.MagicMock()
        page_corrector.should_run.return_value = True
        page_corrector.run.return_value = results(stdout=None, stderr=None, exitcode=0)

        retval = self.run.do_process(obj=page_corrector, job=job)

        self.assertTrue(page_corrector.run.called)
        self.assertTrue(retval)

    def test_do_process_page_corrector_failed(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        page_corrector = PageCorrector(job=job)
        page_corrector.run = mock.MagicMock()
        results = mock_results_tuple()
        page_corrector.should_run = mock.MagicMock()
        page_corrector.should_run.return_value = True
        page_corrector.run.return_value = results(stdout=None, stderr="Test", exitcode=1)
        self.run.append_result = mock.MagicMock()

        retval = self.run.do_process(obj=page_corrector, job=job)

        self.run.append_result.assert_called_with(job=job, results="PageCorrector Failed: Test", failed=True)
        self.assertFalse(retval)

    def test_do_process_page_corrector_skipped(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        page_corrector = PageCorrector(job=job)
        page_corrector.run = mock.MagicMock()
        results = mock_results_tuple()
        page_corrector.run.return_value = results(stdout=None, stderr="Test", exitcode=1)
        flexmock(page_corrector).should_receive("should_run").and_return(False)
        self.run.append_result = mock.MagicMock()

        retval = self.run.do_process(obj=page_corrector, job=job)

        self.assertFalse(self.run.append_result.called)
        self.assertTrue(retval)

    def test_do_process_page_corrector_not_skipped(self):
        settings = default_settings()
        self.run.settings.controller_skip_existing = False
        job = mock_emop_job(settings)
        page_corrector = PageCorrector(job=job)
        page_corrector.run = mock.MagicMock()
        results = mock_results_tuple()
        page_corrector.run.return_value = results(stdout=None, stderr=None, exitcode=0)
        page_corrector.should_run = mock.MagicMock()
        self.run.append_result = mock.MagicMock()

        retval = self.run.do_process(obj=page_corrector, job=job)

        self.assertFalse(page_corrector.should_run.called)
        self.assertTrue(retval)

    def test_do_ocr_tesseract(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        results = mock_results_tuple()
        tesseract = Tesseract(job=job)
        results = mock_results_tuple()
        expected_results = results(stdout=None, stderr=None, exitcode=0)
        flexmock(os.path).should_receive("isfile").with_args(job.image_path).and_return(True)
        mock_mkdirs(job.output_dir)
        flexmock(os.path).should_receive("isfile").with_args(job.txt_file).and_return(True)
        flexmock(os.path).should_receive("isfile").with_args(job.hocr_file).and_return(True)
        flexmock(os.path).should_receive("isfile").with_args(job.xml_file).and_return(True)
        flexmock(tesseract).should_receive("run").and_return(expected_results)

        retval = self.run.do_ocr(job=job)

        self.assertTrue(retval)

    def test_do_ocr_tesseract_failed(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        job.page_result.ocr_text_path_exists = False
        job.page_result.ocr_xml_path_exists = False
        results = mock_results_tuple()
        tesseract = Tesseract(job=job)
        results = mock_results_tuple()
        expected_results = "tesseract OCR Failed: Could not find page image %s" % job.image_path
        flexmock(os.path).should_receive("isfile").with_args(job.txt_file).and_return(False)
        flexmock(os.path).should_receive("isfile").with_args(job.xml_file).and_return(False)
        flexmock(tesseract).should_receive("should_run").and_return(True)
        flexmock(os.path).should_receive("isfile").with_args(job.image_path).and_return(False)
        flexmock(tesseract).should_receive("run")
        self.run.append_result = mock.MagicMock()

        retval = self.run.do_ocr(job=job)

        self.run.append_result.assert_called_with(job=job, results=expected_results, failed=True)
        self.assertFalse(retval)

    def test_do_ocr_tesseract_skipped(self):
        settings = default_settings()
        job = mock_emop_job(settings)
        results = mock_results_tuple()
        tesseract = Tesseract(job=job)
        flexmock(os.path).should_receive("isfile").with_args(job.txt_file).and_return(True)
        flexmock(os.path).should_receive("isfile").with_args(job.xml_file).and_return(True)
        flexmock(tesseract).should_receive("should_run").and_return(False)
        flexmock(tesseract).should_receive("run")
        self.run.append_result = mock.MagicMock()

        retval = self.run.do_ocr(job=job)

        self.assertFalse(self.run.append_result.called)
        self.assertTrue(retval)

    # This test doesn't correctly validate should_run is not called.
    # When self.run.settings.controller_skip_existing is not set to False
    # the test still passes
    def test_do_ocr_tesseract_not_skipped(self):
        settings = default_settings()
        self.run.settings.controller_skip_existing = False
        job = mock_emop_job(settings)
        results = mock_results_tuple()
        tesseract = Tesseract(job=job)
        flexmock(os.path).should_receive("isdir").with_args(tesseract.output_parent_dir).and_return(True)
        flexmock(os.path).should_receive("isfile").with_args(job.txt_file).and_return(False)
        flexmock(os.path).should_receive("isfile").with_args(job.xml_file).and_return(True)
        flexmock(os.path).should_receive("isfile").with_args(job.hocr_file).and_return(True)
        flexmock(os.path).should_receive("isfile").with_args(job.image_path).and_return(True)
        flexmock(tesseract).should_receive("should_run").never()
        flexmock(tesseract).should_receive("run")

        retval = self.run.do_ocr(job=job)

        self.assertTrue(retval)

    def test_do_postprocesses(self):
        settings = default_settings()
        job = mock_emop_job(settings)

        # denoise = Denoise(job=job)
        # multi_column_skew = MultiColumnSkew(job=job)
        # xml_to_text_proc = XML_To_Text(job=job)
        # page_evaluator = PageEvaluator(job=job)
        # page_corrector = PageCorrector(job=job)
        # juxta_compare = JuxtaCompare(job=job)

        # These mocks don't work for some reason
        # flexmock(self.run).should_receive("do_process").with_args(obj=denoise, job=job).and_return(True)
        # flexmock(self.run).should_receive("do_process").with_args(obj=multi_column_skew, job=job).and_return(True)
        # flexmock(self.run).should_receive("do_process").with_args(obj=xml_to_text_proc, job=job).and_return(True)
        # flexmock(self.run).should_receive("do_process").with_args(obj=page_evaluator, job=job).and_return(True)
        # flexmock(self.run).should_receive("do_process").with_args(obj=page_corrector, job=job).and_return(True)
        # flexmock(self.run).should_receive("do_process").with_args(obj=juxta_compare, job=job).and_return(True)
        flexmock(self.run).should_receive("do_process").and_return(True)

        retval = self.run.do_postprocesses(job=job)

        self.assertTrue(retval)

    def test_do_postprocesses_failed(self):
        settings = default_settings()
        job = mock_emop_job(settings)

        flexmock(self.run).should_receive("do_process").and_return(False)

        retval = self.run.do_postprocesses(job=job)

        self.assertFalse(retval)

    def test_do_job(self):
        settings = default_settings()
        job = mock_emop_job(settings)

        flexmock(self.run).should_receive("do_ocr").and_return(True)
        flexmock(self.run).should_receive("do_postprocesses").and_return(True)

        retval = self.run.do_job(job=job)

        self.assertTrue(retval)

    def test_do_job_failed_ocr(self):
        settings = default_settings()
        job = mock_emop_job(settings)

        flexmock(self.run).should_receive("do_ocr").and_return(False)
        flexmock(self.run).should_receive("do_postprocesses").and_return(True)

        retval = self.run.do_job(job=job)

        self.assertFalse(retval)

    def test_do_job_failed_postprocesses(self):
        settings = default_settings()
        job = mock_emop_job(settings)

        flexmock(self.run).should_receive("do_ocr").and_return(True)
        flexmock(self.run).should_receive("do_postprocesses").and_return(False)

        retval = self.run.do_job(job=job)

        self.assertFalse(retval)


def suite():
    return TestLoader().loadTestsFromTestCase(EmopRun)
