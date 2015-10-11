#!/usr/bin/env python

from api import SynAPI
from time import sleep

if __name__ == '__main__':
    api = SynAPI()

    # Auto storing
    limit = 3000000
    for i in range(300000):
        stats = api.get_owner_stats()
        print(i, stats)
        if stats['credits'] > limit:
            print('stored...')
            api.store_resources('credits', stats['credits']-limit)
        sleep(3)

    api.session.save_session()