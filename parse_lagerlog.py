#!/usr/bin/env python3
import re

import numpy as np
import pandas as pd


regex = re.compile(r'<tr class="tableInner1">\s+'
                   '<td align="left">([\w\._ \-<>/]+)</td>\s+'
                   '<td align="left">([A-Za-z]+)</td>\s+'
                   '<td align="right">([\.0-9]+)</td>\s+'
                   '<td align="left">([A-Za-z]+)</td>\s+')

if __name__ == '__main__':
    with open('docs/lager.log', 'r') as f:
        html = f.read()

    data = []
    for names, res, amount, action in regex.findall(html):
        amount = int(amount.replace('.', ''))
        if '<i>' in names:
            name1, name2 = names.split(' <i>an</i> ')
            data.append([name1, res, amount, 'gezogen worden'])
            data.append([name2, res, amount, 'ziehen'])
        else:
            data.append([names, res, amount, action])

    df = pd.DataFrame(data)
    df.columns = ['name', 'resource', 'amount', 'action']
    pd.set_option('display.max_rows', 1000)
    pivot = pd.pivot_table(
        df,
        index=['name', 'resource', 'action'],
        aggfunc=np.sum
    )
    print(pivot)

    xls = pd.ExcelWriter('docs/lagerlog.xlsx')
    # for manager in pivot.index.get_level_values(0).unique():
    #    temp_df = pivot.xs(manager, level=0)
    pivot.to_excel(xls)
    xls.save()
