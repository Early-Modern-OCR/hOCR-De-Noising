import json
import logging
import os
from emop.lib.emop_base import EmopBase
from emop.lib.emop_payload import EmopPayload

logger = logging.getLogger('emop')


class EmopSubmit(EmopBase):

    def __init__(self, config_path, simulate=False):
        """ Initialize EmopSubmit object and attributes

        Args:
            config_path (str): path to application config file

        """
        super(self.__class__, self).__init__(config_path)
        self.simulate = simulate

    def current_job_count(self):
        """Get count of this application's active jobs

        Currently this returns Running+Pending jobs
        """
        cmd = ["squeue", "-r", "--noheader", "-p", self.settings.slurm_queue, "-n", self.settings.slurm_job_name]
        proc = EmopBase.exec_cmd(cmd, log_level="debug")
        lines = proc.stdout.splitlines()
        num = len(lines)
        return num

    def optimize_submit(self, page_count, running_job_count):
        """Determine optimal job submission

        This function attempts to determine the best number of jobs
        and how many pages per job should be submitted to the scheduler.

        This function does not return a value but sets the num_jobs and
        pages_per_job attributes.

        Args:
            page_count (int): Number of pages needing to be processed
            running_job_count (int): Number of active jobs

        """
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
        expected_runtime_msg = "Expected job runtime: %s seconds" % expected_runtime
        if self.simulate:
            logger.info(expected_runtime_msg)
        else:
            logger.debug(expected_runtime_msg)

        self.total_pages_to_run = self.num_jobs * self.pages_per_job

        optimal_submit_msg = "Optimal submission is %s jobs with %s pages per job" % (self.num_jobs, self.pages_per_job)
        if self.simulate:
            logger.info(optimal_submit_msg)
        else:
            logger.debug(optimal_submit_msg)

    def submit_job(self):
        """Submit a job to SLURM

        First reserve pages by sending PUT request to dashboard API.
        The results from the dashboard API are then used to submit the job
        to SLURM.

        The PROC_ID environment variable is set so that the SLURM job can know
        which JSON file to load.

        Returns:
            None is returned upon failure.

        """
        if self.simulate:
            return None
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
        logger.debug("Payload: %s" % json.dumps(results, sort_keys=True, indent=4))

        if reserved < 1:
            logger.error("No pages reserved")
            return None

        self.payload = EmopPayload(self.settings, proc_id)
        self.payload.save_input(results)

        os.environ['PROC_ID'] = proc_id
        cmd = ["sbatch", "--parsable", "-p", self.settings.slurm_queue, "-J", self.settings.slurm_job_name, "-o", self.settings.slurm_logfile, "emop.slrm"]
        proc = EmopBase.exec_cmd(cmd, log_level="debug")
        if proc.exitcode != 0:
            logger.error("Failed to submit job to SLURM.")
            return None
        slurm_job_id = proc.stdout.rstrip()
        logger.info("SLURM job %s submitted for PROC_ID %s" % (slurm_job_id, proc_id))
