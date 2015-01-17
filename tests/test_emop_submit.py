from unittest import TestCase
from unittest import TestLoader
from tests.utilities import default_config_path
from emop.emop_submit import EmopSubmit


class TestEmopSubmit(TestCase):
    def setUp(self):
        pass

    def get_submit(self, max_jobs, min_job_runtime, max_job_runtime, avg_page_runtime):
        submit = EmopSubmit(default_config_path())
        submit.settings.max_jobs = max_jobs
        submit.settings.min_job_runtime = min_job_runtime
        submit.settings.max_job_runtime = max_job_runtime
        submit.settings.avg_page_runtime = avg_page_runtime
        return submit

    def test_optimize_submit_1(self):
        submit = self.get_submit(100, 300, 3600, 60)
        num_jobs, pages_per_job = submit.optimize_submit(page_count=10000, running_job_count=0)
        self.assertEqual(num_jobs, 100)
        self.assertEqual(pages_per_job, 60)

    def test_optimize_submit_2(self):
        submit = self.get_submit(100, 300, 3600, 60)
        num_jobs, pages_per_job = submit.optimize_submit(page_count=4, running_job_count=0)
        self.assertEqual(num_jobs, 1)
        self.assertEqual(pages_per_job, 4)

    def test_optimize_submit_3(self):
        submit = self.get_submit(100, 300, 3600, 60)
        num_jobs, pages_per_job = submit.optimize_submit(page_count=100, running_job_count=0)
        self.assertEqual(num_jobs, 20)
        self.assertEqual(pages_per_job, 5)

    def test_optimize_submit_4(self):
        submit = self.get_submit(100, 300, 3600, 60)
        num_jobs, pages_per_job = submit.optimize_submit(page_count=600, running_job_count=0)
        self.assertEqual(num_jobs, 100)
        self.assertEqual(pages_per_job, 6)

    def test_optimize_submit_idhmc_1(self):
        submit = self.get_submit(128, 300, 259200, 300)
        num_jobs, pages_per_job = submit.optimize_submit(page_count=128000, running_job_count=0)
        self.assertEqual(num_jobs, 128)
        self.assertEqual(pages_per_job, 864)

    def test_optimize_submit_background_1(self):
        submit = self.get_submit(500, 300, 345600, 300)
        num_jobs, pages_per_job = submit.optimize_submit(page_count=5000, running_job_count=0)
        self.assertEqual(num_jobs, 500)
        self.assertEqual(pages_per_job, 10)

def suite():
    return TestLoader().loadTestsFromTestCase(TestEmopSubmit)
