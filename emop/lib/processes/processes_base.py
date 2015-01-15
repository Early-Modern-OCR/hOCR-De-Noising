import collections


class ProcessesBase(object):

    def __init__(self, job):
        self.job = job
        self.results = collections.namedtuple('Results', ['stdout', 'stderr', 'exitcode'])

    def run(self):
        raise NotImplementedError
