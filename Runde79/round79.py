#!/usr/bin/env python
from __future__ import division

from datetime import datetime as dt

import numpy as np

from intelligence import BaseBot, BonusBotMixin, EnergyFPBotMixin, StatsBotMixin, StockBot

# TODO: overall_limit with tenders! -> adjust cr_limit dynamically
# TODO: adjust tenders if too much erz...
# TODO next: buy fp
# TODO: if prodder & stored ... make sleep time higher? -> end of tick or smth?
# TODO: rebuy protection after 20hours or smth -> new db table, "reached 10%"?


class NEBBot(BaseBot, BonusBotMixin, EnergyFPBotMixin, StatsBotMixin, StockBot):
    def __init__(self):
        super(NEBBot, self).__init__()
        self.last_hour = self.last_stats()

        # bot base settings
        self.active = False
        self.sleep_time = (90, 10)
        self.api.session.refresh_mean = 0

        # resources settings
        # store everything + store everything up to limit..
        self.cr_limit = 4900000
        self.energy_limit = 1000000
        self.erz_limit = 0
        self.fp_limit = 30000
        self.overall_limit = 5000000

        # relevant fos values
        self.tax = 0.15  # needed for spend_cr -> on units?!

        # # # all regular jobs
        self.jobs.append(self.set_night_mode)
        # # #  print owner stats before all actions
        self.jobs.append(self.print_owner_stats)
        # # # spend cr
        self.jobs.append(self.build_buildings)
        # self.jobs.append(self.build_ha)
        self.jobs.append(self.buy_energy_with_cr)
        # TODO: exactly here we need a priority queue
        # -> shifting protection before and after build ha
        # -> how to rate this? Ranking system?!
        # self.jobs.append(self.keep_protection)
        # self.jobs.append(self.store_energy_with_cr)
        # self.jobs.append(self.store_fp_with_cr)
        self.jobs.append(self.store_cr)
        # # # handle prod
        self.jobs.append(self.sell_erz)
        # self.jobs.append(self.store_erz)
        # self.jobs.append(self.sell_energy)
        # self.jobs.append(self.store_energy)
        # # # cover energy & fp consumption, if not done by spend cr
        self.jobs.append(self.cover_energy_consumption)
        # # # print owner stats after all actions
        self.jobs.append(self.print_owner_stats)

        # # # all hourly jobs
        self.hourly_jobs.append(self.take_ha_bonus)
        self.hourly_jobs.append(self.cover_energy_consumption)
        self.hourly_jobs.append(self.update_energy_consumption)
        self.hourly_jobs.append(self.take_log)

        # EnergyFPBot
        self.energy_consumption = None
        self.energy_minimum = None
        self.energy_consumption_multiplier = 2

        # StockBot
        self.protect_percent = 0.1
        self.protection_syns = [11]

        # TODO: add oop for this..
        # BuildingsBot
        # last item should handle "leftover" buildings
        # (due to int rounding of percentage*amount)
        # min_buildings is used
        self.buildings_types = [('bh', 0.150), ('wz', 0.18), ('efas', 0.25), ('hz', 0.42)]
        self.min_buildings = int(1 / min(self.buildings_types, key=lambda x: x[1])[1]) + 1

    def store_energy_with_cr(self):
        """ For this round... never enough energy in storage """
        # TODO: 10% here, too
        stats = self.api.get_owner_stats()
        cr = stats['credits'] - self.cr_limit
        if cr > 0:
            store = self.api.get_store_resources()
            if store['energy'] < 100000000:
                gm = self.api.get_gm_resources()
                if store['ex_energy'] > gm['ex_energy']:
                    amount = min(int(cr / gm['ex_energy']), gm['energy'])
                    if amount > 0:
                        self.db.action_output(
                            'Buy {0}energy for {1} and store it'.format(amount, gm['ex_energy']),
                            dt.now()
                        )
                        self.api.buy('energy', amount, gm['ex_energy'])
                        self.api.store_resources('energy', amount)

    def store_fp_with_cr(self):
        """ For this round... never enough fp in storage """
        stats = self.api.get_owner_stats()
        cr = stats['credits'] - self.cr_limit
        if cr > 0:
            store = self.api.get_store_resources()
            gm = self.api.get_gm_resources()
            if store['ex_fp'] > gm['ex_fp']:
                amount = min(int(cr / gm['ex_fp']), gm['fp'])
                if amount > 0:
                    self.db.action_output(
                        'Buy {0}fp for {1} and store it'.format(amount, gm['ex_fp']),
                        dt.now()
                    )
                    self.api.buy('fp', amount, gm['ex_fp'])
                    self.api.store_resources('fp', amount)

    def sell_erz(self):
        stats = self.api.get_owner_stats()
        amount = stats['erz'] - self.erz_limit
        # TODO: check how many tenders are placed - maybe adjust some
        if amount > 0:
            store = self.api.get_store_resources()
            # TODO: USE median... higher refreshtimes then - 60s should be fine
            # median-1, weighting by appearances, not by amount
            price = int(store['ex_erz']*10+2)
            self.db.action_output('Sell {0}erz for {1}'.format(amount, price), dt.now())
            self.api.place_tender('erz', price, amount)

    def sell_energy(self):
        stats = self.api.get_owner_stats()
        amount = stats['energy'] - self.energy_limit
        # TODO: check how many tenders are placed - maybe adjust some
        if amount > 0:
            store = self.api.get_store_resources()
            # TODO: USE median... higher refreshtimes then - 60s should be fine
            # median-1, weighting by appearances, not by amount
            price = int(store['ex_energy']*10)
            self.db.action_output('Sell {0}energy for {1}'.format(amount, price), dt.now())
            self.api.place_tender('energy', price, amount)

    def build_buildings(self):
        buildings = self.api.get_buildings()
        if buildings[1] > self.min_buildings:
            cr = self.api.get_owner_stats()['credits']
            amount = min(cr//buildings[0], buildings[1])
            if amount > self.min_buildings:
                summe = 0
                for i, (building, percentage) in enumerate(self.buildings_types):
                    if i < len(self.buildings_types)-1:
                        x = int(amount*percentage)
                    else:
                        x = amount-summe
                    if x > 0:
                        summe += x
                        self.db.action_output('Build {0}{1}'.format(x, building), dt.now())
                        self.api.build_buildings(building, x)

    def build_ha(self):
        cr = self.api.get_owner_stats()['credits']
        if cr > 0:
            area = self.api.get_area_cost()
            cost = area[0]
            in_construction = area[1]
            amount = min(cr // cost, 1000-in_construction)
            if amount > 0:
                self.db.action_output('Build {0}ha'.format(amount), dt.now())
                self.api.build_area(amount)

if __name__ == '__main__':
    bot = NEBBot()
    bot.run()
