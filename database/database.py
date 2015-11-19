from datetime import datetime as dt
import sqlite3 as sql

from settings import sql_file


class Database(object):
    def __init__(self):
        self.con = sql.connect(sql_file,
                               detect_types=sql.PARSE_DECLTYPES)
        self.cur = self.con.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()

    def _create_table(self, name, create_string):
        self.con.execute("DROP TABLE IF EXISTS {0}".format(name))
        self.con.execute(create_string.format(name))
        self.con.commit()

    def create_database(self):
        """
        Creates a new Database. Careful - it will overwrite your
        old data!
        """
        self.create_table_actions()
        self.create_table_rankings()
        self.create_table_shares()
        self.create_table_storage()
        self.create_table_spies()

    def create_table_spies(self):
        """
        Table to save suffered spies
        """
        create_string = """
            CREATE TABLE {0} (
            id INTEGER PRIMARY KEY NOT NULL,
            spy_date TIMESTAMP NOT NULL,
            amount INTEGER NOT NULL)"""
        self._create_table('suffered_spies', create_string)

    def create_table_storage(self):
        """
        Table to save storage exchange rates
        """
        create_string = """
            CREATE TABLE {0} (
            id INTEGER PRIMARY KEY NOT NULL,
            storage_date TIMESTAMP NOT NULL,
            energy DOUBLE NOT NULL,
            erz DOUBLE NOT NULL,
            fp DOUBLE NOT NULL)"""
        self._create_table('storage', create_string)

    def create_table_rankings(self):
        """
        Table to save nw / ha rankings in
        """
        create_string = """
            CREATE TABLE {0} (
            id INTEGER PRIMARY KEY NOT NULL,
            rank_date TIMESTAMP NOT NULL,
            current_rank INTEGER NOT NULL,
            name TEXT NOT NULL,
            class TEXT NOT NULL,
            ha INTEGER NOT NULL,
            nw INTEGER NOT NULL,
            syn INTEGER NOT NULL)"""
        self._create_table('rankings', create_string)

    def create_table_actions(self):
        """
        Table to save bot actions / output
        """
        create_string = """
            CREATE TABLE {0} (
            id INTEGER PRIMARY KEY NOT NULL,
            action_date TIMESTAMP NOT NULL,
            action TEXT NOT NULL)"""
        self._create_table('actions', create_string)

    def create_table_shares(self):
        """
        Table to save shares stats
        """
        create_string = """
            CREATE TABLE {0} (
            id INTEGER PRIMARY KEY NOT NULL,
            shares_date TIMESTAMP NOT NULL,
            syn INTEGER NOT NULL,
            owning INTEGER NOT NULL,
            percentage_owning DOUBLE NOT NULL,
            overall INTEGER NOT NULL,
            price INTEGER NOT NULL)"""
        self._create_table('shares', create_string)

    def action_output(self, x, date):
        """
        prints and saves an bot action / output
        with formated datetime
        """
        print('{0}: {1}'.format(dt.strftime(date, "%H:%M"), x))
        self.cur.execute(
            'INSERT INTO actions '
            '(action_date, action) '
            'VALUES (?, ?)',
            [date, x]
        )
        self.con.commit()

    def save_shares(self, shares, date):
        """
        saves the scraped share amounts / prices etc.
        from scraper.shares in form of

        {syn: [owning, percentage_owning, amount, price], ...}

        to the database table 'shares':
        | ID | DATE | SYN | OWNING | PERCENTAGE_OWNING | OVERALL | PRICE |
        """
        tmp = []
        for key in shares.keys():
            tmp.append([key, date] + shares[key])
        # TODO: Bulk upload
        for syn in tmp:
            self.cur.execute(
                'INSERT INTO shares '
                '(shares_date, syn, owning, percentage_owning, overall, price) '
                'VALUES (?, ?, ?, ?, ?, ?)',
                syn
            )
            self.con.commit()

    def save_storage(self, store, date):
        """
        saves the scraped storage exchange rates
        from scraper.store in form of

        [(datetime.now(), 'energy', 'erz', 'fp')]

        to the database table 'storage':
        | ID | DATE | ENERGY | ERZ | FP |
        """
        tmp = [date, store['ex_energy'], store['ex_erz'], store['ex_fp']]
        self.cur.execute(
            'INSERT INTO storage '
            '(storage_date, energy, erz, fp) '
            'VALUES (?, ?, ?, ?)',
            tmp
        )
        self.con.commit()

    def save_spies(self, spies, date):
        """
        saves the scraped suffered
        from scraper.stats in form of

        [(datetime.now(), 'spies'), ...]

        to the database table 'storage':
        | ID | DATE | amount |
        """
        self.cur.execute(
            'INSERT INTO suffered_spies '
            '(spy_date, amount) '
            'VALUES (?, ?)',
            [date, spies]
        )
        self.con.commit()

    def save_rankings(self, rankings, date):
        """
        saves the scraped and ordered rankings
        from scraper.rankings in form of

        [(datetime.now(), 'rank', 'name',
        'class', 'ha', 'nw', 'syn'), ...]

        to the database table 'rankings':
        | ID | DATE | RANK | NAME | CLASS | HA | NW | SYN |
        """
        for i in range(len(rankings)):
            rankings[i] = [date, i+1] + rankings[i]

        # TODO: bulk upload...
        for rank in rankings:
            self.cur.execute(
                'INSERT INTO rankings '
                '(rank_date, current_rank, name, class, '
                'ha, nw, syn) '
                'VALUES (?, ?, ?, ?, ?, ?, ?)',
                rank
            )
            self.con.commit()

    def read_rankings(self):
        self.cur.execute('SELECT * FROM rankings')
        r = map(list, self.cur.fetchall())
        # Unicode Hack...
        for i in r:
            i[3] = eval(i[3])
        return r

    def get_last_log(self):
        # should be sql solution. This is dirty... but quick!
        self.cur.execute('SELECT * FROM actions WHERE action=?', ['end stats recording'])
        last_record = self.cur.fetchall()[-1]
        return last_record[1]
