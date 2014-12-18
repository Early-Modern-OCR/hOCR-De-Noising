import collections
import os
from emop.lib.emop_base import EmopBase
from emop.lib.processes.processes_base import ProcessesBase


class Denoise(ProcessesBase):

    def __init__(self, job):
        super(self.__class__, self).__init__(job)
        self.home = os.environ["DENOISE_HOME"]
        self.executable = os.path.join(self.home, "deNoise_Post.py")

    def run(self):
        Results = collections.namedtuple('Results', ['stdout', 'stderr', 'exitcode'])

        if not self.xml_file or not os.path.isfile(self.xml_file):
            stderr = "Denoise: Could not find XML file"
            return Results(stdout=None, stderr=stderr, exitcode=1)

        # This adds a trailing /
        self.xml_file_dir = os.path.join(self.output_dir, '')
        self.xml_filename = os.path.basename(self.xml_file)

        cmd = ["python", self.executable, "-p", self.xml_file_dir, "-n", self.xml_filename]
        proc = EmopBase.exec_cmd(cmd)

        if proc.exitcode != 0:
            stderr = "DeNoise failed: %s" % proc.stderr
            return Results(stdout=proc.stdout, stderr=stderr, exitcode=proc.exitcode)

        return Results(stdout=None, stderr=None, exitcode=0)
