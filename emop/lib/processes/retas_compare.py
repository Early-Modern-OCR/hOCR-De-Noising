import collections
import os
import re
from emop.lib.emop_base import EmopBase
from emop.lib.processes.processes_base import ProcessesBase


class RetasCompare(ProcessesBase):

    def __init__(self, job):
        super(self.__class__, self).__init__(job)
        self.home = self.job.settings.retas_home
        self.executable = os.path.join(self.home, "retas.jar")
        self.cfg = os.path.join(self.home, "config.txt")

    def run(self, postproc):
        Results = collections.namedtuple('Results', ['stdout', 'stderr', 'exitcode'])

        if not self.job.page.hasGroundTruth():
            return Results(stdout=None, stderr=None, exitcode=0)

        if postproc:
            input_file = self.job.alto_txt_file
        else:
            input_file = self.job.idhmc_txt_file

        if not input_file or not os.path.isfile(input_file):
            stderr = "Could not find RetasCompare input file: %s" % input_file
            return Results(stdout=None, stderr=stderr, exitcode=1)

        cmd = [
            "java", "-Xms128M", "-Xmx128M", "-jar", self.executable, self.job.page.ground_truth_file, input_file,
            "-opt", self.cfg
        ]
        proc = EmopBase.exec_cmd(cmd)
        if proc.exitcode != 0:
            stderr = "RetasCompare of %s failed: %s" % (input_file, proc.stderr)
            return Results(stdout=proc.stdout, stderr=stderr, exitcode=proc.exitcode)

        out = proc.stdout.strip()
        values = re.split(r"\t", out)
        value = float(values[-1])

        if postproc:
            # self.job.postproc_result.pp_retas = value
            self.job.page_result.alt_change_index = value
        # else:
        #     self.job.page_result.alt_change_index = value

        return Results(stdout=None, stderr=None, exitcode=0)
