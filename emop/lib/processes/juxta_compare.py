import os
from emop.lib.utilities import exec_cmd
from emop.lib.processes.processes_base import ProcessesBase


class JuxtaCompare(ProcessesBase):

    def __init__(self, job):
        super(self.__class__, self).__init__(job)
        self.home = self.job.settings.juxta_home
        self.executable = os.path.join(self.home, "juxta-cl.jar")
        self.jx_algorithm = self.job.settings.juxta_cl_jx_algorithm

    def run(self, postproc):
        if not self.job.page.hasGroundTruth():
            return self.results(stdout=None, stderr=None, exitcode=0)

        if postproc:
            input_file = self.job.alto_txt_file
        else:
            input_file = self.job.idhmc_txt_file

        if not input_file or not os.path.isfile(input_file):
            stderr = "Could not find JuxtaCompare input file: %s" % input_file
            return self.results(stdout=None, stderr=stderr, exitcode=1)

        cmd = [
            "java", "-Xms128M", "-Xmx128M", "-jar", self.executable,
            "-diff", self.job.page.ground_truth_file, input_file,
            "-algorithm", self.jx_algorithm, "-hyphen", "none"
        ]

        proc = exec_cmd(cmd)
        if proc.exitcode != 0:
            stderr = "JuxtaCompare of %s failed: %s" % (input_file, proc.stderr)
            return self.results(stdout=proc.stdout, stderr=stderr, exitcode=proc.exitcode)

        out = proc.stdout.strip()

        # Handle invalid values returned by Juxta
        if out == 'NaN':
            value = '-1'
        else:
            value = float(out)

        if postproc:
            # self.job.postproc_result.pp_juxta = value
            self.job.page_result.juxta_change_index = value
        # else:
        #     self.job.page_result.juxta_change_index = value

        return self.results(stdout=None, stderr=None, exitcode=0)
