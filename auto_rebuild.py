#!/usr/bin/env python

from api import SynAPI
from time import sleep

import numpy as np

from intelligence.dev import seller_optimizer

if __name__ == '__main__':
    api = SynAPI()

    # Auto storing
    limit = 1000000
    for i in range(300000):
        stats = api.get_owner_stats()
        print(i, stats)
        if stats['credits'] > limit:

            storage_resources = api.get_store_resources()
            gm_resources = api.get_gm_resources()

            # where to pick which resource -> [energy, erz, fp]
            # from gm or from store?
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

                print(resource_source)
                print(amount, ressis)

                for j in range(1, 4):
                    res = res_names[j-1]
                    source = resource_source[j-1]
                    price = ex_rates[j-1]*10

                    quantity = ressis[j]

                    if quantity > 0:
                        if source == 'gm':
                            api.buy(res, quantity, price)
                        elif source == 'store':
                            api.pull_store_resources(res, quantity)

                api.build_military('huc', amount)
            else:
                api.store_resources('credits', stats['credits']-limit)

        sleep(3)

    api.session.save_session()