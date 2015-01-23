from emop.lib.emop_base import EmopBase
from emop.lib.models.emop_model import EmopModel


class EmopPageResult(EmopModel):

    PROPERTIES = [
        'page_id',
        'batch_id',
        'ocr_text_path',
        'ocr_xml_path',
        'corr_ocr_text_path',
        'corr_ocr_xml_path',
        'juxta_change_index',
        'alt_change_index',
    ]

    def __init__(self, settings):
        super(self.__class__, self).__init__(settings)
        self._ocr_text_path = None
        self._ocr_xml_path = None
        self._corr_ocr_text_path = None
        self._corr_ocr_xml_path = None
        for _property in self.PROPERTIES:
            setattr(self, _property, None)
            setattr(self, ("%s_exists" % _property), False)

    def set_existing_attrs(self, dictionary):
        if dictionary:
            for _property in self.PROPERTIES:
                if _property in dictionary:
                    setattr(self, ("%s_exists" % _property), True)

    def to_dict(self):
        _dict = {}
        for _property in self.PROPERTIES:
            value = getattr(self, _property)
            if value is None:
                continue
            _dict[_property] = value
        return _dict

    def has_data(self):
        keys = self.to_dict().keys()
        data_keys = set(keys) - set(["page_id", "batch_id"])
        if len(data_keys) >= 1:
            return True
        else:
            return False

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
