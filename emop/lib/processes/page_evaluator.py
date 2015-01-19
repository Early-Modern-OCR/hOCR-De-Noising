import json
import os
from emop.lib.utilities import exec_cmd
from emop.lib.processes.processes_base import ProcessesBase


class PageEvaluator(ProcessesBase):

    def __init__(self, job):
        super(self.__class__, self).__init__(job)
        self.home = self.job.settings.seasr_home
        self.executable = os.path.join(self.home, "PageEvaluator.jar")
        self.java_args = json.loads(self.job.settings.get_value('page-evaluator', 'java_args'))

    def run(self):
        if not self.job.xml_file or not os.path.isfile(self.job.xml_file):
            stderr = "Could not find XML file: %s" % self.job.xml_file
            return self.results(stdout=None, stderr=stderr, exitcode=1)

        # TODO Move -Xms and -Xmx into config.ini
        cmd = ["java", self.java_args, "-jar", self.executable, "-q", self.job.xml_file]
        proc = exec_cmd(cmd)

        if proc.exitcode != 0:
            return self.results(stdout=proc.stdout, stderr=proc.stderr, exitcode=proc.exitcode)

        out = proc.stdout.strip()
        scores = out.split(",")

        if len(scores) != 2:
            stderr = "PageEvaluator Error: unexpected response format: %s" % out
            return self.results(stdout=None, stderr=stderr, exitcode=1)

        pp_ecorr = scores[0]
        pp_pg_quality = scores[1]

        # Handle invalid values returned by PageEvaluator
        if pp_ecorr == 'NaN':
            pp_ecorr = '-1'
        if pp_pg_quality == 'NaN':
            pp_pg_quality = '-1'

        self.job.postproc_result.pp_ecorr = pp_ecorr
        self.job.postproc_result.pp_pg_quality = pp_pg_quality
        return self.results(stdout=None, stderr=None, exitcode=0)
