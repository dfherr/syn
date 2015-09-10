import re

from unipath import Path

from login.login import main_link
from syn_utils import string_to_int, RES_DIR


def link_home():
    return main_link('php/statusseite.php')

html = ''
with open(Path(RES_DIR, 'home/home_basic.html')) as f:
    html = f.read()

# Find relevant sections of the html
start_index = html.find('TOP LEISTE ###')
end_index = html.find('TOP LEISTE ## ENDE')

# Every value
base_regex = r'[&nbsp; ]([0-9\.]+) {0}'
networth_regex = re.compile(base_regex.format('NW'))
land_regex = re.compile(base_regex.format('ha'))
credits_regex = re.compile(base_regex.format('Cr'))
energy_regex = re.compile(base_regex.format('MWh'))
erz_regex = re.compile(base_regex.format('t'))
fp_regex = re.compile(base_regex.format('P'))

# Find the match and convert it to ints
networth = string_to_int(networth_regex.findall(html, start_index, end_index)[0])
land = string_to_int(land_regex.findall(html, start_index, end_index)[0])

print(networth, land)