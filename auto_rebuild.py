#!/usr/bin/env python
from __future__ import division

from api import SynAPI
from time import sleep
from datetime import datetime

import numpy as np

from intelligence.optimize import seller_optimizer, area_optimizer

# Where to put left over credits
put_money = 'ha'
limit = 1000000


if __name__ == '__main__':
    api = SynAPI()

    last_stats = None
    for i in xrange(9000000):
        stats = api.get_owner_stats()
        if stats != last_stats:
            print(datetime.strftime(datetime.now(), "%H:%M"), stats)
        last_stats = stats

        if stats['credits'] > limit and (stats['capas_military'] > 0 or stats['capas_carrier'] > 0 or stats['capas_spies'] > 0):
            storage_resources = api.get_store_resources()
            gm_resources = api.get_gm_resources()

            # where to pick which resource -> [energy, erz, fp]
            # from gm or from store?
            # TODO -> optimize
            res_names = ['energy', 'erz', 'fp']
            ex_rate_names = ['ex_energy', 'ex_erz', 'ex_fp']
            resource_source = [
                'gm' if
                gm_resources[i] <= storage_resources[i] / 0.95
                else 'store' for i in ex_rate_names
            ]
            ex_rates = [0, 0, 0]
            volumes = [0, 0, 0]

            for j, x in enumerate(ex_rate_names):
                if resource_source[j] == 'gm':
                    ex_rates[j] = gm_resources[x]
                    volumes[j] = gm_resources[res_names[j]]
                else:
                    ex_rates[j] = storage_resources[x]
                    volumes[j] = storage_resources[res_names[j]]

            ex_rates = np.asarray([1] + ex_rates)
            volumes = np.asarray([0] + volumes)
            owner_resources = np.asarray([
                stats['credits'],
                stats['energy'],
                stats['erz'],
                stats['fp']
            ])

            # Hack to build the order ... is there a better way?
            if stats['capas_spies'] > 0:
                capas = 'capas_spies'
                unit = 'spy'
                unit_price = np.asarray([160, 120, 0, 8])
            if stats['capas_carrier'] > 0:
                capas = 'capas_carrier'
                unit = 'buc'
                unit_price = np.asarray([880, 200, 120, 0])
            if stats['capas_military'] > 0:
                capas = 'capas_military'
                unit = 'huc'
                unit_price = np.asarray([0, 700, 240, 96])

            amount, ressis = seller_optimizer(
                owner_resources,
                unit_price,
                ex_rates,
                stats[capas],
                volumes,
                resource_source
            )
            for j in range(1, 4):
                res = res_names[j-1]
                source = resource_source[j-1]
                price = ex_rates[j]

                quantity = ressis[j]
                if quantity > 0:
                    print('Buy {0}{1} for {2} from {3}'.format(quantity, res, price*10, source))
                    if source == 'gm':
                        api.buy(res, quantity, price)
                    elif source == 'store':
                        # TODO: pull from syn first, calculate new quantities
                        api.pull_store_resources(res, quantity)
            print('Build {0} {1}s'.format(amount, unit))
            if unit == 'spy':
                a1 = (2*amount)//3
                a2 = amount - a1
                api.build_military('thief', amount)
                # api.build_military('guardian', a2)
            else:
                api.build_military(unit, amount)

        else:
            if stats['credits'] > limit:
                if put_money == 'store':
                    store_cr = stats['credits']-limit
                    print('Store {0}cr'.format(store_cr))
                    api.store_resources('credits', store_cr)
                elif put_money == 'ha':
                    ha = area_optimizer(stats['credits'], api.get_area_cost())
                    print('Build {0}ha'.format(ha))
                    api.build_area(ha)
            sleep(3)

    api.session.save_session()
