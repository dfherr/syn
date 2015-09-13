import json
from unipath import Path


__all__ = ['BASE_DIR', 'TEST_DIR', 'RES_DIR',
           'get_secret', 'string_to_int',
           'main_link', 'overview_link']

BASE_DIR = Path(__file__).resolve().ancestor(1)
TEST_DIR = Path(BASE_DIR, 'tests')
RES_DIR = Path(TEST_DIR, 'resources')

with open(Path(BASE_DIR, 'secrets.json'), 'r') as f:
    secrets = json.loads(f.read())


def get_secret(setting, secrets=secrets):
    return secrets[setting]


def string_to_int(x):
    return int(x.replace('.', ''))


# Different Links
def main_link(page):
    return 'http://www.syndicates-online.de/{0}'.format(page)


def syndicate_link(syn_number):
    return main_link('php/syndicate.php?rid={0}'.format(syn_number))

login_link = main_link('php/login.php')
overview_link = main_link('php/statusseite.php')
military_link = main_link('php/militaerseite.php')