import logging
import os
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
