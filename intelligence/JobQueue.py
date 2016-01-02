from datetime import datetime as dt

__all__ = ['Job', 'JobQueue']


class Job(object):
    def __init__(self, refresh_interval, last_refresh, funct):
        pass

    def __cmp__(self, other):
        return True


class JobQueue(object):
    def __init__(self, jobs):
        self.job = 0

    def append(self, job):
        pass

    def next(self):
        pass