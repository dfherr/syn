import re

from unipath import Path

from syn_utils import overview_link, RES_DIR, string_to_int


with open(Path(RES_DIR, 'home/home_basic.html')) as f:
    html = f.read()

# Every value
base_regex = r'[&nbsp; ]([0-9\.]+) {0}'
networth_regex = re.compile(base_regex.format('NW'))
land_regex = re.compile(base_regex.format('ha'))
credits_regex = re.compile(base_regex.format('Cr'))
energy_regex = re.compile(base_regex.format('MWh'))
erz_regex = re.compile(base_regex.format('t'))
fp_regex = re.compile(base_regex.format('P'))


def get_owner_stats(html):
    # Find relevant sections of the html
    # -- top bar with resources and performance
    start_index = html.find('TOP LEISTE ###')
    end_index = html.find('TOP LEISTE ## ENDE')

    # Find the match and convert it to ints
    networth = string_to_int(networth_regex.findall(html, start_index, end_index)[0])
    land = string_to_int(land_regex.findall(html, start_index, end_index)[0])
    cr = string_to_int(credits_regex.findall(html, start_index, end_index)[0])
    energy = string_to_int(energy_regex.findall(html, start_index, end_index)[0])
    erz = string_to_int(erz_regex.findall(html, start_index, end_index)[0])
    fp = string_to_int(fp_regex.findall(html, start_index, end_index)[0])

    # Find relevant sections of the html
    # -- available military and available spaces

    return networth, land, cr, energy, erz, fp