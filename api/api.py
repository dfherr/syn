from datetime import datetime as dt

from .login import LoggedInSession
from scraper.rankings import scrape_syndicate, generate_user_rankings

# TODO: scraping with imported parser...
# TODO: stats_collection extern

__all__ = ['main_link', 'links', 'SynAPI']


def main_link(page):
    return 'http://www.syndicates-online.de/php/{0}'.format(page)


def syndicate_link(syn_number):
    return main_link('syndicate.php?rid={0}'.format(syn_number))

links = {
    'aktuelles': main_link('aktuelles'),
    'bonus': main_link('bonus.php'),
    'home': main_link('statusseite.php'),
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


class SynAPI(object):
    def __init__(self):
        self.session = LoggedInSession.get_session()

    # TODO: ASAP
    # Goal: update owner resources all the time
    # build military units (build prices updates once an hour...)
    # if cr too high,
    # capacity update...
    # buy from market / store(if 5% cheaper)
    # build military (-> HUC, Spies, Carrier...)
    # when selling, permanently tenders... to reasonable price
    def get_owner_resources(self):
        # TODO: use the smallest page for this step
        raise NotImplementedError

    def get_gm_resources(self):
        raise NotImplementedError

    def get_store_resources(self):
        raise NotImplementedError

    def get_military_stats(self):
        raise NotImplementedError

    def get_tenders(self):
        raise NotImplementedError

    def get_offers(self):
        raise NotImplementedError

    def discard_tender(self):
        raise NotImplementedError

    def discard_offer(self):
        raise NotImplementedError

    def take_bonus(self, bonus_id):
        """
        sends a get request to take the given bonuses

        bonus_id: 1 -> credits once a day
        bonus_id: 2 -> 5ha once an hour

        request example:
        ?type=1
        """
        if bonus_id not in bonus_types:
            raise KeyError('Wrong bonus id {0}'.format(bonus_id))

        return self.session.get(
            links['bonus'],
            params={'type': bonus_id},
            referral_link=links['home']
        )

    def build_area(self, amount):
        raise NotImplementedError

    def build_buildings(self, building, amount):
        raise NotImplementedError

    def build_military(self, unit, amount):
        """
        sends a post request to build the 'unit'
        'amount' times

        request example:
        offspecs=0&defspecs=0&
        elites=0&elites2=0&techs=0&
        offspies=0&defspies=190&intelspies=0&
        decision=build
        """
        if unit not in military:
            raise KeyError('{0} is not a military unit!'.format(unit))
        payload = {
            'offspecs': 0,
            'defspecs': 0,
            'elites': 0,
            'elites2': 0,
            'techs': 0,
            'offspies': 0,
            'defspies': 0,
            'intelspies': 0,
            'decision': 'build',
            request_names[unit]: amount,
        }
        return self.session.post(links['military'], data=payload)

    def _interact_with_market(self, unit, amount, price, action):
        """
        sends a post request to sell/order the 'unit' for 'price'
        times the 'amount'

        request example:
        input=bringin&product=elites2&price=4699&number=1
        input=gebot&product=elites2&price=4699&number=1
        """
        if unit not in military + resources:
            raise KeyError('It is not possible to sell/buy'
                           ' {0} at the market'.format(unit))
        payload = {
            'input': action,
            'product': request_names[unit],
            'price': price,
            'number': amount
        }
        return self.session.post(links['market'], data=payload)

    def sell(self, unit, amount, price):
        return self._interact_with_market(unit, amount, price, 'bringin')

    def order(self, unit, amount, price):
        return self._interact_with_market(unit, amount, price, 'gebot')

    def buy(self, unit, amount, price):
        """
        sends a post request to buy the 'unit' for 'price'
        times the 'amount' at the market

        request example:
        input=buy&anzahl=158470&buyprice=12&buyproduct=energy
        """
        if unit not in military + resources:
            raise KeyError('It is not possible to buy'
                           ' {0} at the market'.format(unit))
        payload = {
            'input': 'buy',
            'anzahl': amount,
            'buyprice': price,
            'buyproduct': request_names[unit]
        }
        return self.session.post(links['market'], data=payload)

    def cancel_selling(self, i):
        raise NotImplementedError

    def cancel_order(self, i):
        raise NotImplementedError

    def _interact_with_store(self, unit, amount, action):
        """
        sends a post request to the store to pull or store
        resources

        request example:
        energy=&metal=&sciencepoints=&money=10&inneraction=store
        energy=&metal=&sciencepoints=&money=10&inneraction=get
        """
        if unit not in resources:
            raise KeyError('You cannot store {0}'.format(unit))
        payload = {
            'energy': '',
            'metal': '',
            'sciencepoints': '',
            'money': '',
            'inneraction': action,
            request_names[unit]: amount
        }
        return self.session.post(links['store'], data=payload)

    def store_resources(self, unit, amount):
        return self._interact_with_store(unit, amount, 'store')

    def pull_store_resources(self, unit, amount):
        return self._interact_with_store(unit, amount, 'get')

    def pull_syn_resources(self, unit, amount):
        """
        sends a post request to pull resources from syn members

        request example:
        product=money&number=10&inneraction=getfromsyn
        """
        if unit not in resources:
            raise KeyError('Cannot pull {0} from syn members'.format(unit))
        payload = {
            'product': request_names[unit],
            'number': amount,
            'inneraction': 'getfromsyn'
        }
        return self.session.post(links['store'], data=payload)

    def buy_shares(self, syn, amount):
        raise NotImplementedError

    def get_fos_info(self):
        # fps = 0
        # time_left = 0
        # return time_left, fps
        raise NotImplementedError

    def generate_rankings(self):
        """
        Generates a full live ranking out of the
        'syndikat' page.

        returns:
        [(datetime.now(), 'rank', 'name', 'class', 'ha', 'nw'), ...]

        for manual output following pandas settings
        are recommended:
        pd.set_option('display.width', 200)
        pd.set_option('display.max_rows', 1000)
        """
        # TODO: find a way to automatically determine
        # amount of syndicates
        rankings = []
        for i in range(1, 29):
            r = self.session.get(syndicate_link(i))
            rankings += scrape_syndicate(i, r.content)
        rankings = generate_user_rankings(rankings)

        # add datetime and current rank
        for i in range(len(rankings)):
            rankings[i] = [dt.now(), i+1] + rankings[i]

        return rankings