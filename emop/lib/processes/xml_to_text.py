import collections
import os
import xml.etree.ElementTree as ET
from emop.lib.processes.processes_base import ProcessesBase


class XML_To_Text(ProcessesBase):

    def __init__(self, job):
        super(self.__class__, self).__init__(job)

    def run(self):
        Results = collections.namedtuple('Results', ['stdout', 'stderr', 'exitcode'])

        if not self.idhmc_xml_file or not os.path.isfile(self.idhmc_xml_file):
            stderr = "XML to Text: Could not find XML file"
            return Results(stdout=None, stderr=stderr, exitcode=1)

        xml = ET.parse(self.idhmc_xml_file)

        # paragraphs = xml.findall(".//*[@class='ocr_par']/*")
        lines = xml.findall(".//*[@class='ocr_line']")
        # xml.findall(".//*[@class='ocrx_word']/*")

        text_lines = []
        for line in lines:
            words = line.findall(".//*[@class='ocrx_word']")
            line_words = []
            for word in words:
                s = word.text or ""
                for sub_ele in word:
                    s += ET.tostring(sub_ele, encoding="utf-8", method="text")
                # s += word.tail
                line_words.append(s)
            line_text = " ".join(filter(None, line_words))
            text_lines.append(line_text)

        text = "\n".join(text_lines)
        print text

        with open(self.idhmc_txt_file, 'w') as txt_file:
            txt_file.write(text)

        return Results(stdout=None, stderr=None, exitcode=0)
