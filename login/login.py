import cPickle as pickle
import requests
from StringIO import StringIO
from time import time

from PIL import Image

from captcha.captcha_solver import solve_captcha
from syn_utils import get_secret, main_link, overview_link, login_link


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

        if not self.successful_login():
            raise Exception('Login Error')

    def successful_login(self, captcha_attempt_cap=5):
        """
        checks first if the login was successful
        if it was successful solve captchas until one
        captcha is successfully solved
        (max attempts = captcha_attempt_cap)

        return True if everything was successful
        else return False
        """
        r = self.s.get(overview_link)
        # if "Passwort vergessen" in content your session id
        # is not available or not valid anymore
        if 'Passwort vergessen?' in r.content:
            print('Logged Out!')
            return False

        # if "action=account_cfg" (-> "Account verwalten") in content
        # you still have to solve the captcha
        attempts = 0
        while 'action=account_cfg' in r.content:
            if attempts == captcha_attempt_cap:
                return False
            print('refreshing captcha')
            self.refresh_session_captcha()
            r = self.s.get(overview_link)
            attempts += 1

        return True

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
        pass