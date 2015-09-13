from datetime import datetime, timedelta

from .owner_stats import get_owner_stats
from syn_utils import military_link


class StatsCollection(object):
    def __init__(self, update_limits, session):
        """
        game stats are saved in self.stats
        the last refresh point of these stats is saved in self.updates
        update_limits gives the refreshing rate in seconds of each update
        """
        self.stats = {}
        self.updates = {}
        self.update_limits = {}
        self.session = session

        # transform the given update_limits to timedeltas
        for key, value in update_limits.iteritems():
            self.update_limits[key] = timedelta(seconds=value)

        # insert fake date for first update
        # and fully construction of values
        last_update = datetime(year=2000, month=1, day=1)

        self.updates['owner_stats'] = last_update
        self.updates['owner_military'] = last_update
        # energy / fp / resources per military unit
        self.updates['owner_needed_resources'] = last_update
        self.updates['gm_stats'] = last_update
        self.updates[''] = ''

        # check if for every stat there is a
        # update limit, if not raise an exception
        for key in self.updates:
            if key not in self.update_limits:
                raise Exception('Improperly configured: missing '
                                'update_limits["{0}"] in syn_utils'
                                .format(key))

        # call refresh to get the initial data
        self.refresh()

    def time_add(self, key):
        return self.updates[key] + self.update_limits[key]

    def refresh(self):
        """
        compare date times of last updates
        if last update of certain stat too old,
        update it
        add random distribution on update limits
        """
        refresh_time = datetime.now()

        # military page can be used for both
        # owner_stats and owner_military
        stats_refresh = self.time_add('owner_stats') < refresh_time
        military_html = self.session.s.get(military_link)
        # TODO: think about interaction with bot... what does really need updates
        if stats_refresh:
            # TODO:
            self.updates['owner_stats'] = refresh_time

    def force_refresh(self):
        raise NotImplementedError

    def save_to_db(self):
        """
        saves the whole object to a db to compare and
        understand correlations for future rounds
        might be useful for full spy bot too
        """
        raise NotImplementedError