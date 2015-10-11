#!/usr/bin/env python

from intelligence import Bot

if __name__ == '__main__':
    bot = Bot()
    bot.run()

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

-> if no left over resources
    -> check gm and sell stuff up to threshold (spies no threshold, buc, huc
    manually saved in db?!), pricing, 10cr cheaper than market price
    -> threshold both on amount and price(percentage)

-> a few min before each tick -> recheck game_stats
    -> if something went wrong take resources out of storage
       (e.g. not enough fp for research)

-> update storage prices once an hour...
"""