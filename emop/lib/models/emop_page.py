from emop.lib.emop_base import EmopBase
from emop.lib.models.emop_model import EmopModel


class EmopPage(EmopModel):

    def __init__(self, settings):
        super(self.__class__, self).__init__(settings)
        self._ground_truth_file = None

    def setattrs(self, dictionary):
        self.id = dictionary["id"]
        self.number = dictionary["pg_ref_number"]
        self.image_path = dictionary["pg_image_path"]
        self.gale_ocr_file = dictionary["pg_gale_ocr_file"]
        self.ground_truth_file = dictionary["pg_ground_truth_file"]

    def hasGroundTruth(self):
        if self.ground_truth_file:
            return True
        else:
            return False

    def hasGaleText(self):
        if self.gale_ocr_file:
            return True
        else:
            return False

    @property
    def ground_truth_file(self):
        """The path to the page's ground truth file"""
        return self._ground_truth_file

    @ground_truth_file.setter
    def ground_truth_file(self, value):
        prefix = self.settings.input_path_prefix
        new_value = EmopBase.add_prefix(prefix=prefix, path=value)
        self._ground_truth_file = new_value
