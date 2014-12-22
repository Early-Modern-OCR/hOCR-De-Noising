import subprocess
import shlex
import collections
import os
import re
import logging
import logging.config
import time
from emop.lib.emop_settings import EmopSettings
from emop.lib.emop_api import EmopAPI
from emop.lib.emop_stdlib import EmopStdlib

logger = logging.getLogger('emop')


class EmopBase(object):

    def __init__(self, config_path):
        self.settings = EmopSettings(config_path)
        self.emop_api = EmopAPI(self.settings.url_base, self.settings.api_headers)
        os.environ['EMOP_HOME'] = self.settings.emop_home

        logging_level = getattr(logging, self.settings.log_level)
        # logging_format = '[%(asctime)s] %(levelname)s: %(message)s'
        # logging_datefmt = '%Y-%m-%dT%H:%M:%S'
        # logging.basicConfig(level=logging_level, format=logging_format, datefmt=logging_datefmt)
        # logging.getLogger('requests').setLevel(logging.WARNING)

        logging.config.fileConfig(config_path, disable_existing_loggers=True)
        logging.getLogger('emop').setLevel(logging_level)

        logger.debug("%s: %s" % (self.settings.__class__.__name__, EmopStdlib.to_JSON(self.settings)))

    @staticmethod
    def page_timing(func):
        def wrap(*args, **kwargs):
            start = time.time()
            ret = func(*args, **kwargs)
            elapsed = time.time() - start
            logger.info("Job [%s] COMPLETE: Duration: %0.3f secs" % (kwargs.get('job').id, elapsed))
            return ret
        return wrap

    @staticmethod
    def job_timing(func):
        def wrap(*args, **kwargs):
            start = time.time()
            ret = func(*args, **kwargs)
            elapsed = time.time() - start
            logger.info("TOTAL TIME: %0.3f" % elapsed)
            return ret
        return wrap

    @staticmethod
    def add_prefix(prefix, path):
        # TODO: may be necessary
        # if not prefix or not path:
        #     return None
        relative_path = re.sub("^/", "", path)
        full_path = os.path.join(prefix, relative_path)
        return full_path

    @staticmethod
    def exec_cmd(cmd, log_level="info"):
        if isinstance(cmd, basestring):
            cmd_str = cmd
            cmd = shlex.split(cmd)
        else:
            cmd_str = " ".join(cmd)

        try:
            getattr(logger, log_level)("Executing: '%s'" % cmd_str)
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ)
            process.wait()
            out, err = process.communicate()
            # TODO: set timeout??
            retval = process.returncode

            proc = collections.namedtuple('Proc', ['stdout', 'stderr', 'exitcode'])
            return proc(stdout=out, stderr=err, exitcode=retval)
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                logger.error("File not found for command: %s" % e.message)
                return proc(stdout=None, stderr=None, exitcode=1)
            else:
                raise
