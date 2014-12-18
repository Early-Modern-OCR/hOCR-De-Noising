import collections
import os
from emop.lib.emop_base import EmopBase
from emop.lib.processes.processes_base import ProcessesBase


class PageEvaluator(ProcessesBase):

    def __init__(self, job):
        super(self.__class__, self).__init__(job)
        self.home = os.environ["SEASR_HOME"]
        self.executable = os.path.join(self.home, "PageEvaluator.jar")

    def run(self):
        Results = collections.namedtuple('Results', ['stdout', 'stderr', 'exitcode'])

        if not self.xml_file or not os.path.isfile(self.xml_file):
            stderr = "PageEvaluator Error: Could not find XML file"
            return Results(stdout=None, stderr=stderr, exitcode=1)

        # TODO Move -Xms and -Xmx into config.ini
        cmd = ["java", "-Xms128M", "-Xmx128M", "-jar", self.executable, "-q", self.xml_file]
        proc = EmopBase.exec_cmd(cmd)

        if proc.exitcode != 0:
            stderr = "PageEvaluator Failed: %s" % proc.stderr
            return Results(stdout=proc.stdout, stderr=stderr, exitcode=proc.exitcode)

        out = proc.stdout.strip()
        scores = out.split(",")

        if len(scores) != 2:
            stderr = "PageEvaluator Error: unexpected response format: %s" % out
            return Results(stdout=None, stderr=stderr, exitcode=1)

        self.job.postproc_result.pp_ecorr = scores[0]
        self.job.postproc_result.pp_stats = scores[1]
        return Results(stdout=None, stderr=None, exitcode=0)
