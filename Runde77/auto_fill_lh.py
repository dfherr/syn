#!/usr/bin/env python
from __future__ import division

from time import sleep

import numpy as np

from api import SynAPI


if __name__ == '__main__':
    api = SynAPI()

    for i in range(10):
        stats = api.get_owner_stats()

        # cost of units
        cost_huc = np.asarray([0, 700, 240, 96])
        cost_spy = np.asarray([160, 120, 0, 8])
        cost_buc = np.asarray([880, 200, 120, 0])

        # sum of costs
        cr = sum([
            stats['capas_military']*cost_huc[0],
            stats['capas_carrier']*cost_buc[0],
            stats['capas_spies']*cost_spy[0],
            -stats['credits']
        ])
        ene = sum([
            stats['capas_military']*cost_huc[1],
            stats['capas_carrier']*cost_buc[1],
            stats['capas_spies']*cost_spy[1],
            -stats['energy']
        ])
        erz = sum([
            stats['capas_military']*cost_huc[2],
            stats['capas_carrier']*cost_buc[2],
            stats['capas_spies']*cost_spy[2],
            -stats['erz']
        ])
        fp = sum([
            stats['capas_military']*cost_huc[3],
            stats['capas_carrier']*cost_buc[3],
            stats['capas_spies']*cost_spy[3],
            -stats['fp']
        ])

        # pull resources from store
        print(cr, ene, erz, fp)

        raw_input('')

        api.pull_store_resources('credits', cr)
        api.pull_store_resources('energy', ene)
        api.pull_store_resources('erz', erz)
        api.pull_store_resources('fp', fp)

        # build units
        print('huc: {0}'.format(stats['capas_military']))
        api.build_military('huc', stats['capas_military'])
        print('buc: {0}'.format(stats['capas_carrier']))
        api.build_military('buc', stats['capas_carrier'])

        print('spies: {0}'.format(stats['capas_spies']))
        thieves = (2*stats['capas_spies'])//3
        guards = stats['capas_spies']-thieves
        api.build_military('thief', thieves)
        api.build_military('guardian', guards)

        # Wait one hour
        print('sleeping...')
        sleep(60*60)

    api.session.save_session()
