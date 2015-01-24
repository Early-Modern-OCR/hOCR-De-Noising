from emop.lib.models.emop_model import EmopModel


class EmopPostprocResult(EmopModel):

    PROPERTIES = [
        'page_id',
        'batch_job_id',
        'pp_noisemsr',
        'pp_ecorr',
        'pp_juxta',
        'pp_retas',
        'pp_health',
        'pp_pg_quality',
        'noisiness_idx',
        'multicol',
        'skew_idx',
    ]

    def __init__(self, settings):
        super(self.__class__, self).__init__(settings)
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
        data_keys = set(keys) - set(["page_id", "batch_job_id"])
        if len(data_keys) >= 1:
            return True
        else:
            return False
