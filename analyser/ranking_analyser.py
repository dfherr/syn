from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pandas as pd

from database import Database


def analyse_player(
    rankings, syn_id,
    target_ha=None, syn=None, frak=None, expands_last_tick=False,
    save=True, plot=False
):
    """
    shows the development of player 'name' (which is the syndicates id)
    plots ha and nw on a timeline
    """
    player_rankings = rankings[rankings['name'] == syn_id]

    id_current = max(player_rankings.index)
    current_ha = player_rankings['ha'][id_current]
    current_syn = player_rankings['syn'][id_current]
    current_frak = player_rankings['frak'][id_current]
    current_name = player_rankings['current_name'][id_current]

    # some criteria for advanced searches
    meets_criteria = True

    if target_ha is not None:
        if not (target_ha[0] < current_ha < target_ha[1]):
            meets_criteria = False

    if syn is not None:
        if current_syn != syn:
            meets_criteria = False

    if frak is not None:
        if current_frak != frak:
            meets_criteria = False

    if expands_last_tick:
        if len(player_rankings.index) > 1:
            last_id = list(player_rankings.index)[-2]
            last_tick_ha = player_rankings['ha'][last_id]
            if last_tick_ha >= current_ha:
                meets_criteria = False

    if meets_criteria:
        fig = plt.figure(figsize=[10, 6])
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212, sharex=ax1)

        ax1.set_title(current_name)
        ax1.set_ylabel('NW')
        ax1.grid()
        plt.setp(ax1.get_xticklabels(), visible=False)

        ax2.set_ylabel('ha')
        ax2.grid()

        ax1.plot(player_rankings['date'], player_rankings['nw'])
        ax2.plot(player_rankings['date'], player_rankings['ha'])
        if save:
            plt.savefig('docs/round79/{0:02d}_{1}.png'.format(current_syn, current_name))
        if plot:
            plt.show()
        plt.close(fig)


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


def filter_duplicates(rankings):
    filtered_rankings = rankings[rankings.date > datetime.now()-timedelta(seconds=3600)]
    filtered_rankings = filtered_rankings.drop_duplicates(take_last=True, subset=['name'])

    return filtered_rankings


def find_highest_ha(rankings, n=25):
    rankings = rankings.sort(columns=['ha', 'nw'], ascending=False)
    print(rankings[:n])


def find_highest_nw(rankings, n=25):
    rankings = rankings.sort(columns=['nw'], ascending=False)
    print(rankings[:n])

if __name__ == '__main__':
    pd.set_option('display.width', 200)
    pd.set_option('display.max_rows', 1000)

    with Database() as db:
        rankings = pd.DataFrame(db.read_rankings())
        rankings.columns = ['id', 'date', 'rank', 'name', 'current_name', 'frak', 'ha', 'nw', 'syn']

        filtered_rankings = filter_duplicates(rankings)
        find_highest_nw(filtered_rankings)
        find_highest_ha(filtered_rankings, n=100)

        analyse_player(rankings, 24, plot=True)
