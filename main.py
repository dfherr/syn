#!/usr/bin/env python

from api import SynAPI
from database import Database

if __name__ == '__main__':
    # Saves current rankings to db
    api = SynAPI()
    with Database() as db:
        # db.create_database()
        rankings = api.generate_rankings()
        db.save_rankings(rankings)

    api.session.save_session()

"""
# TODO: save rankings
# TODO: save gamestats
# to db

# TODO: scrape Land -> alle 60min
# TODO: scrape Forschung -> alle 60min
# TODO: scrape credits -> scrape militär
# TODO: scrape gm
# TODO: post für Land/Militär/GM
# TODO: BOT -> self.gamestats ... some time handling....

Basic Ideas:
First Step should always be determining the owner stats
-> game_stats (research time / costs, unit cost, building cost, land cost,
energy usage) should be updated once every tick and saved
-> if left over ressources
    -> build buildings, huc, spys, buc (might need to trade credits)
    (-> huc, spys, buc in a way that left over ressources is minimized (with
    max huc then max spys then buc), considering buying
    other ressources with credits over gm)
    -> if nothing to build -> syn bank until not in dispo anymore
        if still money left over -> land / shares...?!?!

-> if no left over ressources
    -> check gm and sell stuff up to threshold (spys no threshold, buc, huc
    manually saved in db?!), pricing, 10cr cheaper than market price
    -> threshold both on amount and price

-> a few minuts before each tick -> recheck game_stats
    -> if smth went wrong take ressources out of syn bank
"""