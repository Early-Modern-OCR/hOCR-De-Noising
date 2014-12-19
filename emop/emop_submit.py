import logging
import os
from emop.lib.emop_base import EmopBase
from emop.lib.emop_payload import EmopPayload

logger = logging.getLogger('emop')


class EmopSubmit(EmopBase):

    def __init__(self, config_path):
        super(self.__class__, self).__init__(config_path)

    def current_job_count(self):
        cmd = ["squeue", "-r", "--noheader", "-p", self.settings.slurm_queue, "-n", self.settings.slurm_job_name]
        proc = EmopBase.exec_cmd(cmd)
        lines = proc.stdout.splitlines()
        num = len(lines)
        return num

    def optimize_submit(self, page_count, running_job_count):
        job_slots_available = self.settings.max_jobs - running_job_count
        run_option_a = page_count / job_slots_available
        run_option_b = self.settings.max_job_runtime / self.settings.avg_page_runtime
        run_option_c = self.settings.min_job_runtime / self.settings.avg_page_runtime

        if run_option_a > run_option_b:
            self.num_jobs = job_slots_available
            self.pages_per_job = run_option_b
        elif page_count < run_option_c:
            self.num_jobs = page_count / run_option_c
            self.pages_per_job = page_count
        elif run_option_a < run_option_c:
            self.num_jobs = page_count / run_option_c
            self.pages_per_job = run_option_c
        else:
            self.num_jobs = page_count / run_option_a
            self.pages_per_job = run_option_a

        if not self.num_jobs:
            self.num_jobs = 1

        expected_runtime = self.pages_per_job * self.settings.avg_page_runtime
        logger.debug("Expected job runtime: %s seconds" % expected_runtime)

        self.total_pages_to_run = self.num_jobs * self.pages_per_job

        logger.debug("Optimal submission is %s jobs with %s pages per job" % (self.num_jobs, self.pages_per_job))

    def submit_job(self):
        reserve_data = {
            "job_queue": {"num_pages": self.pages_per_job}
        }
        reserve_request = self.emop_api.put_request("/api/job_queues/reserve", reserve_data)
        if not reserve_request:
            return None
        requested = reserve_request.get('requested')
        reserved = reserve_request.get('reserved')
        proc_id = reserve_request.get('proc_id')
        results = reserve_request.get('results')
        logger.debug("Requested %s pages, and %s were reserved with proc_id: %s" % (requested, reserved, proc_id))
        logger.debug("Payload: %s" % str(results))

        if reserved < 1:
            logger.error("No pages reserved")
            return None

        self.payload = EmopPayload(self.settings.payload_input_path, self.settings.payload_output_path, proc_id)
        self.payload.save_input(results)

        os.environ['PROC_ID'] = proc_id
        cmd = ["sbatch", "--parsable", "-p", self.settings.slurm_queue, "-J", self.settings.slurm_job_name, "-o", self.settings.slurm_logfile, "emop.slrm"]
        proc = EmopBase.exec_cmd(cmd)
        out = proc.stdout.rstrip()
        logger.info("SLURM jobID: %s" % out)
