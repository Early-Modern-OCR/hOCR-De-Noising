from flexmock import flexmock
import mock
import os
import pytest
from unittest import TestCase
from unittest import TestLoader
from tests.utilities import *
from emop.lib.emop_job import EmopJob


class TestEmopPostprocResult(TestCase):
    def setUp(self):
        os.environ["TMPDIR"] = "/tmpdne"
        input_data = load_fixture_file("input_payload_1.json")
        self.job_data = input_data[0]
        self.settings = default_settings()
        self.scheduler = mock_scheduler_slurm()
        self.job = EmopJob(self.job_data, self.settings, self.scheduler)

    def test_init(self):
        self.assertEqual("/dh/data/shared/text-xml/IDHMC-ocr", self.job.output_root_dir)
        self.assertEqual("/tmpdne", self.job.temp_dir)
        expected_output_dir = "/dh/data/shared/text-xml/IDHMC-ocr/%s/%s" % (self.job.batch_job.id, self.job.work.id)
        self.assertEqual(expected_output_dir, self.job.output_dir)

def suite():
    return TestLoader().loadTestsFromTestCase(TestEmopPostprocResult)
