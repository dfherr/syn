#!/usr/bin/env python
from __future__ import division

from datetime import datetime as dt
from time import sleep

import numpy as np

from api import SynAPI
from api.utils import select_capas, res_names
from database import Database
from intelligence import (
    area_optimizer,
    calculate_taxed_cr,
    free_capas,
    seller_optimizer,
    split_units_per_ratio,
    prepare_resources
)

# SPYLOGS -> times scanned..
# FIND LAST LOG....
# NO RESOURCE TENDERS!
# PULL RESOURCES FIRST!
# pay right amount of taxes...
# TENDERS ONLINE?

# add __alls__ everywhere?
# TESTs!


class SellerStatsBot(object):
    def __init__(self):
        self.selling = False
        self.sleep_time = 5
        self.cr_limit = 2500000
        self.ene_limit = 5000000
        self.spend_on = 'store'
        self.tax = 0.05
        self.ranger_rines_ratio = [0, 1]
        self.spy_ratio = [1, 1, 2]
        self.build_order = ['ranger', 'spies', 'buc']
        self.unit_prices = {
            'ranger': np.asarray([188, 60, 50, 0]),
            'buc': np.asarray([880, 200, 120, 0]),
            'spies': np.asarray([160, 120, 0, 8])
        }

        self.api = SynAPI()
        self.db = Database()

    def run(self):
        last_log = self.db.get_last_log()
        log_minute = 2
        last_stats = None
        active_building = False

        # convert ratios into percentage ratios
        self.ranger_rines_ratio = np.asarray(list(map(
            lambda x: round(x/sum(self.ranger_rines_ratio), 2),
            self.ranger_rines_ratio
        )))
        self.spy_ratio = np.asarray(list(map(
            lambda x: round(x/sum(self.spy_ratio), 2),
            self.spy_ratio
        )))

        # rebuild units after selling, put left over credits in 'store' or 'ha'
        # update database rankings, storage prices and shares
        while True:
            # # # SELLING
            if self.selling:
                stats = self.api.get_owner_stats()
                if stats != last_stats:
                    self.db.action_output(str(stats), dt.now())
                    last_stats = stats

                # TODO: how to handle "no resources left"?!
                if stats['credits'] > self.cr_limit and free_capas(stats):
                    active_building = True
                    self.build_units(stats)
                # if no units to build, use credits for new ha / store them
                elif stats['credits'] > self.cr_limit:
                    if self.spend_on == 'store':
                        amount = stats['credits']-self.cr_limit
                        action = 'Store {0}cr'.format(amount)
                        self.api.store_resources('credits', amount)
                    elif self.spend_on == 'ha':
                        ha = area_optimizer(stats['credits'], self.api.get_area_cost())
                        action = 'Build {0}ha'.format(ha)
                        self.api.build_area(ha)

                    self.db.action_output(action, dt.now())
                else:
                    active_building = False

            # # # hourly jobs
            # if new tick since last log
            # give the server time for the next tick... then start logging etc
            if last_log != dt.now().hour and dt.now().minute > log_minute and not active_building:
                last_log = dt.now().hour

                if not self.selling:
                    self.db.action_output('login', dt.now())

                self.take_log()

                stats = self.api.get_owner_stats()
                if stats['energy'] > self.ene_limit:
                    amount = stats['energy']-self.ene_limit
                    self.db.action_output('Store {0}energy'.format(amount))
                    self.api.store_resources('energy', amount)

                if not self.selling:
                    self.db.action_output('logout', dt.now())
                    self.api.logout()

            if not active_building:
                sleep(self.sleep_time)

    def take_log(self):
        date = dt.now()

        self.db.action_output('start stats recording', date)

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

    def build_units(self, stats):
        owner_resources, volumes, ex_rates, resource_source = prepare_resources(
            self.api.get_gm_resources(),
            self.api.get_store_resources(),
            stats,
            self.tax
        )

        unit_price = None
        unit = None
        capas = None
        for x in self.build_order:
            tmp = select_capas(x)
            if stats[tmp] > 0:
                capas = tmp
                unit = x
                unit_price = self.unit_prices[unit]
                break

        if unit is not None:
            amount, ressis = seller_optimizer(
                owner_resources,
                unit_price,
                ex_rates,
                stats[capas],
                volumes,
                resource_source
            )

            # get resources to rebuild units
            for i in range(1, 4):
                res = res_names[i-1]
                source = resource_source[i-1]
                price = round(ex_rates[i], 2)

                quantity = ressis[i]
                if quantity > 0:
                    self.db.action_output(
                        'Buy {0}{1} for {2} from {3}'.format(quantity, res, int(price*10), source),
                        dt.now()
                    )
                    if source == 'gm':
                        self.api.buy(res, quantity, int(price*10))
                    elif source == 'store':
                        # TO BE TESTED
                        self.api.store_resources('credits', calculate_taxed_cr(self.tax, quantity, price))
                        self.api.pull_store_resources(res, quantity)

            # rebuild units
            if unit == 'ranger':
                tmp = split_units_per_ratio(amount, self.ranger_rines_ratio)
                action = self.api.bulk_build_military(tmp, ['ranger', 'marine'])
            elif unit == 'spies':
                tmp = split_units_per_ratio(amount, self.spy_ratio)
                print(tmp)
                action = self.api.bulk_build_military(tmp, ['thief', 'guardian', 'agent'])
            else:
                action = 'Build {0} {1}s'.format(amount, unit)
                self.api.build_military(unit, amount)
            self.db.action_output(action, dt.now())

if __name__ == '__main__':
    bot = SellerStatsBot()
    bot.run()
