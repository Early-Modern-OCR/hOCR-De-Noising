import os


class EmopScheduler(object):

    supported_schedulers = {
        "slurm": {"module": "emop.lib.schedulers.emop_slurm", "class": "EmopSLURM"},
    }

    supported_jobid_env_vars = [
        'SLURM_JOB_ID',
        'SLURM_JOBID',
    ]

    def __init__(self, settings):
        """ Initialize EmopScheduler object and attributes

        Args:
            settings (object): EmopSettings instance
        """
        self.settings = settings

    def current_job_count(self):
        raise NotImplementedError

    def submit_job(self, proc_id):
        raise NotImplementedError

    @classmethod
    def is_job_environment(cls):
        """Test if currently in a valid scheduler job environment.

        The class variable `supported_jobid_env_vars` contains a list
        of the valid job ID environment variables for supported schedulers.

        The current environment is tested to see if it contains a valid job ID
        environment variable.

        Returns:
            bool: True if the current environment contains an environment
                variable from the class `supported_jobid_env_vars` list.
                False is returned if none are found.

        """
        job_env = False
        for jobid_env_var in cls.supported_jobid_env_vars:
            if os.environ.get(jobid_env_var):
                job_env = True
        return job_env
