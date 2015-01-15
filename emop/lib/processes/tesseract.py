import logging
import os
from emop.lib.emop_base import EmopBase
from emop.lib.processes.processes_base import ProcessesBase

logger = logging.getLogger('emop')


class Tesseract(ProcessesBase):

    def __init__(self, job):
        super(self.__class__, self).__init__(job)
        self.cfg = os.path.join(os.environ["EMOP_HOME"], "tess_cfg.txt")

    def run(self):
        if not self.job.image_path:
            stderr = "No image path could be determined"
            return self.results(stdout=None, stderr=stderr, exitcode=1)
        if not os.path.isfile(self.job.image_path):
            stderr = "Could not find page image %s" % self.job.image_path
            return self.results(stdout=None, stderr=stderr, exitcode=1)

        output_parent_dir = os.path.dirname(self.job.xml_file)
        if not os.path.isdir(output_parent_dir):
            EmopBase.mkdirs_exists_ok(output_parent_dir)

        # Strip file extension, tesseract auto-appends it
        output_filename, output_extension = os.path.splitext(self.job.xml_file)

        cmd = ["tesseract", self.job.image_path, output_filename, "-l", self.job.font.name, self.cfg]
        proc = EmopBase.exec_cmd(cmd)

        if proc.exitcode != 0:
            return self.results(stdout=proc.stdout, stderr=proc.stderr, exitcode=proc.exitcode)

        # Rename hOCR file to XML
        if os.path.isfile(self.job.hocr_file) and not os.path.isfile(self.job.xml_file):
            logger.debug("Renaming %s to %s" % (self.job.hocr_file, self.job.xml_file))
            os.rename(self.job.hocr_file, self.job.xml_file)

        self.job.page_result.ocr_text_path = self.job.txt_file
        self.job.page_result.ocr_xml_path = self.job.xml_file
        return self.results(stdout=None, stderr=None, exitcode=0)
