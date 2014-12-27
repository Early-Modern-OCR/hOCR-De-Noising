from emop.lib.models.emop_model import EmopModel


class EmopWork(EmopModel):

    def __init__(self):
        super(self.__class__, self).__init__()

    def setattrs(self, dictionary):
        self.id = dictionary["id"]
        self.organizational_unit = dictionary["wks_organizational_unit"]
        self.title = dictionary["wks_title"]
        self.ecco_id = dictionary["wks_ecco_number"]
        self.ecco_directory = dictionary["wks_ecco_directory"]
        self.eebo_id = dictionary["wks_eebo_image_id"]
        self.eebo_directory = dictionary["wks_eebo_directory"]

    def is_ecco(self):
        if self.ecco_directory:
            return True
        else:
            return False
