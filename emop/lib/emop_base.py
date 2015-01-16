import errno
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
# from emop.lib.emop_stdlib import EmopStdlib

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

        # logger.debug("%s: %s" % (self.settings.__class__.__name__, EmopStdlib.to_JSON(self.settings)))

    @staticmethod
    def run_timing(func):
        """Decorator used to time a function

        This decorator is intended to be used by functions in
        EmopRun.  The functions should return only bool values.

        The purpose of this decorator is to print the time it takes
        a function to run.
        """
        def wrap(*args, **kwargs):
            klass = args[0].__class__.__name__
            func_name = func.func_name

            # Condition to get the class of EmopRun.do_process
            if kwargs.get('obj'):
                name = kwargs.get('obj').__class__.__name__
                item = kwargs.get('job').id
            # Condition for EmopRun.do_ocr
            elif func_name == "do_ocr":
                name = "OCR"
                item = kwargs.get('job').id
            # Condition for EmopRun.run
            elif klass == "EmopRun" and func_name == "run":
                name = "Total"
                item = None
            # Condition for EmopRun.do_job
            else:
                name = "Job"
                item = kwargs.get('job').id

            start = time.time()
            ret = func(*args, **kwargs)
            # If the function returns False or None
            # do not print the completed time
            if not ret:
                return ret
            elapsed = time.time() - start
            if name == "Total":
                logger.info("TOTAL TIME: %0.3f" % elapsed)
            else:
                logger.info("%s [%s] COMPLETE: Duration: %0.3f secs" % (name, item, elapsed))
            return ret
        return wrap

    @staticmethod
    def add_prefix(prefix, path):
        """Add prefix to a path

        Args:
            prefix (str): Path prefix
            path (str): Path to add prefix

        Returns:
            str: The prefix + path.
            None is returned if prefix or path are not present.
        """
        if not prefix or not path:
            return None
        relative_path = re.sub("^/", "", path)
        full_path = os.path.join(prefix, relative_path)
        return full_path

    @staticmethod
    def remove_prefix(prefix, path):
        """Remove prefix from a path

        Args:
            prefix (str): Path prefix
            path (str): Path to remove prefix from

        Returns:
            str: The path with prefix removed.
            None is returned if prefix or path are not present.
        """
        if not prefix or not path:
            return None
        if path.startswith(prefix):
            return path[len(prefix):]
        else:
            return path

    @staticmethod
    def mkdirs_exists_ok(path):
        """Wrapper for os.makedirs

        This function is needed to avoid race conditions
        when the directory exists when attempting to use
        os.makedirs.  This emulates the behavior of Python 3.x
        os.makedirs exist_ok argument.

        Args:
            path (str): Path of directory to create
        """
        try:
            os.makedirs(path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

    @staticmethod
    def exec_cmd(cmd, log_level="info"):
        """Executes a command

        This is the method used by this application to execute
        shell commands.

        If the cmd argument can be a 2D list but only one level deep.

        The command's stdout, stderr and exitcode are turned as a namedtuple.

        Args:
            cmd (str or list): Command to execute
            log_level (str, optional): log level when printing information
                about the command being executed.

        Returns:
            tuple: (stdout, stderr, exitcode)
        """
        Proc = collections.namedtuple('Proc', ['stdout', 'stderr', 'exitcode'])

        if isinstance(cmd, basestring):
            cmd_str = cmd
            cmd = shlex.split(cmd)
        elif isinstance(cmd, list):
            cmd_flat = []
            for i in cmd:
                if hasattr(i, '__iter__'):
                    for j in i:
                        cmd_flat.append(j)
                else:
                    cmd_flat.append(i)
            cmd = cmd_flat
            cmd_str = " ".join(cmd)

        try:
            getattr(logger, log_level)("Executing: '%s'" % cmd_str)
            # TODO Eventually may just need to redirect all stderr to stdout for simplicity
            # process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=os.environ)
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ)
            process.wait()
            out, err = process.communicate()
            # TODO: set timeout??
            retval = process.returncode

            return Proc(stdout=out, stderr=err, exitcode=retval)
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                logger.error("File not found for command: %s" % e)
                return Proc(stdout=None, stderr=None, exitcode=1)
            else:
                raise
