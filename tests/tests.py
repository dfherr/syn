import copy
import random
import unittest
from PIL import Image

from unipath import Path

from api.captcha_solver import solve_captcha
from stats.rankings import scrape_syndicate, generate_user_rankings
from syn_utils import RES_DIR


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