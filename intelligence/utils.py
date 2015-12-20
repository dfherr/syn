from __future__ import division

from api.utils import res_names, unit_capas

import numpy as np


def split_units_per_ratio(amount, ratio):
    tmp = (amount*ratio).astype(int)
    if tmp.sum() < amount:
        tmp[0] += (amount - tmp.sum())
    return tmp


def calculate_taxed_cr(tax, quantity, ex_rate):
    # TODO: is that correct?!
    return int((quantity*ex_rate) / (1 - tax)) + 1


def prepare_resources(gm_resources, storage_resources, stats, tax):
    """
    Calculates where to get resources from
    Then prepares the parsed data for the seller_optimizer
    """
    ex_rate_names = ['ex_energy', 'ex_erz', 'ex_fp']
    resource_source = [
        'gm' if
        gm_resources[i] <= storage_resources[i] / (1.0-tax)
        else 'store' for i in ex_rate_names
    ]
    ex_rates = [0, 0, 0]
    volumes = [0, 0, 0]

    for j, x in enumerate(ex_rate_names):
        if resource_source[j] == 'gm':
            ex_rates[j] = gm_resources[x]
            volumes[j] = gm_resources[res_names[j]]
        else:
            ex_rates[j] = storage_resources[x]
            volumes[j] = storage_resources[res_names[j]]

    ex_rates = np.asarray([1] + ex_rates)
    volumes = np.asarray([0] + volumes)
    owner_resources = np.asarray([
        stats['credits'],
        stats['energy'],
        stats['erz'],
        stats['fp']
    ])

    return owner_resources, volumes, ex_rates, resource_source


def free_capas(stats, build_order):
    free = False
    for unit in build_order:
        if stats[unit_capas[unit]] > 0:
            free = True
    return free
