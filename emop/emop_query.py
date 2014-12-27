import glob
import logging
import os
import re
from emop.lib.emop_base import EmopBase

logger = logging.getLogger('emop')


class EmopQuery(EmopBase):

    def __init__(self, config_path):
        super(self.__class__, self).__init__(config_path)

    def pending_pages(self):
        job_status_params = {
            'name': 'Not Started',
        }
        job_status_request = self.emop_api.get_request("/api/job_statuses", job_status_params)
        if not job_status_request:
            return None
        job_status_results = job_status_request.get('results')[0]
        job_status_id = job_status_results.get('id')
        job_queue_params = {
            'job_status_id': "%s" % job_status_id,
        }
        job_queue_request = self.emop_api.get_request("/api/job_queues/count", job_queue_params)
        if not job_status_request:
            return None
        job_queue_results = job_queue_request.get('job_queue')
        count = job_queue_results.get('count')
        return count

    def parse_file_for_runtimes(self, filename):
        runtimes = {}
        runtimes["pages"] = []
        runtimes["total"] = []
        with open(filename) as f:
            lines = f.readlines()

        for line in lines:
            page_match = re.search("COMPLETE. Duration: ([0-9.]+) secs", line)
            total_match = re.search("TOTAL TIME: ([0-9.]+)$", line)

            if page_match:
                page_runtime = page_match.group(1)
                runtimes["pages"].append(float(page_runtime))
            elif total_match:
                total_runtime = total_match.group(1)
                runtimes["total"].append(float(total_runtime))
            else:
                continue
        return runtimes

    def get_runtimes(self):
        results = {}
        runtimes = {}
        runtimes["pages"] = []
        runtimes["total"] = []

        glob_path = os.path.join(self.settings.scheduler_logdir, "*.out")
        files = glob.glob(glob_path)

        for f in files:
            results = self.parse_file_for_runtimes(f)
            runtimes["pages"] = runtimes["pages"] + results["pages"]
            runtimes["total"] = runtimes["total"] + results["total"]

        total_pages = len(runtimes["pages"])
        total_jobs = len(runtimes["total"])

        if total_pages > 0:
            total_page_runtime = sum(runtimes["pages"])
            average_page_runtime = total_page_runtime / total_pages
        else:
            total_page_runtime = sum(runtimes["pages"])
            average_page_runtime = 0

        if total_jobs > 0:
            total_job_runtime = sum(runtimes["total"])
            average_job_runtime = total_job_runtime / total_jobs
        else:
            total_job_runtime = sum(runtimes["total"])
            average_job_runtime = 0

        results["total_pages"] = total_pages
        results["total_page_runtime"] = total_page_runtime
        results["average_page_runtime"] = average_page_runtime
        results["total_jobs"] = total_jobs
        results["average_job_runtime"] = average_job_runtime
        return results
