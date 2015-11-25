import re

from scraper.utils import machine_readable_stats

__all__ = ['scrape_market_resources']

base_regex_res = (r'<form name="{0}".+\s+.+\s+.+\s+.+\s+.+\s+.+\s+.+\s+.+\s+'
                  '<td align="center" class="tableInner1">\s+([0-9\.]+)\s+</td>\s+'
                  '<td align=center class="tableInner1">\s+([0-9\.]+)\s+</td>')

energy_regex = re.compile(base_regex_res.format('Energie'))
erz_regex = re.compile(base_regex_res.format('Erz'))
fp_regex = re.compile(base_regex_res.format('Forschungspunkte'))


def scrape_market_resources(html):
    market_stats = {}

    energy = energy_regex.search(html)
    erz = erz_regex.search(html)
    fp = fp_regex.search(html)

    # TODO
    if energy is not None:
        market_stats['energy'] = energy.group(1)
    else:
        market_stats['energy'] = 0

    market_stats['erz'] = erz.group(1)
    market_stats['fp'] = fp.group(1)

    market_stats = machine_readable_stats(market_stats)

    market_stats['ex_energy'] = float(energy.group(2))/10.
    market_stats['ex_erz'] = float(erz.group(2))/10.
    market_stats['ex_fp'] = float(fp.group(2))/10.

    return market_stats

if __name__ == '__main__':
    from settings import RES_DIR
    from unipath import Path

    with open(Path(RES_DIR, 'home/home_market.html'), 'r') as f:
        html = f.read()

    base_regex_units = (r'<form name="{0}".+\s+.+\s+.+\s+.+\s+.+\s+.+\s+.+\s+.+\s+'
                        '<td align="center" class="tableInner1">\s+([0-9\.]+)\s+</td>\s+'
                        '<td align="center" class="tableInner1">\s+([0-9\.]+) \(([0-9\.]+) / ([0-9]+)%\)')

    marine_regex = re.compile(base_regex_units.format('Marine'))
    ranger_regex = re.compile(base_regex_res.format('Ranger'))
