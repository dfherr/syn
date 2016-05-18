#!/usr/bin/env python3

import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scraper.utils import string_to_int


with open("spys.txt", "r") as f:
    spys = f.readlines()


i = 0
steals = []
while i < len(spys):
    if spys[i].startswith('Sie konnten folgende Ressourcen stehlen'):
        name = spys[i-8].split('\t')
        name = name[1].split(')')[0]
        name, syn = name.split(' (#')
        if spys[i+7].startswith('Summe'):
            val = spys[i+7].strip()
            amount = string_to_int(val.split(' ')[1])
        else:
            val = spys[i+3].strip()
            kind, amount = re.split('\s+', val)
            amount = string_to_int(amount)
            if kind == "Erz":
                amount *= 6
            if kind == "Foschungspunkte":
                amount *= 16
            if kind == "Energie":
                amount *= 1.2

        steals.append((name, syn, amount))
    i += 1


df = pd.DataFrame(steals)
# print(df)

df.columns = ['name', 'syn', 'amount']
pd.set_option('display.max_rows', 1000)
pivot = pd.pivot_table(
    df,
    index=['name', 'syn'],
    aggfunc=np.sum
).sort(columns='amount', ascending=False)
print(pivot)

top_x = 25
top_donators = []
for i in range(top_x):
    x = pivot.iloc[i]
    name = '{0} #{1}'.format(*x.name)
    amount = int(x.amount)
    top_donators.append((name, amount))

donators, amount = zip(*top_donators)
print(donators)
print(amount)

y_pos = np.arange(len(donators))

plt.barh(y_pos, amount, align='center', alpha=0.4)
plt.yticks(y_pos, donators)
plt.xlabel('Performance')
plt.title('How fast do you want to go today?')

plt.show()
