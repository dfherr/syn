# __author__ = 'sol1x'
# ranking analysis
#
# In [100]: n = pd.merge(n2, n3, on=1)
# In [101]: n.loc[:, 'z'] = pd.Series(n['3_x'] - n['3_y'])
# n.sort_index(by='z', inplace=True)
#
# def diff(n1, n2):
#     n = pd.merge(n1, n2, on=1)
#     n.loc[:, 'z'] = pd.Series(n['3_x'] - n['3_y'])
#     n.sort_index(by='z', inplace=True)
#     return n
#
#
# for x in log:
#     data, data_date = x
#     nw.append(data[data[1]=='Vollidioten'][3])
#     ha.append(data[data[1]=='Vollidioten'][2])
#     dates.append(data_date)
#
# pandas unicode -> ?!
#
#  for x in log:
#     data, data_date = x
#     nw.append(data[data[1]=='Vollidioten'][3])
#     ha.append(data[data[1]=='Vollidioten'][2])
#     dates.append(data_date)


import pandas as pd


def find_top_ha_diff(n1, n2):
    n = pd.merge(n1, n2, on=1)
    n.loc[:, 'ha_diff'] = pd.Series(n['2_x'] - n['2_y'])
    n.sort_index(by='ha_diff', inplace=True)
    return n


def find_top_nw_diff(n1, n2):
    n = pd.merge(n1, n2, on=1)
    n.loc[:, 'nw_diff'] = pd.Series(n['3_x'] - n['3_y'])
    n.sort_index(by='nw_diff', inplace=True)
    return n