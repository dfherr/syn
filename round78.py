#!/usr/bin/env python
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
    prepare_resources
)

# variables to set
selling = True
sleep_time = 5
cr_limit = 2000
spend_on = 'ha'
tax = 0.15
thief_ranger_ratio = 4/5.
build_order = ['ranger', 'spies', 'buc']
unit_prices = {
    'ranger': np.asarray([235, 75, 62, 0]),
    'buc': np.asarray([1100, 250, 150, 0]),
    'spies': np.asarray([220, 165, 0, 11])
}


if __name__ == '__main__':
    api = SynAPI()
    db = Database()

    last_log = -1
    log_minute = 2
    last_stats = None
    active_building = False

    # rebuild units after selling, put left over credits in 'store' or 'ha'
    # update database rankings, storage prices and shares
    while True:
        # # # SELLING
        # TODO:
        # if online tenders -> set sleep time lower and start rebuilding
        # if tenders online, set log_minute to smth. like 30 instead of 2
        if selling:
            stats = api.get_owner_stats()
            if stats != last_stats:
                db.action_output(str(stats), dt.now())
                last_stats = stats

            # TODO: how to handle "no resources left"?!
            if stats['credits'] > cr_limit and free_capas(stats):
                active_building = True

                owner_resources, volumes, ex_rates, resource_source = prepare_resources(
                    api.get_gm_resources(),
                    api.get_store_resources(),
                    stats,
                    tax
                )

                unit_price = None
                unit = None
                capas = None
                for x in build_order:
                    tmp = select_capas(x)
                    if stats[tmp] > 0:
                        capas = tmp
                        unit = x
                        unit_price = unit_prices[unit]
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
                            db.action_output(
                                'Buy {0}{1} for {2} from {3}'.format(quantity, res, int(price*10), source),
                                dt.now()
                            )
                            if source == 'gm':
                                api.buy(res, quantity, int(price*10))
                            elif source == 'store':
                                # TO BE TESTED
                                api.store_resources('credits', calculate_taxed_cr(tax, quantity, price))
                                api.pull_store_resources(res, quantity)

                    # rebuild units
                    db.action_output('Build {0} {1}s'.format(amount, unit), dt.now())
                    if unit == 'spies':
                        a1 = int(thief_ranger_ratio*amount)
                        a2 = amount - a1
                        api.build_military('thief', a1)
                        api.build_military('guardian', a2)
                    else:
                        api.build_military(unit, amount)

            elif stats['credits'] > cr_limit:
                if spend_on == 'store':
                    store_cr = stats['credits']-cr_limit
                    action = 'Store {0}cr'.format(store_cr)
                    api.store_resources('credits', store_cr)
                elif spend_on == 'ha':
                    ha = area_optimizer(stats['credits'], api.get_area_cost())
                    action = 'Build {0}ha'.format(ha)
                    api.build_area(ha)

                db.action_output(action, dt.now())
            else:
                active_building = False

        # # # LOGGING
        # If new tick since last log
        # give the server time for the next tick... then start logging
        if last_log != dt.now().hour and dt.now().minute > log_minute and not active_building:
            last_log = dt.now().hour
            date = dt.now()

            db.action_output('login and start stats recording', date)

            db.action_output('rankings...', date)
            rankings = api.generate_rankings()
            db.save_rankings(rankings, date)

            date = dt.now()
            db.action_output('storage...', date)
            store = api.get_store_resources()
            db.save_storage(store, date)

            date = dt.now()
            db.action_output('shares...', date)
            shares = api.get_shares()
            db.save_shares(shares, date)

            if not selling:
                api.logout()

            db.action_output('end stats recording and logout', dt.now())

        if not active_building:
            sleep(sleep_time)
