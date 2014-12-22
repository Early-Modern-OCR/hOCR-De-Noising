class ProcessesBase(object):

    def __init__(self, job):
        self.job = job

    def run(self):
        raise NotImplementedError
