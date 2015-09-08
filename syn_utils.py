import json
from unipath import Path

from login.login import LoggedInSession


__all__ = ['BASE_DIR', 'TEST_DIR', 'RES_DIR',
           'get_secret', 'generate_session', 'main_link']

BASE_DIR = Path(__file__).resolve().ancestor(1)
TEST_DIR = Path(BASE_DIR, 'tests')
RES_DIR = Path(TEST_DIR, 'resources')

with open(Path(BASE_DIR, 'secrets.json'), 'r') as f:
    secrets = json.loads(f.read())


def get_secret(setting, secrets=secrets):
    return secrets[setting]


def generate_session():
    return LoggedInSession(
        user=get_secret('user'),
        password=get_secret('password')
    )


def string_to_int(x):
    return int(x.replace('.', ''))


class InconsistencyException(Exception):
    def __init__(self, message):
        super(InconsistencyException, self).__init__(message)