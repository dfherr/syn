#!/usr/bin/env python
from time import sleep

from api import SynAPI


if __name__ == '__main__':
    api = SynAPI()

    for i in range(10):

        api.take_bonus(2)
        api.pull_store_resources('credits', 1000000)
        api.build_buildings('lh', 8)

        sleep(60*60)