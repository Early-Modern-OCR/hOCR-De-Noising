import logging
import os
import xml.etree.ElementTree as ET
from emop.lib.processes.processes_base import ProcessesBase

logger = logging.getLogger('emop')


class XML_To_Text(ProcessesBase):

    def __init__(self, job):
        super(self.__class__, self).__init__(job)

    def should_run(self):
        # TODO rest of steps rely on API data to know if they should run
        # but this step produces only a file, not output to API
        if self.job.idhmc_txt_file and os.path.isfile(self.job.idhmc_txt_file):
            return False
        else:
            return True

    def run(self):
        if not self.job.idhmc_xml_file or not os.path.isfile(self.job.idhmc_xml_file):
            stderr = "XML to Text: Could not find XML file"
            return self.results(stdout=None, stderr=stderr, exitcode=1)

        logger.info("XML_To_Text: Converting %s to %s" % (self.job.idhmc_xml_file, self.job.idhmc_txt_file))

        xml = ET.parse(self.job.idhmc_xml_file)

        lines = xml.findall(".//*[@class='ocr_line']")
        lines_text = []
        for line in lines:
            words = line.findall(".//*[@class='ocrx_word']")
            words_list = []
            for word in words:
                text = word.text or ""
                for sub_ele in word:
                    sub_ele_txt = sub_ele.text
                    if sub_ele_txt:
                        text += sub_ele_txt
                words_list.append(text)
            line_text = " ".join(filter(None, words_list))
            lines_text.append(line_text)

        # Try to encode to UTF-8 so that the writing does not throw exception
        try:
            text = "\n".join(lines_text).encode("utf-8")
        except UnicodeDecodeError:
            text = "\n".join(lines_text)

        # TODO Move file write operations to emop_base or emop_stdlib and handle encoding there
        with open(self.job.idhmc_txt_file, 'w') as txt_file:
            txt_file.write(text)

        return self.results(stdout=None, stderr=None, exitcode=0)
