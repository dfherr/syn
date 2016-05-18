from datetime import date, datetime, timedelta

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

from database import Database


def analyse_player(
    rankings, syn_id,
    target_nw=None, target_ha=None, syn=None, frak=None, expands_last_tick=False, nw_drop=None,
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
    current_nw = player_rankings['nw'][id_current]
    try:
        last_id = list(player_rankings.index)[-2]
    except Exception:
        print current_name
        return

    # print(current_name)
    # print(eval(current_name))
    # print(str(current_name))
    # print(current_name.encode('utf8'))

    # some criteria for advanced searches
    meets_criteria = True

    # if peak >+, if dip <-
    if nw_drop is not None:
        drop = current_nw - player_rankings['nw'][last_id]
        if nw_drop < 0:
            if not drop < nw_drop:
                meets_criteria = False
            else:
                print(current_name, syn_id, current_syn, current_frak, drop)
        else:
            if not drop > nw_drop:
                meets_criteria = False
            else:
                print(current_name, syn_id, current_syn, current_frak, drop)

    if target_nw is not None:
        if not (target_nw[0] < current_nw < target_nw[1]):
            meets_criteria = False

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
            last_tick_ha = player_rankings['ha'][last_id]
            if last_tick_ha+5 < current_ha:
                print(current_name, syn_id, current_syn, current_frak, current_ha, -last_tick_ha+current_ha)
            else:
                meets_criteria = False

    if meets_criteria:
        fig = plt.figure(figsize=[10, 6], dpi=100)
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212, sharex=ax1)

        ax1.set_title('#{0} - {1} ({2} - {3})'.format(
            current_syn, current_name, current_frak, syn_id
        ))
        ax1.set_ylabel('NW')
        ax1.grid()
        plt.setp(ax1.get_xticklabels(), visible=False)

        ax2.set_ylabel('ha')
        ax2.grid()

        datemin = np.min(player_rankings['date'])
        datemax = np.max(player_rankings['date'])

        ax1.plot(player_rankings['date'], player_rankings['nw'])
        ax1.set_xlim(datemin, datemax+timedelta(hours=10))
        ax2.plot(player_rankings['date'], player_rankings['ha'])
        ax2.set_xlim(datemin, datemax+timedelta(hours=10))
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

        if not plot:
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m'))

        if save:
            plt.savefig('docs/round80/{0:02d}_{1}.png'.format(
                current_syn, current_name),
                dpi=150
            )
        if plot:
            plt.show()
        plt.close(fig)


def plot_multiple_players(rankings, syn_ids):
    fig = plt.figure(figsize=[10, 6])
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212, sharex=ax1)

    ax1.set_ylabel('NW')
    ax1.grid()
    plt.setp(ax1.get_xticklabels(), visible=False)

    ax2.set_ylabel('ha')
    ax2.grid()

    for syn_id in syn_ids:
        player_rankings = rankings[rankings['name'] == syn_id]

        datemin = np.min(player_rankings['date'])
        datemax = np.max(player_rankings['date'])

        id_current = max(player_rankings.index)
        current_name = player_rankings['current_name'][id_current]

        ax1.plot(player_rankings['date'], player_rankings['nw'], label=current_name)
        ax2.plot(player_rankings['date'], player_rankings['ha'])

    ax1.set_xlim(datemin, datemax+timedelta(hours=10))

    leg = ax1.legend(loc=2)
    for leg_obj in leg.legendHandles:
        leg_obj.set_linewidth(2.0)
    plt.savefig('docs/multiplot.png', dpi=150)
    plt.show()


def _find_closest_logs(date1, date2):
    # TODO:
    raise NotImplementedError


def find_top_ha_diff(n1, n2):
    # TODO:
    n = pd.merge(n1, n2, on=1)
    n.loc[:, 'ha_diff'] = pd.Series(n['2_x'] - n['2_y'])
    n.sort_index(by='ha_diff', inplace=True)
    return n


def find_top_nw_diff(n1, n2):
    # TODO:
    n = pd.merge(n1, n2, on=1)
    n.loc[:, 'nw_diff'] = pd.Series(n['3_x'] - n['3_y'])
    n.sort_index(by='nw_diff', inplace=True)
    return n


