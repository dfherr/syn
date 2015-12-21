#!/usr/bin/env python

from intelligence import BaseBot, StatsBot


class NEBBot(BaseBot, StatsBot):
    def __init__(self):
        super(NEBBot, self).__init__()
        self.last_hour = self.last_stats()

        self.active = True
        self.sleep_time = 30

        # self.jobs.append(self.spend_cr)
        # self.jobs.append(self.buy_resources)

        self.hourly_jobs.append(self.take_log)
        # self.hourly_jobs.append(self.sell_open_prod)

    def sell_open_prod(self):
        """ Reasonable part of open prod should be in erz """
        raise NotImplementedError

    def spend_cr(self):
        """ Gebs, HUC(OC?), Spies, Ha, Store ->
        how much erz can get sold each tick? """
        raise NotImplementedError

    def buy_resources(self):
        """ Energy & FP for next tick """
        raise NotImplementedError

if __name__ == '__main__':
    bot = NEBBot()
    bot.run()
