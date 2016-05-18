from .login import LoggedInSession
from .utils import *
from scraper import (
    scrape_area_cost,
    scrape_buildings,
    scrape_market_resources,
    scrape_owner_stats,
    scrape_store,
    scrape_shares,
    scrape_round_statistics,
    scrape_status_stats,
    scrape_syndicate,
    generate_user_rankings
)
from settings import syns_amount

__all__ = ['SynAPI']


class SynAPI(object):
    def __init__(self):
        self.session = LoggedInSession.get_session()

    def logout(self):
        """
        logout of session -> get to captcha page
        thus we have to use session.s (the python requests session)
        instead the LoggedInSession. Else it would try to do it over
        and over again -> see LoggedInSession.session.get docstring
        """
        self.session.session.get(links['logout'])

    def get_owner_stats(self):
        """
        Loads and scrapes from links['military'] to get all resources
        and remaining capacities
        """
        r = self.session.get(links['military'])
        return scrape_owner_stats(r.content)

    def get_gm_resources(self):
        """
        Loads and scrapes from links['market'] to get all market
        exchange rates and the market volumes
        """
        r = self.session.get(links['market'])
        return scrape_market_resources(r.content)

    def get_store_resources(self):
        """
        Loads and scrapes from links['store'] to get all store
        exchange rates and the store volumes
        """
        r = self.session.get(links['store'])
        return scrape_store(r.content)

    def get_suffered_spies(self):
        """
        Loads and scrapes the amount of suffered spys from links['stats']
        """
        r = self.session.get(links['stats'])
        return scrape_round_statistics(r.content)

    def get_next_fos(self):
        """
        Loads and scrapes the cost and start time of the
        next research from links['research']
        """
        # TODO: asap
        raise NotImplementedError

    def place_tender(self, unit, price, amount):
        """
        sends a post request to sell the 'unit'
        'amount' times for price 'price' at the market

        request example:
        input=bringin&product=energy&price=9&number=1
        """
        payload = {
            'input': 'bringin',
            'product': request_names[unit],
            'price': price,
            'number': amount
        }
        return self.session.post(links['market'], data=payload)

    def place_offer(self):
        raise NotImplementedError

    def get_tenders(self):
        """
        <tr>
        <form action="market.php" method="post">
        <input type="hidden" value="delete" name="input">
        <input type="hidden" value="42796" name="offer_id">
        <td width="110" align="center" class="tableInner1">
        &nbsp;Phoenix
        </td>
        <td width="110" align="center" class="tableInner1">
        89
        </td>
        <td width="110" align="center" class="tableInner1">
        2.960
        </td>
        <td width="50"  align="center" class="tableInner1">
        """
        raise NotImplementedError

    def get_offers(self):
        raise NotImplementedError

    def discard_tender(self):
        """
        http://www.syndicates-online.de/php/market.php
        POST /php/market.php HTTP/1.1
        Referer: http://www.syndicates-online.de/php/market.php
        input=delete&offer_id=41882
        """
        raise NotImplementedError

    def discard_offer(self):
        raise NotImplementedError

    def get_status_stats(self):
        """
        Loads and scrapes from links['home'] to get
        the
        """
        r = self.session.get(links['home'])
        return scrape_status_stats(r.content)

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

    def get_area_cost(self):
        """
        Loads and scrapes from links['area'] to get
        the cost of new ha
        """
        r = self.session.get(links['area'])
        return scrape_area_cost(r.content)

    def build_area(self, amount):
        """
        sends a post request to build the 'unit'
        'amount' times

        request example:
        inneraction=land&action=gebaeude&build_land=4&submit2=kaufen
        """
        payload = {
            'inneraction': 'land',
            'action': 'gebaeude',
            'build_land': amount,
            'submit2': 'kaufen'
        }
        return self.session.post(links['area'], data=payload)

    def get_buildings(self):
        """
        Loads and scrapes from links['area'] to get
        the cost of new building and unbuild buildings
        """
        r = self.session.get(links['area'])
        return scrape_buildings(r.content)

    def build_buildings(self, building, amount):
        """
        inneraction=gebaeude&action=gebaeude&
        tradecenters=&powerplants=&depots=1&
        ressourcefacilities=&sciencelabs=&
        spylabs=&buildinggrounds=&factories=&
        offtowers=&deftowers=&s_tradecenters=&
        s_powerplants=&schools=&workshops=&decision=build
        """
        if building not in buildings:
            raise KeyError('{0} is not a building!'.format(building))
        payload = {
            'inneraction': 'gebaeude',
            'action': 'gebaeude',
            buildings[building]: amount,
            'decision': 'build'
        }
        return self.session.post(links['area'], data=payload)

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

    def bulk_build_military(self, amounts, units):
        """
        e.g.:
        amounts = [10, 5], units = ['ranger', 'marine']
        builds 10 rangers and 5 marines
        returns an action output
        """
        for amount, unit in zip(amounts, units):
            self.build_military(unit, amount)
        return ' / '.join([
            'Build {0} {1}s'.format(x, y)
            for x, y in zip(amounts, units)
        ])

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

    def get_shares(self):
        """
        Loads and scrapes from links['shares'] to get
        all data on the shares page
        """
        r = self.session.get(links['shares'])
        return scrape_shares(r.content)

    def buy_shares(self, syn, amount):
        """
        action=buy&rid=18&number=291
        """
        payload = {
            'action': 'buy',
            'rid': syn,
            'number': amount
        }
        return self.session.post(links['shares'], data=payload)

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
        [(datetime.now(), 'rank', 'name',
        'class', 'ha', 'nw', 'syn'), ...]

        for manual output following pandas settings
        are recommended:
        pd.set_option('display.width', 200)
        pd.set_option('display.max_rows', 1000)
        """
        # amount of syndicates
        rankings = []
        for i in range(1, syns_amount+1):
            r = self.session.get(syndicate_link(i))
            rankings += scrape_syndicate(i, r.content)
        return generate_user_rankings(rankings)