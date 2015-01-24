import collections


class ProcessesBase(object):

    def __init__(self, job):
        self.job = job
        self.results = collections.namedtuple('Results', ['stdout', 'stderr', 'exitcode'])

    def should_run(self):
        return True

    def run(self):
        raise NotImplementedError
