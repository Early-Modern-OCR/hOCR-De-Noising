from emop.models.emop_model import EmopModel


class EmopFont(EmopModel):

    def __init__(self):
        super(self.__class__, self).__init__()

    def setattrs(self, dictionary):
        self.name = dictionary["font_name"]
