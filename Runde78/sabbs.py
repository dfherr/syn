#!/usr/bin/env python

from __future__ import division


def op(ha, spys=None, ctp=True, hn=4, gdz=20):
    if spys is None:
        spys = [ha*(15 + 0.5*30), 0, 0]
    base_op = spys[0]*2 + spys[1] + spys[2]

    bonus_op = 0
    if ctp:
        bonus_op = 8

    return (base_op/ha+bonus_op)*(1 + hn*0.1 + gdz*0.01)


def dp(ha, spys=None, ctp=False, hn=3, issdn=3, syn_issdn=0.52, sabbs=0):
    if spys is None:
        spys = [0, ha*15, 0]
    base_dp = spys[0] + spys[1]*2 + spys[2]

    bonus_dp = 0
    if ctp:
        bonus_dp = 18

    return (base_dp/ha+bonus_dp)*(1 + hn*0.1 + issdn*0.1 + syn_issdn + sabbs*0.09)


def mili_sabbs(off_ha, off_spys, def_ha, def_spys, n):
    grab = off_spys[0] * 0.015 +  (off_spys[1]+off_spys[2]) * 0.0075
    print('Maxgrab: {0}'.format(grab))

    s = 0
    sabbs = 0
    for i in range(n):
        prob = 1-(1.5*dp(def_ha, def_spys, sabbs=int(sabbs)))/(2*op(off_ha, off_spys))
        sabbs += prob
        if prob < 0.01:
            prob = 0.01
        ev_per_sabb = prob*grab
        s += ev_per_sabb
        print('{0}:\t {1:.4f} \t {2:07.2f} \t {3:08.2f}'.format(i, prob, ev_per_sabb, s))


if __name__ == '__main__':
    off_ha = 6200
    off_spys = [240000, 0, 0]

    def_ha = 21600
    def_spys = [26000, 570000, 5000]

    mili_sabbs(off_ha, off_spys, def_ha, def_spys, 3 * 65//3)