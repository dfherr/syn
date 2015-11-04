#!/usr/bin/env python
from datetime import datetime as dt
from time import sleep

from api import SynAPI
from database import Database


if __name__ == '__main__':
    api = SynAPI()
    last_log = -1

    # Update Database Rankings, storage prices and shares
    with Database() as db:
        while True:
            if last_log != dt.now().hour:
                last_log = dt.now().hour
                date = dt.now()

                db.action_output('login and start stats recording', date)

                db.action_output('rankings...', date)
                rankings = api.generate_rankings()
                db.save_rankings(rankings, date)

                date = dt.now()
                db.action_output('storage...', date)
                store = api.get_store_resources()
                db.save_storage(store, date)

                date = dt.now()
                db.action_output('shares...', date)
                shares = api.get_shares()
                db.save_shares(shares, date)

                api.logout()

                db.action_output('end stats recording and logout', dt.now())
            sleep(60)
