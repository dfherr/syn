import json
from unipath import Path


__all__ = ['BASE_DIR', 'TEST_DIR', 'RES_DIR',
           'sql_file', 'session_file',
           'get_secret', 'string_to_int']

BASE_DIR = Path(__file__).resolve().ancestor(1)
TEST_DIR = Path(BASE_DIR, 'tests')
RES_DIR = Path(TEST_DIR, 'resources')

sql_file = Path(BASE_DIR, 'Database.sql')
session_file = Path(BASE_DIR, 'last_session.pkl')

with open(Path(BASE_DIR, 'secrets.json'), 'r') as f:
    secrets = json.loads(f.read())


def get_secret(setting, secrets=secrets):
    return secrets[setting]


def string_to_int(x):
    return int(x.replace('.', ''))


# Different Links # DEPRECATED! moved to API
def main_link(page):
    return 'http://www.syndicates-online.de/{0}'.format(page)

login_link = main_link('php/login.php')
overview_link = main_link('php/statusseite.php')
military_link = main_link('php/militaerseite.php')