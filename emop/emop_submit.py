import json
import logging
import os
from emop.lib.emop_base import EmopBase
from emop.lib.emop_payload import EmopPayload
from emop.lib.emop_scheduler import EmopScheduler

logger = logging.getLogger('emop')


class EmopSubmit(EmopBase):

    def __init__(self, config_path):
        """ Initialize EmopSubmit object and attributes

        Args:
            config_path (str): path to application config file
        """
        super(self.__class__, self).__init__(config_path)
        self.scheduler = self.get_scheduler()
    
    def get_scheduler(self):
        """Get the scheduler instance

        Based on the value of the scheduler setting, an instance
        of that scheduler class is returned.

        The logic in the function is dynamic so that only the
        supported_schedulers dict in EmopScheduler needs to be
        updated to add additional scheduler support.

        Returns:
            object: Instance of an EmopScheduler sub-class.
        """
        config_scheduler = self.settings.scheduler.lower()
        supported_schedulers = EmopScheduler.supported_schedulers
        if config_scheduler in supported_schedulers:
            dict_ = supported_schedulers.get(config_scheduler)
            module_ = __import__(dict_["module"], fromlist=[dict_["class"]])
            class_ = getattr(module_, dict_["class"])
            return class_(settings=self.settings)
        else:
            logger.error("Unsupported scheduler %s" % config_scheduler)
            raise NotImplementedError

    def optimize_submit(self, page_count, running_job_count, sim=False):
        """Determine optimal job submission

        This function attempts to determine the best number of jobs
        and how many pages per job should be submitted to the scheduler.

        This function does not return a value but sets the num_jobs and
        pages_per_job attributes.

        Args:
            page_count (int): Number of pages needing to be processed
            running_job_count (int): Number of active jobs

        Returns:
            list: First value is number of jobs and second value
                is number of pages per job.
        """
        num_jobs = 0
        pages_per_job = 1
        job_slots_available = self.settings.max_jobs - running_job_count
        run_option_a = page_count / job_slots_available
        run_option_b = self.settings.max_job_runtime / self.settings.avg_page_runtime
        run_option_c = self.settings.min_job_runtime / self.settings.avg_page_runtime
        logger.debug("RunOptA: %s , RunOptB: %s, RunOptC: %s" % (run_option_a, run_option_b, run_option_c))

        if run_option_a > run_option_b:
            num_jobs = job_slots_available
            pages_per_job = run_option_b
        elif page_count < run_option_c:
            num_jobs = page_count / run_option_c
            pages_per_job = page_count
        elif run_option_a < run_option_c:
            num_jobs = page_count / run_option_c
            pages_per_job = run_option_c
        else:
            num_jobs = page_count / run_option_a
            pages_per_job = run_option_a

        if not num_jobs:
            num_jobs = 1

        expected_runtime = pages_per_job * self.settings.avg_page_runtime
        expected_runtime_msg = "Expected job runtime: %s seconds" % expected_runtime
        if sim:
            logger.info(expected_runtime_msg)
        else:
            logger.debug(expected_runtime_msg)

        total_pages_to_run = num_jobs * pages_per_job

        optimal_submit_msg = "Optimal submission is %s jobs with %s pages per job" % (num_jobs, pages_per_job)
        if sim:
            logger.info(optimal_submit_msg)
        else:
            logger.debug(optimal_submit_msg)

        return num_jobs, pages_per_job

    def reserve(self, num_pages):
        """Reserve pages for a job

        Reserve page(s) for work by sending PUT request to dashboard API.

        Returns:
            str: The reserved work's proc_id.
        """
        reserve_data = {
            "job_queue": {"num_pages": num_pages}
        }
        reserve_request = self.emop_api.put_request("/api/job_queues/reserve", reserve_data)
        if not reserve_request:
            return ""
        requested = reserve_request.get('requested')
        reserved = reserve_request.get('reserved')
        proc_id = reserve_request.get('proc_id')
        results = reserve_request.get('results')
        logger.debug("Requested %s pages, and %s were reserved with proc_id: %s" % (requested, reserved, proc_id))
        logger.debug("Payload: %s" % json.dumps(results, sort_keys=True, indent=4))

        if reserved < 1:
            logger.error("No pages reserved")
            return ""

        self.payload = EmopPayload(self.settings, proc_id)
        self.payload.save_input(results)

        return proc_id

