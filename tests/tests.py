import copy
import os
import random
import unittest
from PIL import Image

from unipath import Path

from api import LoggedInSession
from api.pages import SynPages
from api.captcha_solver import solve_captcha
from scraper.rankings import scrape_syndicate, generate_user_rankings
from syn_utils import BASE_DIR, RES_DIR, session_file, overview_link


class TestSynPageMethods(unittest.TestCase):
    """
    checks if all page links are still valid
    """
    def test_home(self):
        session = LoggedInSession.get_session()
        pages = SynPages(session)

        self.assertEqual(pages.home.status_code, 200)
        self.assertEqual(pages.area.status_code, 200)
        self.assertEqual(pages.military.status_code, 200)
        self.assertEqual(pages.research.status_code, 200)
        self.assertEqual(pages.syndicate(1).status_code, 200)
        self.assertEqual(pages.market.status_code, 200)
        self.assertEqual(pages.storage.status_code, 200)
        self.assertEqual(pages.shares.status_code, 200)


class TestLoginMethods(unittest.TestCase):
    def test_check_login(self):
        """
        check if we are on start / captcha page
        don't take live data for consistency purposes
        - load local copies of the pages
        """
        session = LoggedInSession.get_session()

        # Load different html
        with open(Path(RES_DIR, 'home/home_account.html'), 'r') as f:
            overview_html = f.read()
            self.assertEqual(
                session.check_login(overview_html, build=False),
                True
            )

    def test_session_save(self):
        """
        tests if login with credentials and
        the session saving is working properly
        - first the last session gets deleted
        - a new session is generated via contextmanager
        - check if file is available
        """
        path = Path(BASE_DIR, session_file)
        os.remove(path)
        session = LoggedInSession.get_session()
        session.save_session()
        self.assertEqual(os.path.isfile(path), True)

    def test_session_load(self):
        """
        loads the session of the last test and makes a request
        """
        with LoggedInSession.get_session() as session:
            r = session.s.get(overview_link)
            self.assertEqual(session.check_login(r.content), True)

    def test_refresh_session(self):
        """
        tests the refresh of expiring captchas / session ids
        the implemented 'get' should refresh both by itself using
        the check_login method
        - generate a session
        - to make the first session expire generate a new session
        - check if sessions have access to the overview page
        """
        session = LoggedInSession.load_session()
        session2 = LoggedInSession.get_session(new_session=True)

        # old session got deleted server side
        r = session.s.get(overview_link)
        self.assertEqual(session.check_login(r.content, build=False), False)
        # but the new one should work
        r = session2.s.get(overview_link)
        self.assertEqual(session2.check_login(r.content, build=False), True)

        # with the new get method the session should get refreshed
        r = session.get(overview_link)
        self.assertEqual(session.check_login(r.content, build=False), True)


class TestCaptchaMethods(unittest.TestCase):
    def test_solve_captcha(self):
        """
        Tries to solve several captchas:
        captcha1: 065
        captcha2: 764
        captcha3: 572
        captcha4: 501 -> too close to wall?
        captcha5: 911 -> ??
        captcha6: 429
        """
        img = Image.open(Path(RES_DIR, 'captcha/captcha1.png'))
        code = solve_captcha(img)
        self.assertEqual(code, '065')

        img = Image.open(Path(RES_DIR, 'captcha/captcha2.png'))
        code = solve_captcha(img)
        self.assertEqual(code, '764')

        img = Image.open(Path(RES_DIR, 'captcha/captcha3.png'))
        code = solve_captcha(img)
        self.assertEqual(code, '572')

        img = Image.open(Path(RES_DIR, 'captcha/captcha4.png'))
        code = solve_captcha(img)
        self.assertEqual(code, '501')

        img = Image.open(Path(RES_DIR, 'captcha/captcha5.png'))
        code = solve_captcha(img)
        self.assertEqual(code, '911')

        img = Image.open(Path(RES_DIR, 'captcha/captcha6.png'))
        code = solve_captcha(img)
        self.assertEqual(code, '429')

        img = Image.open(Path(RES_DIR, 'captcha/captcha7.png'))
        code = solve_captcha(img)
        self.assertEqual(code, '470')


class TestRankingMethods(unittest.TestCase):
    def test_scrape_rankings(self):
        """
        Executes the scraping algorithm
        compares the summed up individual values
        with the scraped sum in html

        scrape_syndicates tests itself for self
        consistency
        if its not self consistent it returns []
        """
        with open(Path(RES_DIR, 'syndicate/umlaute_syn.html'), 'r') as f:
            html = f.read()
        ranks = scrape_syndicate(1, html)
        self.assertGreater(len(ranks), 0)

        with open(Path(RES_DIR, 'syndicate/owner_syn.html'), 'r') as f:
            html = f.read()
        ranks = scrape_syndicate(1, html)
        self.assertGreater(len(ranks), 0)

    def test_generate_user_rankings(self):
        """
        Insert a sorted list. Shuffle it with random.shuffle.
        generate_user_rankings should sort the list via the
        user's networth.
        """
        ranks = [
            ['sl', 'unknown', 1742, 883169, 13],
            ['bf', 'Hippie Knight Rider', 2289, 869024, 6],
            ['sl', 'Bacillus Feriatio', 405, 848358, 18],
            ['sl', 'von', 2289, 846062, 25],
        ]
        new_ranks = copy.copy(ranks)
        random.shuffle(new_ranks)
        new_ranks = generate_user_rankings(new_ranks)
        self.assertEqual(new_ranks, ranks)


if __name__ == '__main__':
    unittest.main()