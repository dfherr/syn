from __future__ import division

import numpy as np


def area_optimizer(cr, cost):
    return cr // cost


def seller_optimizer(owner, unit, ex, capacity_cap, market_cap, source):
    """
    Takes the scraped data and computes the optimal amount of
    units to produce using the current exchange rates,
    market volumes, capacities and unit prices

    returns how many units can be produced and how much resources
    have to be bought
    """
    if capacity_cap == 0:
        return 0, np.asarray([0, 0, 0, 0])
    temp_owner = owner.copy()
    temp_market = market_cap.copy()
    limiting_index = -1

    amount = 0
    breaker = True
    while amount < capacity_cap:
        amount += 1
        # for amount in range(1, capacity_cap+1):
        for i in range(1, 4):
            if temp_market[i] >= unit[i]:
                if temp_owner[i] < amount * unit[i]:
                    if temp_owner[0] >= ex[i] * unit[i]:
                        if source[i-1] == 'gm':
                            temp_owner[0] -= ex[i] * unit[i]
                        temp_market[i] -= unit[i]
                        temp_owner[i] += unit[i]
                    else:
                        breaker = False
                        break
            else:
                limiting_index = i
                break

        if temp_owner[0] < amount * unit[0] or limiting_index != -1 or not breaker:
            amount -= 1
            break

    # calculate volume to buy from market for each resource
    # insert 0 for consistent indexing

    # don't use temp owner cause of possible overlay
    # but cause of that we have to remove negative values
    # if owner has more of a single resource than needed
    to_buy = np.asarray([0] + [
        amount * unit[i] - owner[i] for i in range(1, 4)
    ])
    to_buy[to_buy < 0] = 0

    # if market provides only a limited amount
    # buy everything to get the next ex/volume
    if limiting_index != -1:
        to_buy[limiting_index] = market_cap[limiting_index]

    return amount, to_buy