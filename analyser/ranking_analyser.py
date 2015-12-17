from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pandas as pd

from database import Database


def analyse_player(rankings, name, target_ha, expands_last_tick=False, recent=False):
    """
    shows the development of player 'name'
    plots ha and nw on a timeline
    """
    player_rankings = rankings[rankings[3] == name]
    id_current = max(player_rankings.index)
    current_ha = player_rankings.loc[id_current][5]
    meets_criteria = True

    if not (target_ha[0] < current_ha < target_ha[1]):
        meets_criteria = False

    if expands_last_tick:
        try:
            last_id = list(player_rankings.index)[-2]
            last_tick_ha = player_rankings.loc[last_id][5]
            if last_tick_ha >= current_ha:
                meets_criteria = False
        except IndexError:
            meets_criteria = False

    if recent:
        time_stamp = player_rankings.loc[id_current][1]
        # d1 = datetime.strptime("%Y-%M-%D %H:%m:%s", str(time_stamp).split('.')[0])
        d2 = datetime.now()

    meets_criteria = True
    if not player_rankings.loc[id_current][4] == 'neb':
        meets_criteria = False

    syn = player_rankings.irow(0)[7]
    if True:
        dates = player_rankings.loc[:, 1]
        ha = player_rankings.loc[:, 5]
        nw = player_rankings.loc[:, 6]

        fig = plt.figure(figsize=[10, 6])
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212, sharex=ax1)

        ax1.set_title(name)
        ax1.set_ylabel('NW')
        ax1.grid()
        plt.setp(ax1.get_xticklabels(), visible=False)

        ax2.set_ylabel('ha')
        ax2.grid()

        ax1.plot(dates, nw)
        ax2.plot(dates, ha)
        plt.savefig('docs/round10/{0:02d}_{1}.png'.format(syn, name.encode('utf-8')))
        plt.show()
        plt.close(fig)
        print(name.encode('utf-8'))


def _find_logs(date1, date2):
    raise NotImplementedError


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


def generate_all_rankings(rankings, target_ha=[0000, 10000], expands_last_tick=False):
    names = []
    for name in rankings.loc[:, 3]:
        if name not in names:
            names.append(name)
            analyse_player(rankings, name, target_ha, expands_last_tick)


def find_highest_ha():
    pd.set_option('display.width', 200)
    pd.set_option('display.max_rows', 1000)

    db = Database()
    rankings = pd.DataFrame(db.read_rankings())
    rankings.columns = ['id', 'date', 'rank', 'name', 'class', 'ha', 'nw', 'syn']

    rankings = rankings[rankings.date > datetime.now()-timedelta(seconds=3600)]
    rankings = rankings.drop_duplicates(take_last=True, subset=['name'])
    rankings = rankings.sort(columns=['ha'], ascending=False)

    rankings = rankings[rankings.ha > 12500]

    print(rankings)


def find_highest_nw():
    pd.set_option('display.width', 200)
    pd.set_option('display.max_rows', 1000)

    db = Database()
    rankings = pd.DataFrame(db.read_rankings())
    rankings.columns = ['id', 'date', 'rank', 'name', 'class', 'ha', 'nw', 'syn']

    rankings = rankings[rankings.date > datetime.now()-timedelta(seconds=3600)]
    rankings = rankings.drop_duplicates(take_last=True, subset=['name'])
    rankings = rankings.sort(columns=['nw'], ascending=False)

    print(rankings[:25])

if __name__ == '__main__':
    find_highest_nw()
    find_highest_ha()

    with Database() as db:
        rankings = db.read_rankings()
        rankings = pd.DataFrame(rankings)
        pd.set_option('display.width', 200)
        pd.set_option('display.max_rows', 1000)

        names = ['DragonDisgrace', 'Major Hochstetter','Geldspeicher', 'Bob the Builder']

        for name in names:
            analyse_player(rankings, name, [0, 10000])
        generate_all_rankings(rankings)
