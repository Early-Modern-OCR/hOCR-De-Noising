import glob
import json
import os
from emop.lib.utilities import exec_cmd
from emop.lib.processes.processes_base import ProcessesBase


class PageCorrector(ProcessesBase):

    def __init__(self, job):
        super(self.__class__, self).__init__(job)
        self.home = self.job.settings.seasr_home
        self.executable = os.path.join(self.home, "PageCorrector.jar")
        self.cfg = os.path.join(self.job.temp_dir, "emop.properties")
        self.dicts_dir = os.path.join(self.home, "dictionaries")
        self.rules_file = os.path.join(self.home, "rules", "transformations.json")
        self.java_args = json.loads(self.job.settings.get_value('page-corrector', 'java_args'))
        self.alt_arg = self.job.settings.get_value('page-corrector', 'alt_arg')
        self.max_transforms = self.job.settings.get_value('page-corrector', 'max_transforms')
        self.noise_cutoff = self.job.settings.get_value('page-corrector', 'noise_cutoff')
        self.ctx_min_match = self.job.settings.get_value('page-corrector', 'ctx_min_match')
        self.ctx_min_vol = self.job.settings.get_value('page-corrector', 'ctx_min_vol')

    def should_run(self):
        if (self.job.postproc_result.pp_health_exists
                and self.job.page_result.corr_ocr_text_path_exists
                and self.job.page_result.corr_ocr_xml_path_exists):
            return False
        else:
            return True

    def run(self):
        if not self.job.xml_file or not os.path.isfile(self.job.xml_file):
            stderr = "Could not find XML file: %s" % self.job.xml_file
            return self.results(stdout=None, stderr=stderr, exitcode=1)

        dict_files = glob.glob("%s/*.dict" % self.dicts_dir)
        cmd = [
            "java", self.java_args, "-jar", self.executable, "--dbconf", self.cfg,
            "-t", self.rules_file, "-o", self.job.output_dir, "--stats",
            "--alt", self.alt_arg, "--max-transforms", self.max_transforms, "--noiseCutoff", self.noise_cutoff,
            "--dict", dict_files
        ]
        if self.ctx_min_match:
            cmd.append("--ctx-min-match")
            cmd.append(self.ctx_min_match)
        if self.ctx_min_vol:
            cmd.append("--ctx-min-vol")
            cmd.append(self.ctx_min_vol)
        cmd.append("--")
        cmd.append(self.job.xml_file)
        proc = exec_cmd(cmd)

        if proc.exitcode != 0:
            # TODO: PageCorrector errors are going to stdout not stderr
            if not proc.stdout and proc.stderr:
                stderr = proc.stderr
            else:
                stderr = proc.stdout
            return self.results(stdout=proc.stdout, stderr=stderr, exitcode=proc.exitcode)

        out = proc.stdout.strip()

        # Check that output is valid JSON
        try:
            json.loads(out)
        except ValueError:
            stderr = "PageCorrector Error: output is not valid JSON"
            return self.results(stdout=None, stderr=stderr, exitcode=1)

        self.job.postproc_result.pp_health = out
        self.job.page_result.corr_ocr_text_path = self.job.alto_txt_file
        self.job.page_result.corr_ocr_xml_path = self.job.alto_xml_file
        return self.results(stdout=None, stderr=None, exitcode=0)
