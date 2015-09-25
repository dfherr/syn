import sqlite3 as sql

from syn_utils import sql_file


class Database(object):
    def __init__(self):
        self.con = sql.connect(sql_file,
                               detect_types=sql.PARSE_DECLTYPES)
        self.cur = self.con.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()

    def create_database(self):
        """
        Creates a new Database. Careful - it will overwrite your
        old data if there is an old database with the same table name!
        """
        create_string = """
                CREATE TABLE rankings (
                    id INTEGER PRIMARY KEY,
                    rank_date TIMESTAMP NOT NULL,
                    current_rank INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    class TEXT NOT NULL,
                    ha INTEGER NOT NULL,
                    nw INTEGER NOT NULL)"""
        self.con.execute("DROP TABLE IF EXISTS rankings")
        self.con.execute(create_string)
        self.con.commit()

    def save_rankings(self, rankings):
        """
        saves the scraped and ordered rankings
        from scraper.rankings in form of
        [(datetime.now(), 'rank', 'name', 'class', 'ha', 'nw'), ...]
        to the database table 'rankings':
        | ID | DATE | RANK | NAME | CLASS | HA | NW |
        """
        self.cur.execute('BEGIN TRANSACTION')
        for rank in rankings:
            self.cur.execute(
                'INSERT INTO rankings VALUES (?, ?, ?, ?, ?, ?)',
                rank
            )
        self.cur.execute('COMMIT')