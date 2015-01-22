import json
import os
from emop.lib.utilities import exec_cmd
from emop.lib.processes.processes_base import ProcessesBase


class MultiColumnSkew(ProcessesBase):

    def __init__(self, job):
        super(self.__class__, self).__init__(job)
        self.home = os.path.join(self.job.settings.emop_home, "lib/MultiColumnSkew")
        self.executable = os.path.join(self.home, "multiColDetect.py")

    def should_run(self):
        return True

    def run(self):
        if not self.job.idhmc_xml_file or not os.path.isfile(self.job.idhmc_xml_file):
            stderr = "Could not find XML file: %s" % self.job.idhmc_xml_file
            return self.results(stdout=None, stderr=stderr, exitcode=1)

        cmd = ["python", self.executable, self.job.idhmc_xml_file]
        proc = exec_cmd(cmd)

        if proc.exitcode != 0:
            return self.results(stdout=proc.stdout, stderr=proc.stderr, exitcode=proc.exitcode)

        out = proc.stdout.strip()

        # Check that output is valid JSON
        try:
            json_data = json.loads(out)
        except ValueError:
            stderr = "MultiColumnSkew Error: output is not valid JSON"
            return self.results(stdout=None, stderr=stderr, exitcode=1)

        self.job.postproc_result.multicol = json_data.get("multicol")
        self.job.postproc_result.skew_idx = json_data.get("skew_idx")

        return self.results(stdout=None, stderr=None, exitcode=0)
