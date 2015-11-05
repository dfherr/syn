__all__ = ['index_link', 'main_link', 'syndicate_link', 'links', 'request_names',
           'buildings', 'bonus_types', 'military', 'res_names', 'resources',
           'select_capas']


def main_link(page):
    return 'http://www.syndicates-online.de/php/{0}'.format(page)


def syndicate_link(syn_number):
    return main_link('syndicate.php?rid={0}'.format(syn_number))


def select_capas(unit):
    if unit in ['marine', 'ranger', 'auc', 'huc']:
        return 'capas_military'
    if unit in ['buc']:
        return 'capas_carrier'
    if unit in ['thief', 'guardian', 'agent']:
        return 'capas_spies'


index_link = 'http://www.syndicates-online.de/index.php'
links = {
    'aktuelles': main_link('aktuelles'),
    'area': main_link('gebaeude.php'),
    'bonus': main_link('bonus.php'),
    'captcha': 'http://www.syndicates-online.de/captcha.php?t={0}',
    'home': main_link('statusseite.php'),
    'login': 'http://www.syndicates-online.de/index.php',
    'logout': main_link('logout.php'),
    'military': main_link('militaerseite.php'),
    'market': main_link('market.php'),
    'news': main_link('nachrichten.php'),
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

res_names = ['energy', 'erz', 'fp']

buildings = {
    'lh': 'depots'
}
bonus_types = [1, 2]
military = ['marine', 'ranger', 'buc', 'auc', 'huc',
            'thief', 'guardian', 'agent']
resources = ['credits', 'energy', 'erz', 'fp']