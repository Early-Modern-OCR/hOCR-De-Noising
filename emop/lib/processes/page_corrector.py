import collections
import glob
import json
import os
from emop.lib.emop_base import EmopBase
from emop.lib.processes.processes_base import ProcessesBase


class PageCorrector(ProcessesBase):

    def __init__(self, job):
        super(self.__class__, self).__init__(job)
        self.home = os.environ["SEASR_HOME"]
        self.executable = os.path.join(self.home, "PageCorrector.jar")
        self.cfg = os.path.join(os.environ["EMOP_HOME"], "emop.properties")
        self.dicts_dir = os.path.join(self.home, "dictionaries")
        self.rules_file = os.path.join(self.home, "rules", "transformations.json")

    def run(self):
        Results = collections.namedtuple('Results', ['stdout', 'stderr', 'exitcode'])

        if not self.job.xml_file or not os.path.isfile(self.job.xml_file):
            stderr = "PageCorrector Error: Could not find XML file"
            return Results(stdout=None, stderr=stderr, exitcode=1)

        # TODO Move -Xms and -Xmx into config.ini
        cmd = [
            "java", "-Xms128M", "-Xmx512M", "-jar", self.executable, "--dbconf", self.cfg,
            "-t", self.rules_file, "-o", self.job.output_dir, "--stats", "--dict"
        ]
        for file in glob.glob("%s/*.dict" % self.dicts_dir):
            cmd.append(file)

        cmd.append("--")
        cmd.append(self.job.xml_file)
        proc = EmopBase.exec_cmd(cmd)

        if proc.exitcode != 0:
            # TODO: PageCorrector errors are going to stdout not stderr
            stderr = "PageCorrector failed: %s" % proc.stdout
            return Results(stdout=proc.stdout, stderr=stderr, exitcode=proc.exitcode)

        out = proc.stdout.strip()

        # Check that output is valid JSON
        try:
            json.loads(out)
        except ValueError:
            stderr = "PageCorrector Error: output is not valid JSON"
            return Results(stdout=None, stderr=stderr, exitcode=1)

        self.job.postproc_result.pp_health = out
        return Results(stdout=None, stderr=None, exitcode=0)
