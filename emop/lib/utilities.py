import collections
import errno
import logging
import os
import shlex
import signal
import subprocess

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


def exec_cmd(cmd, log_level="info", timeout=-1):
    """Executes a command

    This is the method used by this application to execute
    shell commands.

    If the cmd argument can be a 2D list but only one level deep.

    The command's stdout, stderr and exitcode are turned as a namedtuple.

    Args:
        cmd (str or list): Command to execute
        log_level (str, optional): log level when printing information
            about the command being executed.
        timeout (int, optional): The time in seconds the command should
            be allowed to run before timing out.

    Returns:
        tuple: (stdout, stderr, exitcode)
    """
    # REF: http://stackoverflow.com/a/3326559
    class Alarm(Exception):
        pass
    def alarm_handler(signum, frame):
        raise Alarm

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

    if timeout != -1:
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(timeout)

    try:
        getattr(logger, log_level)("Executing: '%s'" % cmd_str)
        # TODO Eventually may just need to redirect all stderr to stdout for simplicity
        # process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=os.environ)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ)
        process.wait()
        out, err = process.communicate()
        if timeout != -1:
            signal.alarm(0)
        # TODO: set timeout??
        retval = process.returncode

        return Proc(stdout=out, stderr=err, exitcode=retval)
    except Alarm:
        process.kill()
        timeout_msg = "Command timed out"
        return Proc(stdout=timeout_msg, stderr=timeout_msg, exitcode=1)
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            error_msg = "File not found for command: %s" % e
            return Proc(stdout=error_msg, stderr=error_msg, exitcode=1)
        else:
            raise

def get_process_children(pid):
    p = subprocess.Popen('ps --no-headers -o pid --ppid %d' % pid, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    return [int(p) for p in stdout.split()]
