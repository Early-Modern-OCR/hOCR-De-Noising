import subprocess
import shlex
import collections
import os
import re
import logging
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

        logging_format = '[%(asctime)s] %(levelname)s: %(message)s'
        logging_level = getattr(logging, self.settings.log_level)
        logging_datefmt = '%Y-%m-%dT%H:%M:%S'
        logger = logging.getLogger('emop')
        logger.setLevel(logging_level)
        logger_handler = logging.StreamHandler()
        logger_handler.setLevel(logging_level)
        logger_formatter = logging.Formatter(logging_format)
        logger_handler.setFormatter(logger_formatter)
        logger.addHandler(logger_handler)
        
        logger.debug("%s: %s" % (self.settings.__class__.__name__, EmopStdlib.to_JSON(self.settings)))

    @staticmethod
    def timing(func):
        def wrap(*args, **kwargs):
            start = time.time()
            ret = func(*args, **kwargs)
            elapsed = time.time() - start
            print "DEBUG: %s" % start
            print "DEBUG: %s" % elapsed
            logger.info("TOTAL TIME: %0.3f" % elapsed)
            return ret
        return wrap

    @staticmethod
    def add_prefix(prefix, path):
        relative_path = re.sub("^/", "", path)
        full_path = os.path.join(prefix, relative_path)
        return full_path

    @staticmethod
    def exec_cmd(cmd):
        if isinstance(cmd, basestring):
            cmd_str = cmd
            cmd = shlex.split(cmd)
        else:
            cmd_str = " ".join(cmd)

        try:
            logger.info("Executing: '%s'" % cmd_str)
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
