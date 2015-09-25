#!/usr/bin/env python

from api import SynAPI
from database import Database

if __name__ == '__main__':
    # Saves current rankings to db
    api = SynAPI()

    rankings = api.generate_rankings()
    with Database() as db:
        db.save_rankings(rankings)

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
"""