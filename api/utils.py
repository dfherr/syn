__all__ = ['main_link', 'syndicate_link', 'links', 'request_names',
           'buildings', 'bonus_types', 'military', 'resources']


def main_link(page):
    return 'http://www.syndicates-online.de/php/{0}'.format(page)


def syndicate_link(syn_number):
    return main_link('syndicate.php?rid={0}'.format(syn_number))

links = {
    'aktuelles': main_link('aktuelles'),
    'bonus': main_link('bonus.php'),
    'home': main_link('statusseite.php'),
    'login': main_link('login.php'),
    'logout': main_link('logout.php'),
    'military': main_link('militaerseite.php'),
    'market': main_link('market.php'),
    'shares': main_link('anleihenmarkt.php'),
    'store': main_link('pod.php'),
    'research': main_link('forschung.php'),
}

request_names = {
    'marine': 'offspecs',
    'ranger': 'defspecs',
    'buc': 'elites',
    'auc': 'elites2',
    'huc': 'techs',
    'thief': 'offspies',
    'guardian': 'defspies',
    'agent': 'intelspies',
    'energy': 'energy',
    'erz': 'metal',
    'fp': 'sciencepoints',
    'credits': 'money',
}
buildings = ['']
bonus_types = [1, 2]
military = ['marine', 'ranger', 'buc', 'auc', 'huc',
            'thief', 'guardian', 'agent']
resources = ['credits', 'energy', 'erz', 'fp']