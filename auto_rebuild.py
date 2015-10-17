#!/usr/bin/env python

from api import SynAPI
from time import sleep

import numpy as np

from intelligence.optimize import seller_optimizer, area_optimizer

# TODO: if lager, don't take cr away at optimizing...?

# Where to put left over credits
put_money = 'ha'


if __name__ == '__main__':
    api = SynAPI()

    # Auto storing
    limit = 1000000
    for i in range(300000):
        stats = api.get_owner_stats()
        print(i, stats)

        if stats['credits'] > 20000 and stats['capas_military'] > 0:

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

            if stats['capas_military'] > 0:
                ex_rates = np.asarray([1] + ex_rates)
                volumes = np.asarray([0] + volumes)
                owner_resources = np.asarray([
                    stats['credits'],
                    stats['energy'],
                    stats['erz'],
                    stats['fp']
                ])
                unit_price = np.asarray([0, 700, 240, 96])
                amount, ressis = seller_optimizer(
                    owner_resources,
                    unit_price,
                    ex_rates,
                    stats['capas_military'],
                    volumes
                )

                for j in range(1, 4):
                    res = res_names[j-1]
                    source = resource_source[j-1]
                    price = ex_rates[j]*10

                    quantity = ressis[j]
                    print('Buy {0}{1} for {2} at {3}'.format(quantity, res, price, source))
                    if quantity > 0:
                        if source == 'gm':
                            api.buy(res, quantity, price)
                        elif source == 'store':
                            api.pull_store_resources(res, quantity)

                api.build_military('huc', amount)
            else:
                if put_money == 'store':
                    api.store_resources('credits', stats['credits']-limit)
                elif put_money == 'ha':
                    api.build_area(
                        area_optimizer(
                            stats['credits']-limit,
                            api.get_area_cost())
                    )
        else:
            sleep(3)

    api.session.save_session()