import ConfigParser
import os


# TODO: Need sane defaults for some settings
class EmopSettings(object):

    def __init__(self, config_path):
        self.config_path = config_path
        config = ConfigParser.ConfigParser()
        config.read(self.config_path)

        self.emop_home = os.path.dirname(config_path)

        # Settings for communicating with dashboard
        self.api_version = config.get('dashboard', 'api_version')
        self.url_base = config.get('dashboard', 'url_base')
        self.auth_token = config.get('dashboard', 'auth_token')
        self.api_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/emop; version=%s' % self.api_version,
            'Authorization': 'Token token=%s' % self.auth_token,
        }

        # Settings used by controller
        self.payload_input_path = config.get('controller', 'payload_input_path')
        self.payload_output_path = config.get('controller', 'payload_output_path')
        self.ocr_root = config.get('controller', 'ocr_root')
        self.input_path_prefix = config.get('controller', 'input_path_prefix')
        self.output_path_prefix = config.get('controller', 'output_path_prefix')
        self.log_level = config.get('controller', 'log_level')

        # Settings used to interact with the cluster scheduler
        self.max_jobs = int(config.get('scheduler', 'max_jobs'))
        self.slurm_queue = config.get('scheduler', 'queue')
        self.slurm_job_name = config.get('scheduler', 'name')
        self.min_job_runtime = int(config.get('scheduler', 'min_job_runtime'))
        self.max_job_runtime = int(config.get('scheduler', 'max_job_runtime'))
        self.avg_page_runtime = int(config.get('scheduler', 'avg_page_runtime'))
        self.slurm_logdir = config.get('scheduler', 'logdir')
        self.slurm_logfile = os.path.join(self.slurm_logdir, "%s-%%j.out" % self.slurm_job_name)

        # Settings used by Juxta-cl
        self.juxta_cl_jx_algorithm = config.get('juxta-cl', 'jx_algorithm')
