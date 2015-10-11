#!/usr/bin/env python

from api import SynAPI
from database import Database
from time import sleep

if __name__ == '__main__':
    # from intelligence.bot import Bot
    #
    # bot = Bot()
    # bot.run()

    api = SynAPI()

    # call random page until tender is online, sleep(2 +/- std dev)
    # check tender every 10 requests (at auto storing, too) (save in stats collection?)

    # set new tender if other one is lower -> 2k

    # do until 5 tenders, then delete highest tender
    # repeat until 55%...

    # testing of rebuild function...

    # Auto storing
    limit = 3000000
    for i in range(300000):
        stats = api.get_owner_stats()
        print(i, stats)
        if stats['credits'] > limit:
            print('stored...')
            api.store_resources('credits', stats['credits']-limit)
        sleep(3)

    # Update Database Rankings
    # # manual update
    # with Database() as db:
    #     rankings = api.generate_rankings()
    #     db.save_rankings(rankings)
    #
    # # automatic updates
    # # with Database() as db:
    # #     for i in range(1000):
    # #         print('start')
    # #         rankings = api.generate_rankings()
    # #         db.save_rankings(rankings)
    # #         api.logout()
    # #         print('stop')
    # #         sleep(60*60)

    api.session.save_session()

"""
Basic Ideas:
First Step should always be determining the owner stats
-> game_stats (research time / costs, unit cost, building cost, land cost,
energy usage) should be updated once every tick and saved
-> if left over resources
    -> build buildings, huc, spies, buc (might need to trade credits)
    (-> huc, spies, buc in a way that left over resources is minimized (with
    max huc then max spies then buc), considering buying
    other resources with credits over gm)
    -> if nothing to build -> syn bank until not in dispo anymore
        if still money left over -> land / shares...?!?!

-> if no left over resources
    -> check gm and sell stuff up to threshold (spies no threshold, buc, huc
    manually saved in db?!), pricing, 10cr cheaper than market price
    -> threshold both on amount and price

-> a few min before each tick -> recheck game_stats
    -> if something went wrong take resources out of syn bank
       (e.g. not enough fp for research)

-> update storage prices once an hour...
-> if no tender online -> check resources and compare with store prices
"""