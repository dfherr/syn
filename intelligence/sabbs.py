#!/usr/bin/env python

from __future__ import division


def op(ha, spys=None, ctp=True, hn=7, gdz=20.0, ca=0.0):
    if spys is None:
        spys = [ha*(15 + 0.5*30), 0, 0]
    base_op = (spys[0]*2 + spys[1] + spys[2]) / ha
    if ctp:
        base_op += 8

    return base_op*(1 + hn*0.1 + gdz*0.01)


def dp(ha, spys=None, ctp=False, hn=3, issdn=3, syn_issdn=0.5, ops=0, difficulty=1.0):
    if spys is None:
        spys = [0, ha*15, 0]
    base_dp = (spys[0] + spys[1]*2 + spys[2]) / ha
    if ctp:
        base_dp += 18

    sabb_protection = 1 + 0.03*(ops-5)
    if sabb_protection < 0:
        sabb_protection = 0

    return difficulty * (base_dp * (1 + hn*0.1 + issdn*0.1 + syn_issdn)) * sabb_protection


def mili_sabs(off_ha, off_spys, def_ha, def_spys, def_units, n):
    grab = off_spys[0] * 0.015 + (off_spys[1]+off_spys[2]) * 0.0075
    print('Maxgrab: {0}'.format(grab))

    o = op(off_ha, off_spys)

    # TODO: CA
    for i in range(n * 65//3):
        d = dp(def_ha, def_spys, ops=i*3, difficulty=1.5)
        prob = 1 - d/(2*o)
        print(prob)
        break

        # sabs += prob
        # if prob < 0.01:
        #     prob = 0.01
        # ev_per_sab = prob*grab
        # s += ev_per_sab
        # print('{0}:\t {1:.4f} \t {2:07.2f} \t {3:08.2f}'.format(i, prob, ev_per_sab, s))


if __name__ == '__main__':
    off_ha = 1
    off_spys = [(12 + 27)*1.5, 0, 0]

    def_ha = 1
    def_spys = [0, 15, 0]

    mili_sabs(off_ha, off_spys, def_ha, def_spys, 1, 1)
