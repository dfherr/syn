import re

from unipath import Path

from settings import RES_DIR


with open(Path(RES_DIR, 'home/home_military.html')) as f:
    html = f.read()

base_resource_regex = r'<td>{0}</td>\s+<td align=right>([0-9\.]+)&nbsp;'
energy_regex = re.compile(base_resource_regex.format('Energie'))
erz_regex = re.compile(base_resource_regex.format('Erz'))
fp_regex = re.compile(base_resource_regex.format('Forschungspunkte'))
credits_regex = re.compile(base_resource_regex.format('Credits'))


def scrape_store(html):
    """
    scrapes all all store stats
    resource volumes / exchange rates
    """
    store = {}

    # find relevant sections of the html
    # -- syndicate resources / exchange rates
    start_index = html.find('Ihr Syndikat besitzt momentan folgende Ressourcen')
    end_index = html.find('Lagerzugriffe der letzten 24 Stunden')
    tmp = html[start_index:end_index]

    # find the matches for the resources / exchange rates
    store['credits'] = credits_regex.search(tmp).group(1)
    # owner_stats['nw'] = networth_regex.search(tmp).group(1)



    return store

if __name__ == '__main__':
    print(scrape_store(html))