from __future__ import division

from time import sleep

import numpy as np

from api import SynAPI
from .optimize import seller_optimizer as new_optimizer


class MAFIABot(object):
    def __init__(self):
        """
        - spends every cr over
        """
        self.api = SynAPI()

        self.base_stats = None
        self.storage_resources = None
        self.gm_resources = None

        self.max_cash = 0  # 1000000

        # should be filled by scraper later..
        self.spy_price = np.asarray([160, 120, 0, 8])

    def handle_cash(self):
        self.storage_resources = self.api.get_store_resources()
        self.gm_resources = self.api.get_gm_resources()

        # where to pick which resource -> [energy, erz, fp]
        # from gm or from store?
        res_names = ['energy', 'erz', 'fp']
        ex_rate_names = ['ex_energy', 'ex_erz', 'ex_fp']
        resource_source = [
            'gm' if
            self.gm_resources[i] <= self.storage_resources[i] / 0.95
            else 'store' for i in ex_rate_names
        ]
        ex_rates = [0, 0, 0]
        volumes = [0, 0, 0]

        for i, x in enumerate(ex_rate_names):
            if resource_source[i] == 'gm':
                ex_rates[i] = self.gm_resources[x]
                volumes[i] = self.gm_resources[res_names[i]]
            else:
                ex_rates[i] = self.storage_resources[x]
                volumes[i] = self.storage_resources[res_names[i]]

        print(self.storage_resources)
        print(self.gm_resources)
        print(resource_source)
        print(ex_rates)
        print(volumes)

        if self.base_stats['capas_spies'] > 0:
            # format for seller_optimizer (requires credits, too)
            ex_rates = np.asarray([1] + ex_rates)
            volumes = np.asarray([0] + volumes)
            owner_resources = np.asarray([
                self.base_stats['credits'],
                self.base_stats['energy'],
                self.base_stats['erz'],
                self.base_stats['fp']
            ])

            x = new_optimizer(
                owner_resources,
                self.spy_price,
                ex_rates,
                self.base_stats['capas_spies'],
                volumes
            )

        print(x)

    def run(self):
        """
        starts the bot and contains the basic intel algorithm
        """
        while True:
            self.base_stats = self.api.get_owner_stats()
            print(self.base_stats)

            if self.base_stats['credits'] > self.max_cash:
                self.handle_cash()

            sleep(3)