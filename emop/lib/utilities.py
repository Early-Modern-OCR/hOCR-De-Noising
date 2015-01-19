import collections
import logging
import os
import shlex
import subprocess
import sys

logger = logging.getLogger('emop')


def get_temp_dir():
    """Gets the temp directory based on environment variables

    Currently searched environment variables:
        * TMPDIR

    Returns:
        str: Path to temp directory.
    """
    env_vars = [
        'TMPDIR',
    ]
    tmp_dir = None

    for env_var in env_vars:
        if os.environ.get(env_var):
            tmp_dir = os.environ.get(env_var)
            logger.debug("Using temp directory %s" % tmp_dir)
            return tmp_dir
    if not tmp_dir:
        logger.error("Temporary directory could not be found.")
    return tmp_dir

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
