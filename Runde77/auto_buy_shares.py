#!/usr/bin/env python
from __future__ import division

from api import SynAPI
from time import sleep

if __name__ == '__main__':
    api = SynAPI()

    limit = 10000000
    for i in range(300000):
        stats = api.get_owner_stats()
        print(i, stats)
        if stats['credits'] > limit:
            amount = stats['credits'] // 4000
            api.buy_shares(5, amount)
        sleep(3)

    api.session.save_session()
