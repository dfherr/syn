#!/usr/bin/env python
from datetime import datetime as dt

from intelligence import BaseBot, BonusBot, EnergyFPBot, StatsBot


class NEBBot(BaseBot, BonusBot, StatsBot, EnergyFPBot):
    def __init__(self):
        super(NEBBot, self).__init__()
        self.last_hour = self.last_stats()

        # bot base settings
        self.active = True
        self.sleep_time = (60, 20)
        self.api.session.refresh_mean = 2

        # resources settings
        # store everything + store everything up to limit..
        self.cr_limit = 5000000
        self.energy_limit = 1000000
        self.erz_limit = 1000000
        self.fp_limit = 30000
        self.overall_limit = 5000000

        # relevant fos values
        self.tax = 0.15  # needed for spend_cr -> on units?!

        # all hourly jobs
        self.hourly_jobs.append(self.take_ha_bonus)
        self.hourly_jobs.append(self.update_energy_consumption)
        self.hourly_jobs.append(self.take_log)

        # all regular jobs
        # print owner stats before and after all actions
        self.jobs.append(self.print_owner_stats)
        self.jobs.append(self.spend_cr)
        self.jobs.append(self.sell_erz)
        self.jobs.append(self.handle_open_prod)
        self.jobs.append(self.cover_energy_consumption)
        self.jobs.append(self.print_owner_stats)

        # EnergyFPBot
        self.energy_consumption = None
        self.energy_minimum = None
        self.energy_consumption_multiplier = 2

        # self.spend_cr_queue = [energy, build_gebs, build_ha, buy_units, store]
        self.spend_cr_queue = [self.store_cr]

        # replace these lists with a job class + queue?
        # job (last refresh, refresh interval, priority, function)
        # -> [+2, +1, -1, -2, ...] -> '+' means it _has to be done_
        # sort jobs after priority

    def sell_erz(self):
        # TODO: night mode..?
        stats = self.api.get_owner_stats()
        amount = stats['erz'] - 50000
        if amount > 0:
            store = self.api.get_store_resources()
            price = int(store['ex_erz']*10 + 3)  # TODO: better system needed here, median could work
            self.db.action_output('Sell {0}erz for {1}'.format(amount, price), dt.now())
            self.api.place_tender('erz', price, amount)

    def handle_open_prod(self):
        stats = self.api.get_owner_stats()
        if self.night_mode:
            amount = stats['erz']
        else:
            amount = stats['erz'] - self.erz_limit
        if amount > 0:
            self.db.action_output('Store {0}erz'.format(amount), dt.now())
            self.api.store_resources('erz', amount)

    def build_gebs(self):
        raise NotImplementedError

    def build_ha(self):
        raise NotImplementedError

    def store_cr(self):
        stats = self.api.get_owner_stats()
        if self.night_mode:
            amount = stats['credits']
        else:
            amount = stats['credits'] - self.cr_limit
        if amount > 0:
            self.db.action_output('Store {0}cr'.format(amount), dt.now())
            self.api.store_resources('credits', amount)

    def spend_cr(self):
        """ Gebs, HUC(OC?), Spies, Ha, Store """
        for f in self.spend_cr_queue:
            f()

if __name__ == '__main__':
    bot = NEBBot()
    bot.run()
