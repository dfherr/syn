import re

from .utils import machine_readable_stats

# Every value
base_regex = r'[&nbsp; ]([0-9\.]+) {0}'
networth_regex = re.compile(base_regex.format('NW'))
land_regex = re.compile(base_regex.format('ha'))
credits_regex = re.compile(base_regex.format('Cr'))
energy_regex = re.compile(base_regex.format('MWh'))
erz_regex = re.compile(base_regex.format('t'))
fp_regex = re.compile(base_regex.format('P'))

capacity_base_regex = r'<b class="highlightAuftableInner">([0-9\.]+)</b> {0}'
military_regex = re.compile(capacity_base_regex.format('Milit'))
spies_regex = re.compile(capacity_base_regex.format('Spionage'))
carrier_regex = re.compile(capacity_base_regex.format('Carrier'))


def scrape_owner_stats(html):
    """
    scrapes all all owner stats
    like net worth, ha, resources, capacities

    uses the military page
    """
    owner_stats = {}

    # find relevant sections of the html
    # -- top bar with resources and performance
    start_index = html.find('TOP LEISTE ###')
    end_index = html.find('TOP LEISTE ## ENDE')
    tmp = html[start_index:end_index]

    # find the matches for stats
    owner_stats['nw'] = networth_regex.search(tmp).group(1)
    owner_stats['ha'] = land_regex.search(tmp).group(1)
    owner_stats['credits'] = credits_regex.search(tmp).group(1)
    owner_stats['energy'] = energy_regex.search(tmp).group(1)
    owner_stats['erz'] = erz_regex.search(tmp).group(1)
    owner_stats['fp'] = fp_regex.search(tmp).group(1)

    # find relevant sections of the html
    # -- available military and available spaces
    start_index = html.find('Sie haben noch Kapazit')
    end_index = html.find('<!-- SPIONAGEEINHEITEN -->')
    tmp = html[start_index:end_index]

    # find the matches for capacities
    owner_stats['capas_military'] = military_regex.search(tmp).group(1)
    owner_stats['capas_spies'] = spies_regex.search(tmp).group(1)
    owner_stats['capas_carrier'] = carrier_regex.search(tmp).group(1)

    return machine_readable_stats(owner_stats)