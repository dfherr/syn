import requests
from StringIO import StringIO
from time import time

from PIL import Image

from captcha.captcha_solver import solve_captcha


def main_link(page):
    return 'http://www.syndicates-online.de/{0}'.format(page)


class LoggedInSession(object):
    def __init__(self, user, password):
        login_payload = {
            'action': 'login',
            'user': user,
            'password': password,
        }
        user_agent = ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0)'
                      'Gecko/20100101 Firefox/40.')

        self.s = requests.Session()
        self.s.headers.update({'User-Agent': user_agent})
        self.s.post(main_link('index.php'), data=login_payload)

        self.refresh_session_captcha()

        if not self.successful_login():
            raise Exception('Login/Captcha Error')

    def successful_login(self):
        r = self.s.get(main_link('php/statusseite.php'))
        if 'Angriffsrechner' in r.content:
            return True
        else:
            return False

    def refresh_session_captcha(self, save_to_db=False):
        """
        refreshes the session captcha
        raises an Exception if the captcha isn't solvable
        """
        captcha = self.s.get(main_link('captcha.php?t={0}'.format(time)))
        img = Image.open(StringIO(captcha.content))
        code = solve_captcha(img)

        captcha_payload = {
            'action': 'login',
            'codeinput': code,
        }
        self.s.post(main_link('php/login.php'), data=captcha_payload)
        # TODO: handle incorrect captcha