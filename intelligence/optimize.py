from __future__ import division

import numpy as np

# gets filled by scraper
# cr, energy, erz, fp
owner = np.asarray([1242100, 175110, 67, 27137])
spy_price = np.asarray([280, 210, 0, 14])

# energy to cr, erz to cr, fp to cr
# insert 1 - cr to cr for consistent indexing
ex_rate = np.asarray([1, 1.4, 7.3, 17.2])
# nrg, erz, fp available at scraped price at market
# insert '0' for credits for consistent indexing
market_cap = np.asarray([0, 150000, 100000, 42788])

capacity_cap = 20000


def new_optimizer(owner, unit, ex, capacity_cap, market_cap):
    """
    Takes the scraped data and computes the optimal amount of
    units to produce using the current exchange rates,
    market volumes and capacities
    """
    temp_owner = owner.copy()
    temp_market = market_cap.copy()
    limiting_index = -1
    for amount in range(capacity_cap+1):
        for i in range(1, 4):
            if temp_owner[i] < amount*unit[i]:
                if temp_market[i] >= unit[i] and temp_owner[0] > ex[i]*unit[i]:
                    temp_owner[0] -= ex[i]*unit[i]
                    temp_market[i] -= unit[i]
                    temp_owner[i] += unit[i]
                else:
                    limiting_index = i
                    break
        if not temp_owner[0] > amount*unit[0]:
            amount -= 1
            break

    # calculate volume to buy from market for each resource
    # insert 0 for consistent indexing

    # don't use temp owner cause of possible overlay
    # but cause of that we have to remove negative values
    # if owner has more of a single resource than needed
    to_buy = np.asarray([0] + [
        amount*unit[i] - owner[i] for i in range(1, 4)
    ])
    to_buy[to_buy < 0] = 0
    # if market is capped buy everything to get the next ex/volume
    if limiting_index != -1:
        to_buy[limiting_index] = market_cap[limiting_index]

    return amount, to_buy


print(new_optimizer(owner, spy_price, ex_rate, capacity_cap, market_cap))
