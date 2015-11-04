#!/usr/bin/env python

from api import SynAPI
from time import sleep

from intelligence.optimize import area_optimizer

if __name__ == '__main__':
    api = SynAPI()

    # Auto storing
    limit = 1000000
    for i in range(300000):
        stats = api.get_owner_stats()
        print(i, stats)
        if stats['credits'] > limit:
            ha = area_optimizer(stats['credits'], api.get_area_cost())
            print('Build {0}ha'.format(ha))
            api.build_area(ha)
        sleep(3)

    api.session.save_session()
