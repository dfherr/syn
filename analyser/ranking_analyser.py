import matplotlib.pyplot as plt
import pandas as pd


from database import Database


def analyse_player(rankings, name):
    """
    shows the development of player 'name'
    plots ha and nw on a timeline
    """
    player_rankings = rankings[rankings[3] == name]
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

    plt.savefig('docs/{0}.png'.format(name))
    plt.show()


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

if __name__ == '__main__':
    with Database() as db:
        rankings = db.read_rankings()
        rankings = pd.DataFrame(rankings)
        pd.set_option('display.width', 200)
        pd.set_option('display.max_rows', 1000)
        s = 'VDI 6022 Blatt 2'
        analyse_player(rankings, s)