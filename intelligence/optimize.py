from __future__ import division

import numpy as np

__all__ = ['area_optimizer', 'optimize_neb_wz', 'neb_prod', 'seller_optimizer']


def area_optimizer(cr, cost):
    return cr // cost


def optimize_neb_wz(ha, prodha, prodbonus, trade, syn_trade, output=False):
    wz = np.linspace(0, prodha, prodha+1)
    prod = np.zeros(wz.shape[0])
    for x in wz:
        prod[x] = neb_prod(ha, prodha, x, prodbonus, trade, syn_trade, output=False)

    if output:
        import matplotlib.pyplot as plt
        plt.plot(wz, prod)
        plt.show()

    m = prod.argmax()
    return m, prod[m]


def neb_prod(ha, prodha, wz, prodbonus, trade, syn_trade, output=False):
    """
    prodbonus _without_ synergy bonus!
    trade in cr
    syntrade in cr
    """
    base_prod = 250
    prod_gebs = prodha-wz

    synergy_bonus = prod_gebs*0.02
    if synergy_bonus > 0.5:
        synergy_bonus = 0.5

    wz_bonus = (wz/ha) * 8
    bonus = prodbonus + synergy_bonus + wz_bonus

    geb_prod = prod_gebs*base_prod*(1 + bonus)
    trade_prod = prod_gebs*(trade + syn_trade)

    prod = geb_prod + trade_prod

    if output:
        print ('synergy bonus', synergy_bonus)
        print ('wz_bonus', wz_bonus)
        print ('bonus', bonus)
        print ('geb_prod', geb_prod)
        print ('trade_prod', trade_prod)
        print ('prod', prod)

    return prod


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
                        # Use this, if always enough lgh
                        # if source[i-1] == 'gm':
                        if True:
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
