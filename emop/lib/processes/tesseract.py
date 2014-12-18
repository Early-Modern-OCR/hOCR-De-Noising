import collections
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
        Results = collections.namedtuple('Results', ['stdout', 'stderr', 'exitcode'])

        if not self.image_path or not os.path.isfile(self.image_path):
            stderr = "Tesseract: Could not find page image"
            return Results(stdout=None, stderr=stderr, exitcode=1)

        # TODO: Remove once ready to run in production, this helps speed up testing
        if os.path.isfile(self.xml_file) and os.path.isfile(self.txt_file):
            self.job.page_result.ocr_text_path = self.txt_file
            self.job.page_result.ocr_xml_path = self.xml_file
            return Results(stdout=None, stderr=None, exitcode=0)

        output_parent_dir = os.path.dirname(self.xml_file)
        if not os.path.isdir(output_parent_dir):
            os.makedirs(output_parent_dir)

        # Strip file extension, tesseract auto-appends it
        output_filename, output_extension = os.path.splitext(self.xml_file)

        cmd = ["tesseract", self.image_path, output_filename, "-l", self.font.name, self.cfg]
        proc = EmopBase.exec_cmd(cmd)

        if proc.exitcode != 0:
            stderr = "Tesseract OCR Failed: %s" % proc.stderr
            Results(stdout=proc.stdout, stderr=stderr, exitcode=proc.exitcode)

        # Rename hOCR file to XML
        if os.path.isfile(self.hocr_file) and not os.path.isfile(self.xml_file):
            # TODO remove debug or only print if debug enabled
            logger.debug("Renaming %s to %s" % (self.hocr_file, self.xml_file))
            os.rename(self.hocr_file, self.xml_file)

        self.job.page_result.ocr_text_path = self.txt_file
        self.job.page_result.ocr_xml_path = self.xml_file
        return Results(stdout=None, stderr=None, exitcode=0)
