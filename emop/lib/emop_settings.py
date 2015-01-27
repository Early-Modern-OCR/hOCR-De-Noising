import ConfigParser
import json
import os

# TODO: Need sane defaults for all settings
defaults = {
    "controller": {
        "scheduler": "slurm",
        "skip_existing": True
    },
    "scheduler": {
        "mem_per_cpu": "4000",
        "cpus_per_task": "1",
        "set_walltime": False,
        "extra_args": '[]',
    },
    "multi-column-skew": {
        "enabled": True,
    },
    "page-corrector": {
        "java_args": '["-Xms128M", "-Xmx512M"]',
        "alt_arg": "2",
        "max_transforms": "20",
        "noise_cutoff": "0.5",
        "ctx_min_match": None,
        "ctx_min_vol": None,
        "timeout": -1,
    },
    "page-evaluator": {
        "java_args": '["-Xms128M", "-Xmx128M"]',
    },
}


class EmopSettings(object):

    def __init__(self, config_path):
        self.config_path = config_path
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_path)

        # Settings based on environment variables
        if os.getenv("EMOP_HOME"):
            self.emop_home = os.getenv("EMOP_HOME")
        else:
            self.emop_home = os.path.dirname(self.config_path)
        if os.getenv("DENOISE_HOME"):
            self.denoise_home = os.getenv("DENOISE_HOME")
        else:
            raise RuntimeError("DENOISE_HOME environment variable not set")
        if os.getenv("SEASR_HOME"):
            self.seasr_home = os.getenv("SEASR_HOME")
        else:
            raise RuntimeError("SEASR_HOME environment variable not set")
        if os.getenv("JUXTA_HOME"):
            self.juxta_home = os.getenv("JUXTA_HOME")
        else:
            raise RuntimeError("JUXTA_HOME environment variable not set")
        if os.getenv("RETAS_HOME"):
            self.retas_home = os.getenv("RETAS_HOME")
        else:
            raise RuntimeError("RETAS_HOME environment variable not set")

        # Settings for communicating with dashboard
        self.api_version = self.get_value('dashboard', 'api_version')
        self.url_base = self.get_value('dashboard', 'url_base')
        self.auth_token = self.get_value('dashboard', 'auth_token')
        self.api_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/emop; version=%s' % self.api_version,
            'Authorization': 'Token token=%s' % self.auth_token,
        }

        # Settings used by controller
        self.payload_input_path = self.get_value('controller', 'payload_input_path')
        self.payload_output_path = self.get_value('controller', 'payload_output_path')
        self.payload_completed_path = os.path.join(self.payload_output_path, "completed")
        self.payload_uploaded_path = os.path.join(self.payload_output_path, "uploaded")
        self.ocr_root = self.get_value('controller', 'ocr_root')
        self.input_path_prefix = self.get_value('controller', 'input_path_prefix')
        self.output_path_prefix = self.get_value('controller', 'output_path_prefix')
        self.log_level = self.get_value('controller', 'log_level')
        self.scheduler = self.get_value('controller', 'scheduler')
        self.controller_skip_existing = self.get_bool_value('controller', 'skip_existing')

        # Settings used to interact with the cluster scheduler
        self.max_jobs = int(self.get_value('scheduler', 'max_jobs'))
        self.scheduler_queue = self.get_value('scheduler', 'queue')
        self.scheduler_job_name = self.get_value('scheduler', 'name')
        self.min_job_runtime = int(self.get_value('scheduler', 'min_job_runtime'))
        self.max_job_runtime = int(self.get_value('scheduler', 'max_job_runtime'))
        self.avg_page_runtime = int(self.get_value('scheduler', 'avg_page_runtime'))
        self.scheduler_logdir = self.get_value('scheduler', 'logdir')
        self.scheduler_logfile = os.path.join(self.scheduler_logdir, "%s-%%j.out" % self.scheduler_job_name)
        self.scheduler_mem_per_cpu = self.get_value('scheduler', 'mem_per_cpu')
        self.scheduler_cpus_per_task = self.get_value('scheduler', 'cpus_per_task')
        self.scheduler_set_walltime = self.get_bool_value('scheduler', 'set_walltime')
        # Allow to fail if invalid type provided
        self.scheduler_extra_args = json.loads(self.get_value('scheduler', 'extra_args'))

        # Settings used by MultiColumnSkew
        self.multi_column_skew_enabled = self.get_bool_value('multi-column-skew', 'enabled')

        # Settings used by PageCorrector
        self.page_corrector_timeout = int(self.get_value('page-corrector', 'timeout'))

        # Settings used by Juxta-cl
        self.juxta_cl_jx_algorithm = self.get_value('juxta-cl', 'jx_algorithm')

    def get_value(self, section, option, default=None):
        """Get settings value

        This function is a warper for ConfigParser.get() that
        handles missing values and substitutes them for defaults set
        in a dict within global space of EmopSettings.

        Interpolation is performed on specific items found in %() within
        the INI file.

        ``home`` - HOME environment variable
        ``emop_home`` - The emop_home setting value

        Args:
            section (str): INI file section
            option (str): INI file option name
            default (str): Default value if one is not found.
            Defaults to None.

        Returns:
            str: The config value
        """
        interpolation_map = {
            "home": os.getenv("HOME"),
            "emop_home": self.emop_home,
        }

        raw_value = None

        try:
            raw_value = self.config.get(section, option, raw=False, vars=interpolation_map)
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError) as e:
            if default:
                raw_value = default
            elif section in defaults:
                if option in defaults[section]:
                    raw_value = defaults[section][option]
                else:
                    raise e

        return raw_value

    def get_bool_value(self, section, option, default=None):
        """Get settings bool value

        This function is a warper for RawConfigParser.getboolean() that
        handles missing values and substitutes them for defaults set
        in a dict within global space of EmopSettings.

        Args:
            section (str): INI file section
            option (str): INI file option name
            default (str): Default value if one is not found.
            Defaults to None.

        Returns:
            bool: The config value
        """
        bool_value = None

        try:
            bool_value = self.config.getboolean(section, option)
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError) as e:
            if default:
                bool_value = default
            elif section in defaults:
                if option in defaults[section]:
                    bool_value = defaults[section][option]
                else:
                    raise e

        return bool_value
