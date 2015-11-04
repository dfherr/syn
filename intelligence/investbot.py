from __future__ import division

from datetime import datetime, timedelta
from time import sleep

import numpy as np

from api import SynAPI
from database import Database


def stamped_output(x):
    d = datetime.now()
    x = str(x)
    # TODO: save to db
    print(datetime.strftime(d, "%H:%M"), x)


class INVESTBot(object):
    def __init__(self):
        """
        - spends every cr over 40m on shares
        - sells divis on market, spends rewards on shares
        - tracks storage prices
        - tracks rankings
        TODO: if everything works, checks energy / fp usage next tick
        TODO: if everything works, implement huc trading
        """
        self.api = SynAPI()
        self.db = Database()
        self.max_cash = 40000000
        self.refresh_timedelta = 15
        self.syn_shares = [8, 10, 13, 21]

        self.refresh = datetime.now()-timedelta(minutes=self.refresh_timedelta)
        self.last_log = datetime.now().hour - 1
        self.base_stats = None
        self.shares = None

    def handle_cash(self):
        """
        buys energy and fp needed for next tick
        spends cr on shares of self.syn_shares
        maximizes percentage/own percentage?! -> max divi gain...
        """
        cr = self.base_stats['credits'] - self.max_cash
        if cr > 0:
            self.shares = self.api.get_shares()
            syn = self.syn_shares[0]
            owning = 100.

            # TODO in future: maximize divi... -> return syn and amount
            for i in self.syn_shares:
                if self.shares[i][1] < owning:
                    syn = i
                    owning = self.shares[i][1]

            amount = cr // self.shares[3]
            stamped_output('Buy {0} shares of #{1} for {2}'.format(amount, syn, amount))
            self.api.buy_shares(syn, amount)

    def handle_ressis(self):
        """
        sells ressis on gm
        """
        raise NotImplementedError

    def run(self):
        """
        starts the bot and contains the basic triggers
        """
        while True:
            if self.last_log != datetime.now().hour:
                stamped_output('start log')
                rankings = self.api.generate_rankings()
                self.db.save_rankings(rankings)
                store = self.api.get_store_resources()
                self.db.save_storage(store)
                self.api.logout()
                stamped_output('end log')
                self.last_log = datetime.now().hour

            if self.refresh+self.refresh_timedelta < datetime.now():
                self.base_stats = self.api.get_owner_stats()
                stamped_output(self.base_stats)
                self.handle_cash()
                # TODO: get tenders
                # TODO: place new tenders

                self.refresh = datetime.now()
                self.api.logout()
            sleep(60)
