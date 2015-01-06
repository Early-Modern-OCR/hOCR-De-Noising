from emop.lib.models.emop_model import EmopModel


class EmopPostprocResult(EmopModel):

    def __init__(self, settings):
        super(self.__class__, self).__init__(settings)
        self.page_id = None
        self.batch_id = None
        self.pp_noisemsr = None
        self.pp_juxta = None
        self.pp_health = None
        self.pp_ecorr = None
        self.pp_stats = None
        self.pp_retas = None

    def setattrs(self, dictionary):
        pass

    def to_dict(self):
        _dict = {
            'page_id': self.page_id,
            'batch_job_id': self.batch_job_id,
            'pp_noisemsr': self.pp_noisemsr,
            'pp_juxta': self.pp_juxta,
            'pp_health': self.pp_health,
            'pp_ecorr': self.pp_ecorr,
            'pp_stats': self.pp_stats,
            'pp_retas': self.pp_retas,
        }
        return _dict