def generate_all_rankings(rankings, **kargs):
    names = []
    for name in rankings['name']:
        if name not in names:
            names.append(name)
            analyse_player(rankings, int(name), **kargs)


def filter_duplicates(rankings):
    # take only recent logs
    filtered_rankings = rankings[rankings.date > datetime.now()-timedelta(seconds=3600)]
    filtered_rankings = filtered_rankings.drop_duplicates(take_last=True, subset=['name'])

    return filtered_rankings


def find_highest_ha(rankings, n=25):
    rankings = rankings.sort(columns=['ha', 'nw'], ascending=False)
    print(rankings[:n])


def find_highest_nw(rankings, n=25):
    rankings = rankings.sort(columns=['nw'], ascending=False)
    print(rankings[:n])


def find_nw_drop(rankings, nw):
    raise NotImplementedError


def check_atter(rankings):
    atter = [
        140, # 25er atter
        231,
        11,
        # 41,  # 8 rohrratte, uic
        # 222,  # 17 destruktiv, bf
        # 100,  # 14 geeron, bf
        271,  # 21 trollofant, sl huc atter
        # 82,  # 8 gamlbe, uic
        # 45,  # 20 att gefahren, nof
        39,  # 8 rohrverleger, nof
    ]
    for i in atter:
        analyse_player(rankings, i, plot=True, save=True)


def check_victims(rankings):
    steals = [
        # 14,  # 20 wildpinkler, uic huc
        322,  # bacillus dreistus
        106,  # bacillus dreistus
        75,  # bacillus dreistus
        # 75,  # weihnachtsmann, spyseller
        # # 276,  # ascar spyseller
        # 254,  # 13 quelz, neb huc
        # 207,  # 1 maxi king, nof huc
        # 40,  # 23 chronovisor, nof huc
        # 46,  # 2 apres ski, nof huc
        # 206,  # 18 cronus, nof huc
        # 121,  # 15 wholpin nof eco huc
        # 197,  # 20 nuesse geklaut, uic huc fuc
        # 33,  # 19 hefty schlumpf, huc seller
        # 54,  # 11 Meerjungfraumann, huc seller
        # 231,  # 25 Nikolaus, auc seller
    ]
    for i in steals:
        analyse_player(rankings, i, plot=True, save=True)


def check_opponents(rankings):
    steals = [
        13,  # 5er
        225,  # 4er jahresendfluegler, uic
        13,  # 5er 5er, uic
        276,  # 13 balu, patlamer
        75,  # 11 weinnachtsmann, patlamer
   ]
    for i in steals:
        analyse_player(rankings, i, plot=True, save=True)

if __name__ == '__main__':
    pd.set_option('display.width', 200)
    pd.set_option('display.max_rows', 1000)

    with Database() as db:
        rankings = pd.DataFrame(db.read_rankings())
        rankings.columns = ['id', 'date', 'rank', 'name', 'current_name', 'frak', 'ha', 'nw', 'syn']

        # analyse_player(rankings, 178, plot=True, save=True)
        # analyse_player(rankings, 113, plot=True, save=True)

        # filtered_rankings = filter_duplicates(rankings)
        # find_highest_nw(filtered_rankings)
        # find_highest_ha(filtered_rankings)
        # generate_all_rankings(rankings)
        # generate_all_rankings(rankings, target_ha=[2000, 3500], plot=True)
        # generate_all_rankings(rankings, expands_last_tick=True)
        # generate_all_rankings(rankings, nw_drop=+30000)
        # generate_all_rankings(rankings, nw_drop=-30000)
        generate_all_rankings(rankings, syn=10, plot=True)
        # find_highest_drops
        # find_highest_peaks
        # check_atter(rankings)
        # check_victims(rankings)
        # check_opponents(rankings)

        # analyse_player(rankings, 76, plot=True, save=True)
        # analyse_player(rankings, 199, plot=True, save=True)
        # analyse_player(rankings, 87, plot=True, save=True)

        # plot_multiple_players(rankings, [7, 51, 30])
