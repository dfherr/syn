import cPickle as pickle
from StringIO import StringIO
import time
from PIL import Image

import requests

from .captcha_solver import solve_captcha
from .utils import links, main_link
from settings import get_secret, session_file


__all__ = ['LoggedInSession']


class LoggedInSession(object):
    """
    basically an extended python requests session
    automatically re-logs in after session id ran out
    automatically solves captchas

    make a new session with LoggedInSession.get_session()
    save the session with session.save_session()
    post request with session.post(link, payload)
    get request with session.get(link, params)

    doesn't make requests too fast
    at least 'delay' + 'delay_dev' seconds
    """
    def __init__(self, user, password, delay=0, delay_dev=0):
        self.user = user
        self.password = password

        self.session = None
        self.retries = -1

        # log in and solve captcha
        self.build_session()
        self.refresh_session_captcha()

        # check if session successful
        r = self.session.get(links['home'])
        if not self.check_login(r.content):
            raise Exception('Login Error')

    def _retry_timer(self):
        """
        timer for request methods
        if not successful for multiple times
        the sleeping time in between requests
        rises as 2^retries in seconds
        """
        if self.retries != -1:
            seconds = 2**self.retries
            print('Request failed try again in {0}s'.format(seconds))
            time.sleep(seconds)

    def get(self, link, params={}, referral_link=''):
        """
        http get request

        check every get request for session validity
        and captcha validity
        if both is fine return the request object
        """
        self._retry_timer()
        r = self.session.get(
            link, params=params, headers={'referrer': referral_link}
        )
        if not self.check_login(r.content):
            r = self.get(link)

        return r

    def post(self, link, data):
        """
        http post request

        check every post request for session validity
        and captcha validity
        if both is fine return the request object
        """
        self._retry_timer()
        r = self.session.post(link, data=data, headers={'referrer': link})
        if not self.check_login(r.content):
            r = self.post(link, data=data)

        return r

    def build_session(self):
        """
        send log in credentials and save cookies in
        a python requests session
        """
        login_payload = {
            'action': 'login',
            'user': self.user,
            'password': self.password,
        }
        user_agent = ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0)'
                      'Gecko/20100101 Firefox/40.')

        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})
        self.session.post(links['login'], data=login_payload)

    def check_login(self, html, build=True):
        """
        checks first if the login was successful
        if not rebuild a new session and return false

        if it was successful check the captcha
        if captcha not successful try again and return false

        logs retries for to build a rising request time

        if build is False, this function doesn't refresh the
        session
        """
        # if "Passwort vergessen" in content your session id
        # is not available or not valid anymore
        if 'Passwort vergessen?' in html:
            if build:
                self.build_session()
                self.retries += 1
            return False

        # if "action=account_cfg" (-> "Account verwalten") in content
        # you still have to solve the captcha
        if 'action=account_cfg' in html:
            if build:
                self.refresh_session_captcha()
                self.retries += 1
            return False

        # reset retries if everything works
        self.retries = -1
        return True

    def refresh_session_captcha(self):
        """
        refreshes the session captcha
        raises an Exception if the captcha isn't solvable
        """
        captcha = self.session.get('http://www.syndicates-online.de/captcha.php?t=1441314520')  # main_link('captcha.php?t={0}'.format(time.time)))
        img = Image.open(StringIO(captcha.content))
        code = solve_captcha(img)

        captcha_payload = {
            'action': 'login',
            'codeinput': code,
        }
        self.session.post(main_link('login.php'), data=captcha_payload)

    def save_session(self):
        """
        saves the last session object to reduce the
        amount of logins.
        """
        with open(session_file, 'wb') as f:
            pickle.dump(self, f, -1)

    @staticmethod
    def load_session():
        """
        loads the saved session object and returns it
        if the file is not available return a none object
        """
        try:
            with open(session_file, 'rb') as f:
                return pickle.load(f)
        except IOError:
            return None

    @classmethod
    def get_session(cls, new_session=False):
        """
        loads and checks the last session
        if it's not valid anymore, generate a new session
        """
        if not new_session:
            last_session = cls.load_session()
            if last_session is not None:
                try:
                    r = last_session.s.get(links['home'])
                    if last_session.check_login(r.context):
                        return last_session
                except AttributeError as e:
                    # If session object is corrupted
                    pass

        return LoggedInSession(
            user=get_secret('user'),
            password=get_secret('password')
        )