import logging
import os
from emop.lib.utilities import exec_cmd
from emop.lib.emop_scheduler import EmopScheduler

logger = logging.getLogger('emop')


class EmopSLURM(EmopScheduler):

    name = "SLURM"

    jobid_env_vars = [
        'SLURM_JOB_ID',
        'SLURM_JOBID',
    ]

    def __init__(self, settings):
        """Initialize EmopSLURM object and attributes

        Args:
            settings (object): instance of EmopSettings
        """
        super(self.__class__, self).__init__(settings)

    def current_job_count(self):
        """Get count of this application's active jobs

        The currentjobs are those that are Running+Pending.

        Example command used:
            squeue -r --noheader -p idhmc -n emop-controller

        Returns:
            int: The numberof current jobs
        """
        cmd = ["squeue", "-r", "--noheader", "-p", self.settings.scheduler_queue, "-n", self.settings.scheduler_job_name]
        proc = exec_cmd(cmd, log_level="debug")
        lines = proc.stdout.splitlines()
        num = len(lines)
        return num

    def get_submit_cmd(self, num_pages):
        """Generates a sbatch command

        Based on settings a sbatch command is generated.

        Args:
            num_pages (int): Number of pages being scheduled

        Returns:
            list: The command to be executed
        """
        cmd = [
            "sbatch", "--parsable",
            "-p", self.settings.scheduler_queue,
            "-J", self.settings.scheduler_job_name,
            "-o", self.settings.scheduler_logfile,
            "--mem-per-cpu", self.settings.scheduler_mem_per_cpu,
            "--cpus-per-task", self.settings.scheduler_cpus_per_task,
        ]
        # Set walltime if configured to do so
        if self.settings.scheduler_set_walltime:
            walltime_seconds = self.walltime(num_pages)
            # Convert walltime from seconds to minutes
            walltime_minutes = int(walltime_seconds / 60)
            cmd.append("--time")
            cmd.append(str(walltime_minutes))
        extra_args = self.settings.scheduler_extra_args
        if extra_args:
            cmd.append(extra_args)
        cmd.append("emop.slrm")
        return cmd

    def submit_job(self, proc_id, num_pages):
        """Submit a job to SLURM

        Before the job is submitted some environment variables are set
        which are then used by SLURM.

        ``PROC_ID`` tells the SLURM job which JSON file to load.
        ``EMOP_CONFIG_PATH`` tells the SLURM job which INI file should be used.

        Args:
            proc_id (str or int): proc_id to be used by submitted job
            num_pages (int): Number of pages being scheduled

        Returns:
            bool: True if successful, False otherwise.
        """
        if not proc_id:
            logger.error("EmopSLURM#submit_job(): Must provide valid proc_id.")
            return False

        os.environ['PROC_ID'] = proc_id
        os.environ['EMOP_CONFIG_PATH'] = self.settings.config_path
        cmd = self.get_submit_cmd(num_pages)
        proc = exec_cmd(cmd, log_level="debug")
        if proc.exitcode != 0:
            logger.error("Failed to submit job to SLURM: %s" % proc.stderr)
            return False
        slurm_job_id = proc.stdout.rstrip()
        logger.info("SLURM job %s submitted for PROC_ID %s" % (slurm_job_id, proc_id))
        return True
