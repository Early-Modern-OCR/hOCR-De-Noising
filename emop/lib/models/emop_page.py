from emop.lib.models.emop_model import EmopModel


class EmopPage(EmopModel):

    def __init__(self, settings):
        super(self.__class__, self).__init__(settings)

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
