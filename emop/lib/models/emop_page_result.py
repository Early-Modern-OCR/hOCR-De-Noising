from emop.lib.emop_base import EmopBase
from emop.lib.models.emop_model import EmopModel


class EmopPageResult(EmopModel):

    def __init__(self, settings):
        super(self.__class__, self).__init__(settings)
        self._ocr_text_path = None
        self._ocr_xml_path = None
        self._corr_ocr_text_path = None
        self._corr_ocr_xml_path = None
        self.page_id = None
        self.batch_id = None
        self.juxta_change_index = None
        self.alt_change_index = None

    def setattrs(self, dictionary):
        pass

    def to_dict(self):
        _dict = {
            'page_id': self.page_id,
            'batch_id': self.batch_id,
            'ocr_text_path': self.ocr_text_path,
            'ocr_xml_path': self.ocr_xml_path,
            'corr_ocr_text_path': self.corr_ocr_text_path,
            'corr_ocr_xml_path': self.corr_ocr_xml_path,
            'juxta_change_index': self.juxta_change_index,
            'alt_change_index': self.alt_change_index,
        }
        return _dict

    @property
    def ocr_text_path(self):
        """The path to text OCR output"""
        return self._ocr_text_path

    @ocr_text_path.setter
    def ocr_text_path(self, value):
        prefix = self.settings.output_path_prefix
        new_value = EmopBase.remove_prefix(prefix=prefix, path=value)
        self._ocr_text_path = new_value

    @property
    def ocr_xml_path(self):
        """The path to XML OCR output"""
        return self._ocr_xml_path

    @ocr_xml_path.setter
    def ocr_xml_path(self, value):
        prefix = self.settings.output_path_prefix
        new_value = EmopBase.remove_prefix(prefix=prefix, path=value)
        self._ocr_xml_path = new_value

    @property
    def corr_ocr_text_path(self):
        """The path to corrected text OCR output"""
        return self._corr_ocr_text_path

    @corr_ocr_text_path.setter
    def corr_ocr_text_path(self, value):
        prefix = self.settings.output_path_prefix
        new_value = EmopBase.remove_prefix(prefix=prefix, path=value)
        self._corr_ocr_text_path = new_value

    @property
    def corr_ocr_xml_path(self):
        """The path to corrected XML OCR output"""
        return self._corr_ocr_xml_path

    @corr_ocr_xml_path.setter
    def corr_ocr_xml_path(self, value):
        prefix = self.settings.output_path_prefix
        new_value = EmopBase.remove_prefix(prefix=prefix, path=value)
        self._corr_ocr_xml_path = new_value
