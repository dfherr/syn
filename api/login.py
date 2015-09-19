import cPickle as pickle
from StringIO import StringIO
import time
from PIL import Image

import requests

from .captcha_solver import solve_captcha
from syn_utils import get_secret, main_link, overview_link, login_link


class LoggedInSession(object):
    def __init__(self, user, password):
        self.user = user
        self.password = password

        self.s = None
        self.retries = -1

        # log in and solve captcha
        self.build_session()
        self.refresh_session_captcha()

        # check if session successful
        r = self.s.get(overview_link)
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
            time.sleep(seconds)

    def get(self, link):
        """
        http get request

        check every get request for session validity
        and captcha validity
        if both is fine return the request object
        """
        self._retry_timer()
        r = self.s.get(link)
        if not self.check_login(r.content):
            r = self.get(link)

        return r

    def post(self, link, payload):
        """
        http post request

        check every post request for session validity
        and captcha validity
        if both is fine return the request object
        """
        self._retry_timer()
        r = self.s.post(link, payload=payload)
        if not self.check_login(r.content):
            r = self.post(link, payload)

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

        self.s = requests.Session()
        self.s.headers.update({'User-Agent': user_agent})
        self.s.post(main_link('index.php'), data=login_payload)

    def check_login(self, html):
        """
        checks first if the login was successful
        if not rebuild a new session and return false

        if it was successful check the captcha
        if captcha not successful try again and return false

        logs retries for to build a rising request time
        """
        # if "Passwort vergessen" in content your session id
        # is not available or not valid anymore
        if 'Passwort vergessen?' in html:
            self.build_session()
            self.retries += 1
            return False

        # if "action=account_cfg" (-> "Account verwalten") in content
        # you still have to solve the captcha
        # attempts = 0
        if 'action=account_cfg' in html:
            # if attempts == captcha_attempt_cap:
            #     return False
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
        captcha = self.s.get(main_link('captcha.php?t={0}'.format(time.time)))
        img = Image.open(StringIO(captcha.content))
        code = solve_captcha(img)

        captcha_payload = {
            'action': 'login',
            'codeinput': code,
        }
        self.s.post(login_link, data=captcha_payload)

    def save_session(self):
        """
        saves the last session object to reduce the
        amount of logins.
        """
        with open('last_session.pkl', 'wb') as f:
            pickle.dump(self, f, -1)

    @staticmethod
    def load_session():
        """
        loads the saved session object and returns it
        if the file is not available return a none object
        """
        try:
            with open('last_session.pkl', 'rb') as f:
                return pickle.load(f)
        except IOError:
            return None

    @classmethod
    def get_session(cls):
        """
        loads and checks the last session
        if it's not valid anymore, generate a new session
        """
        last_session = cls.load_session()
        if last_session is not None:
            if last_session.successful_login():
                return last_session

        return LoggedInSession(
            user=get_secret('user'),
            password=get_secret('password')
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        implement a context manager to ensure the
        saving of the session object
        """
        self.save_session()

    def __enter__(self):
        return self.__class__.get_session()


class SynAPI(object):
    # TODO: Think about setting referrers ... e.g. don't
    # post a tender without referrer to the market
    pass