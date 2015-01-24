import glob
import logging
import os
import re
from emop.lib.emop_base import EmopBase

logger = logging.getLogger('emop')

processes = [
    "OCR",
    "Denoise",
    "MultiColumnSkew",
    "XML_To_Text",
    "PageEvaluator",
    "PageCorrector",
    "JuxtaCompare",
    # "RetasCompare",
]


class EmopQuery(EmopBase):

    def __init__(self, config_path):
        super(self.__class__, self).__init__(config_path)

    def pending_pages(self, q_filter):
        job_status_params = {
            'name': 'Not Started',
        }
        job_status_request = self.emop_api.get_request("/api/job_statuses", job_status_params)
        if not job_status_request:
            return None
        job_status_results = job_status_request.get('results')[0]
        job_status_id = job_status_results.get('id')
        if q_filter and isinstance(q_filter, dict):
            job_queue_params = q_filter
        else:
            job_queue_params = {}
        job_queue_params["job_status_id"] = str(job_status_id)
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
        runtimes["processes"] = {}
        for process in processes:
            runtimes["processes"][process] = []

        with open(filename) as f:
            lines = f.readlines()

        for line in lines:
            page_match = re.search("Job \[.*\] COMPLETE: Duration: ([0-9.]+) secs", line)
            total_match = re.search("TOTAL TIME: ([0-9.]+)$", line)

            if page_match:
                page_runtime = page_match.group(1)
                runtimes["pages"].append(float(page_runtime))
            elif total_match:
                total_runtime = total_match.group(1)
                runtimes["total"].append(float(total_runtime))
            else:
                for process in processes:
                    process_match = re.search("%s \[.*\] COMPLETE: Duration: ([0-9.]+) secs" % process, line)
                    if process_match:
                        process_runtime = process_match.group(1)
                        runtimes["processes"][process].append(float(process_runtime))
        return runtimes

    def get_runtimes(self):
        results = {}
        results["processes"] = []
        runtimes = {}
        runtimes["pages"] = []
        runtimes["total"] = []
        for process in processes:
            results[process] = []
            runtimes[process] = []

        glob_path = os.path.join(self.settings.scheduler_logdir, "*.out")
        files = glob.glob(glob_path)

        for f in files:
            file_runtimes = self.parse_file_for_runtimes(f)
            runtimes["pages"] = runtimes["pages"] + file_runtimes["pages"]
            runtimes["total"] = runtimes["total"] + file_runtimes["total"]
            for process in processes:
                runtimes[process] = runtimes[process] + file_runtimes["processes"][process]

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

        for process in processes:
            process_runtimes = runtimes[process]
            cnt = len(process_runtimes)
            if cnt > 0:
                total = sum(process_runtimes)
                avg = total / cnt
            else:
                total = sum(process_runtimes)
                avg = 0
            process_results = {"name": process, "count": cnt, "total": total, "avg": avg}
            results["processes"].append(process_results.copy())

        results["total_pages"] = total_pages
        results["total_page_runtime"] = total_page_runtime
        results["average_page_runtime"] = average_page_runtime
        results["total_jobs"] = total_jobs
        results["average_job_runtime"] = average_job_runtime
        return results
