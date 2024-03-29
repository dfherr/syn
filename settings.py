import json
from unipath import Path


__all__ = ['BASE_DIR', 'TEST_DIR', 'RES_DIR', 'current_db_file',
           'session_file', 'syns_amount', 'get_secret']

BASE_DIR = Path(__file__).resolve().ancestor(1)
TEST_DIR = Path(BASE_DIR, 'tests')
RES_DIR = Path(TEST_DIR, 'resources')

current_db_file = Path(BASE_DIR, 'Database.sql')
session_file = Path(BASE_DIR, 'last_session.pkl')

syns_amount = 22

with open(Path(BASE_DIR, 'secrets.json'), 'r') as f:
    secrets = json.loads(f.read())


def get_secret(setting, secrets=secrets):
    return secrets[setting]
