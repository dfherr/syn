from __future__ import division

import numpy as np
import scipy.optimize as opt

__all__ = [
    'area_optimizer', 'neb_buc_rate', 'neb_prod',
    'optimize_neb_wz', 'optimize_neb_buc',
    'optimize_oc', 'optimize_spy_kapas',
    'seller_optimizer'
]


def area_optimizer(cr, cost):
    return cr // cost


def optimize_neb_buc(capas, other_units, pats_construct):
    """ optimizes the amount of pats for given capas and other units """
    def f(x):
        """
        x = pats
        *(-1) cause scipy.optimize usually minimizes
        """
        return (-1)*neb_buc_rate(capas, x, other_units, pats_construct)

    result = opt.minimize_scalar(f)
    return result.x, -result.fun


def neb_buc_rate(capas, pats, others_units, pats_construct):
    """ interest on neb buc"""
    units = pats + others_units + pats_construct
    return pats * (0.018 - (units/capas)**1.5 / 80) * (1 + (others_units/units)**1.5)


def optimize_neb_wz(ha, prodha, prodbonus=1.836, trade=120, syn_trade=60, output=False):
    """ returns the optimal amounts of wz for given prod ha and trade lvl """
    # since small and discrete parameter space
    # just brute force the solution
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

    synergy_bonus = (prod_gebs / ha) * 0.02
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


def optimize_spy_kapas(
    ha, gebs, mil_units,
    bsm=0, isl=0, spy_flex=0, mil_flex=0, issdn=1,
    pb=0, neb=True, parade=True, garden=False
):
    """ returns the optimal amount of lh / spy labs to reach a certain amount of mili kapas """
    bonus = 0
    if neb:
        bonus += 2
    if parade:
        bonus += 2

    def kapas(ha, lh, spylabs, bonus):
        return ha*(12 + bonus) + lh*(12 + bsm*5 + pb) + spylabs*(3 + spy_flex*2)

    spy_bonus = 0
    if garden:
        spy_bonus += 3

    def spy_kapas(ha, lh, spylabs, bonus):
        return ha*(12 + bonus) + lh*(3 + mil_flex*2) + spylabs*(15 + isl*4 + pb)

    for i in range(gebs):
        k = kapas(ha, i, gebs-i, bonus)
        if k > mil_units:
            return [(i, k), (gebs-i, spy_kapas(ha, i, gebs-i, spy_bonus))]
    return Exception('Not possible to reach the amount of mili kapas with given parameters')


def optimize_oc(
    mil_units, spy_units, ha,
    bsm=2, isl=0, spy_flex=1, mil_flex=0, issdn=1,
    pb=0, neb=True, parade=True, garden=False
):
    # TODO: insert lower bounds... no negative values + max lh e.g.
    """ returns the minimum amount of lh/sl needed to reach maximum oc """
    mil_per_ha = 12
    if neb:
        mil_per_ha += 2
    if parade:
        mil_per_ha += 2

    mil_per_lh = 12 + 5*bsm
    if pb:
        mil_per_lh += 1

    mil_per_sl = 3 + 2*spy_flex

    spy_per_ha = 12 + issdn
    if garden:
        spy_per_ha += 3

    spy_per_sl = 15 + 5*isl
    if pb:
        spy_per_sl += 1

    spy_per_lh = 3 + 2*mil_flex

    # TODO: set constraints correct... no negative amount of lh/sl possible
    building_kapas = np.array([[mil_per_lh, mil_per_sl], [spy_per_lh, spy_per_sl]])
    units = np.array([mil_units/1.5 - ha*mil_per_ha, spy_units/1.5 - ha*spy_per_ha])
    return map(lambda x: int(x)+1, np.linalg.solve(building_kapas, units))
