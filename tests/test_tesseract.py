import mock
import os
import pytest
from unittest import TestCase
from unittest import TestLoader
from tests.utilities import *
from emop.lib.processes.tesseract import Tesseract


class TestTesseract(TestCase):
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
            "tesseract", "/dh/dne/image.tiff", "/dh/data/shared/text-xml/IDHMC-ocr/1/1/1",
            "-l", "TEST Font", "/foo/tess_cfg.txt"
        ]
        results = mock_results_tuple()
        expected_results = results(None, None, 0)
        exec_cmd = mock_exec_cmd(stdout="", stderr=None, exitcode=0)

        retval = tesseract.run()
        args, kwargs = exec_cmd.call_args

        self.assertTrue(mock_path_isfile.called)
        self.assertTrue(mock_path_isdir.called)
        self.assertTrue(mock_mkdirs_exists_ok.called)
        self.assertTrue(exec_cmd.called)
        self.assertEqual(expected_cmd, args[0])
        #self.assertTrue(mock_os_rename.called)
        self.assertTupleEqual(expected_results, retval)

def suite():
    return TestLoader().loadTestsFromTestCase(TestTesseract)
