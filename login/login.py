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

        # get captcha and solve it
        # TODO: if it doesn't work, try again
        captcha = self.s.get(main_link('captcha.php?t={0}'.format(time)))
        self.img = Image.open(StringIO(captcha.content))
        number = solve_captcha(self.img)

        captcha_payload = {
            'action': 'login',
            'codeinput': number,
        }
        r = self.s.post(main_link('php/login.php'), data=captcha_payload)
        if 'Angriffsrechner' not in r.content:
            raise Exception('LOGIN ERROR')