from emop.lib.models.emop_model import EmopModel


class EmopFont(EmopModel):

    def __init__(self, settings):
        super(self.__class__, self).__init__(settings)

    def setattrs(self, dictionary):
        self.name = dictionary["font_name"]
