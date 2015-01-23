import logging
import os
from emop.lib.processes.processes_base import ProcessesBase
from emop.lib.utilities import mkdirs_exists_ok, exec_cmd

logger = logging.getLogger('emop')


class Tesseract(ProcessesBase):

    def __init__(self, job):
        super(self.__class__, self).__init__(job)
        self.cfg = os.path.join(self.job.settings.emop_home, "tess_cfg.txt")
        # Strip file extension, tesseract auto-appends it
        output_filename, output_extension = os.path.splitext(self.job.xml_file)
        self.output_filename = output_filename
        self.output_parent_dir = os.path.dirname(self.job.xml_file)

    def should_run(self):
        if (self.job.txt_file and os.path.isfile(self.job.txt_file)) \
        and (self.job.xml_file and os.path.isfile(self.job.xml_file)):
            return False
        else:
            return True

    def run(self):
        if not self.job.image_path:
            stderr = "No image path could be determined"
            return self.results(stdout=None, stderr=stderr, exitcode=1)
        if not os.path.isfile(self.job.image_path):
            stderr = "Could not find page image %s" % self.job.image_path
            return self.results(stdout=None, stderr=stderr, exitcode=1)

        # Create output parent directory if it doesn't exist
        if not os.path.isdir(self.output_parent_dir):
            mkdirs_exists_ok(self.output_parent_dir)

        cmd = ["tesseract", self.job.image_path, self.output_filename, "-l", self.job.font.name, self.cfg]
        proc = exec_cmd(cmd)

        if proc.exitcode != 0:
            return self.results(stdout=proc.stdout, stderr=proc.stderr, exitcode=proc.exitcode)

        # Rename hOCR file to XML
        if os.path.isfile(self.job.hocr_file) and not os.path.isfile(self.job.xml_file):
            logger.debug("Renaming %s to %s" % (self.job.hocr_file, self.job.xml_file))
            os.rename(self.job.hocr_file, self.job.xml_file)

        self.job.page_result.ocr_text_path = self.job.txt_file
        self.job.page_result.ocr_xml_path = self.job.xml_file
        return self.results(stdout=None, stderr=None, exitcode=0)
