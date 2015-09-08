import unittest

from PIL import Image
from unipath import Path

from captcha.captcha_solver import solve_captcha
from rankings.rankings import scrape_syndicate
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
        """
        with open(Path(RES_DIR, 'syndicate/umlaute_syn.html'), 'r') as f:
            html = f.read()
            # Scrape Syndicates tests itself and throws an
            # InconsistencyException on error
            scrape_syndicate(1, html)

if __name__ == '__main__':
    unittest.main()