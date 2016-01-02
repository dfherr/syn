from __future__ import division

from datetime import datetime as dt
from time import sleep

import numpy as np

from api import SynAPI
from database import Database

__all__ = ['BaseBot', 'BonusBot', 'EnergyFPBot', 'StatsBot']


class BaseBot(object):
    def __init__(self):
        self.api = SynAPI()
        self.db = Database()

        # mean, sigma of normal distribution
        # of sleeping time in seconds
        self.sleep_time = (30, 1)

        # night_mode -> to handle tasks before bot goes into sleep mode
        self.night_mode = False
        self.night_sleep_time = 3 * 3600

        # check if owner stats changed
        self.last_owner_stats = None

        # active determines if jobs are carried out
        self.active = True
        self.jobs = []

        self.last_hour = -1
        self.hourly_job_minute = 1
        self.hourly_jobs = []

    def print_owner_stats(self):
        owner_stats = self.api.get_owner_stats()
        if self.last_owner_stats != owner_stats:
            self.last_owner_stats = owner_stats
            self.db.action_output(str(self.last_owner_stats), dt.now())

    def human_sleep_time(self):
        if 2 <= dt.now().hour < 3:
            # TODO: change nightmode in extern function..
            if self.night_mode:
                return self.night_sleep_time
            self.night_mode = True
            self.db.action_output('Enter night mode', dt.now())
        else:
            if self.night_mode:
                self.db.action_output('Exit night mode', dt.now())
                self.night_mode = False
        return abs(int(np.random.normal(self.sleep_time[0], self.sleep_time[1])))

    def run(self):
        while True:
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

            # # # regular jobs
            if self.active:
                for job in self.jobs:
                    job()

            sleep_time = self.human_sleep_time()
            if self.night_mode:
                self.db.action_output('Sleeping for {0}s'.format(sleep_time), dt.now())
            sleep(sleep_time)


class StatsBot(object):
    # TODO: stolen ressis...
    def take_log(self):
        self.db.action_output('start stats recording', dt.now())

        date = dt.now()
        self.db.action_output('military stats...', date)
        mili_stats = self.api.get_owner_stats()
        self.db.save_military_stats(mili_stats, date)

        date = dt.now()
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


class BonusBot(object):
    def take_ha_bonus(self):
        status_stats = self.api.get_status_stats()
        if status_stats['ha_bonus']:
            self.db.action_output('Taking ha bonus', dt.now())
            self.api.take_bonus(2)


class ResourceBot(object):
    def __init__(self):
        # resource limits
        self.cr_limit = None
        self.energy_limit = None
        self.erz_limit = None
        self.fp_limit = None
        self.overall_limit = None

        # storage taxes
        self.tax = None

    def pull_to_target_value(self, unit, target_value, current_value):
        """
        pulls energy / erz / fp up to a target value
        first from syn members, then from the store
        """
        # TODO: not enough available!? Not enough lgh?!
        self.api.pull_syn_resources(unit, target_value-current_value)
        current_value = self.api.get_owner_stats()[unit]
        if current_value < target_value:
            self.api.pull_store_resources(unit, target_value-current_value)


class EnergyFPBot(ResourceBot):
    def __init__(self):
        super(EnergyFPBot, self).__init__()
        self.energy_consumption = None
        self.energy_minimum = None
        self.energy_consumption_multiplier = 2

    def update_energy_consumption(self):
        status_stats = self.api.get_status_stats()
        self.energy_consumption = status_stats['energy_consumption']

        # if we prod energy, we don't have to care about the energy consumption
        # else the actual _consumption_ is positive!
        if self.energy_consumption > 0:
            self.energy_consumption = 0
        else:
            self.energy_consumption *= -1

        if self.night_mode:
            self.energy_minimum = self.energy_consumption * (self.night_sleep_time // 3600 + 2)
        else:
            self.energy_minimum = self.energy_consumption * self.energy_consumption_multiplier

        if self.energy_limit is not None:
            if self.energy_minimum > self.energy_limit:
                self.energy_limit = self.energy_minimum
        else:
            self.energy_limit = self.energy_minimum
        self.db.action_output(
            'Set Energy limits: min: {0} | max: {1}'.format(
                self.energy_minimum,
                self.energy_limit
            ),
            dt.now()
        )

    def cover_energy_consumption(self):
        """ energy for next tick """
        # backtrack to energy consumption if we enter night mode
        if self.night_mode or self.energy_consumption is None:
            self.update_energy_consumption()

        energy = self.api.get_owner_stats()['energy']
        if energy < self.energy_minimum:
            self.db.action_output(
                'Pull {0}energy from syn/storage'.format(self.energy_minimum-energy),
                dt.now()
            )
            self.pull_to_target_value('energy', self.energy_minimum, energy)

    # def cover_fp_consumption(self):
    #     """ fp for next tick """
    #     # TODO: FP...
    #     raise NotImplementedError
