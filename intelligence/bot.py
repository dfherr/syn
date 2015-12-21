from __future__ import division

from datetime import datetime as dt
from time import sleep

import numpy as np

from api import SynAPI
from database import Database


class BaseBot(object):
    def __init__(self):
        self.api = SynAPI()
        self.db = Database()

        self.active = True
        self.sleep_time = 30

        self.jobs = []

        self.last_hour = -1
        self.hourly_job_minute = 2
        self.hourly_jobs = []

    def human_sleep_time(self):
        return np.random.poisson(self.sleep_time)

    def run(self):
        while True:
            if self.active:
                for job in self.jobs:
                    job()

            # # # hourly jobs
            if self.last_hour != dt.now().hour and dt.now().minute > self.hourly_job_minute:
                self.last_hour = dt.now().hour

                if not self.active:
                    self.db.action_output('login', dt.now())

                for job in self.hourly_jobs:
                    job()

                if not self.active:
                    self.db.action_output('logout', dt.now())
                    self.api.logout()

            sleep(self.human_sleep_time())


class StatsBot(object):
    def take_log(self):
        date = dt.now()

        self.db.action_output('start stats recording', date)

        self.db.action_output('military stats...', date)
        mili_stats = self.api.get_owner_stats()
        self.db.save_military_stats(mili_stats, date)

        self.db.action_output('rankings...', date)
        rankings = self.api.generate_rankings()
        self.db.save_rankings(rankings, date)

        date = dt.now()
        self.db.action_output('storage...', date)
        store = self.api.get_store_resources()
        self.db.save_storage(store, date)

        date = dt.now()
        self.db.action_output('shares...', date)
        shares = self.api.get_shares()
        self.db.save_shares(shares, date)

        date = dt.now()
        self.db.action_output('spies...', date)
        spies = self.api.get_suffered_spies()
        self.db.save_spies(spies, date)

        self.db.action_output('end stats recording', dt.now())

    def last_stats(self):
        last_log = self.db.get_last_log()
        if (dt.now()-last_log).total_seconds() > 3600:
            return -1
        return last_log.hour
