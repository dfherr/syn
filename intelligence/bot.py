from scraper.stats_collection import StatsCollection
from .optimize import *


class Bot(object):
    def __init__(self, session):
        """
        should handle all the session interaction
        TODO: decouple StatsCollection from session
        TODO: session id running out... how to handle this!?
        """
        self.session = session
        self.game_stats = StatsCollection()

    def run(self):
        """
        starts the bot
        """
        raise NotImplementedError