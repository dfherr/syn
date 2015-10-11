#!/usr/bin/env python

from api import SynAPI
from database import Database
from time import sleep

if __name__ == '__main__':
    api = SynAPI()

    # Update Database Rankings
    # manual update
    with Database() as db:
        rankings = api.generate_rankings()
        db.save_rankings(rankings)

    # automatic updates
    # with Database() as db:
    #     for i in range(1000):
    #         print('start')
    #         rankings = api.generate_rankings()
    #         db.save_rankings(rankings)
    #         api.logout()
    #         print('stop')
    #         sleep(60*60)

    api.session.save_session()