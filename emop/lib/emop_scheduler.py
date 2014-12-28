import logging
import os

logger = logging.getLogger('emop')


class EmopScheduler(object):

    #: Define attributes of supported schedulers.
    #: To add a new scheduler this dict must be updated.
    supported_schedulers = {
        "slurm": {"module": "emop.lib.schedulers.emop_slurm", "class": "EmopSLURM"},
    }

    #: The name of the scheduler must be defined in a child class.
    name = ""
    #: The support JOB ID environment variables must be defined in a child class.
    jobid_env_vars = []

    def __init__(self, settings):
        """ Initialize EmopScheduler object and attributes

        Attributes:
            settings (EmopSettings): Instance of EmopSettings
            name (str): Name of the scheduler, defined in a child class.
            job_id (str or int): Current job ID and the value is determined
                by environment variable list defined in a child class.

        Args:
            settings (object): EmopSettings instance
        """
        self.settings = settings
        self.name = self.get_name()
        self.job_id = self.get_job_id()

    @classmethod
    def get_scheduler_instance(cls, name, settings):
        """Get the scheduler instance

        Based on the value of the name argument, an instance
        of that scheduler class is returned.

        The logic in the function is dynamic so that only the
        supported_schedulers dict in EmopScheduler needs to be
        updated to add additional scheduler support.

        Args:
            name (str): Name of scheduler to get instance of.
            settings (EmopSettings): Instance of EmopSettings.

        Returns:
            object: Instance of an EmopScheduler sub-class.
        """
        name = name.lower()
        supported_schedulers = cls.supported_schedulers
        if name in supported_schedulers:
            dict_ = supported_schedulers.get(name)
            module_ = __import__(dict_["module"], fromlist=[dict_["class"]])
            class_ = getattr(module_, dict_["class"])
            return class_(settings=settings)
        else:
            logger.error("Unsupported scheduler %s" % name)
            raise NotImplementedError

    def current_job_count(self):
        raise NotImplementedError

    def submit_job(self, proc_id):
        raise NotImplementedError

    def is_job_environment(self):
        """Test if currently in a valid scheduler job environment.

        The class attribute `jobid_env_vars` contains a list
        of the valid job ID environment variables for a scheduler.

        The current environment is tested to see if it contains a valid job ID
        environment variable.

        Returns:
            bool: True if the current environment contains an environment
                variable from the class attribute `jobid_env_vars` list.
                False is returned if none are found.

        """
        job_env = False
        for jobid_env_var in self.__class__.jobid_env_vars:
            if os.environ.get(jobid_env_var):
                logger.debug("Found scheduler job ID environment variable %s" % jobid_env_var)
                job_env = True
        return job_env

    def get_name(self):
        """Get the scheduler's name

        The return value is pulled from the class `name` attribute.

        Returns:
            str: The scheduler's name
        """
        name = self.__class__.name
        if not name:
            raise NotImplementedError
        return name

    def get_job_id(self):
        """Get the scheduler's job ID

        Loops over the class' `jobid_env_vars` attribute to find the
        current job ID.

        Returns:
            int: The job ID of the current scheduler job.
        """
        jobid_env_vars = self.__class__.jobid_env_vars
        if not jobid_env_vars:
            raise NotImplementedError
        for jobid_env_var in jobid_env_vars:
            jobid = os.environ.get(jobid_env_var)
            if jobid:
                return jobid
