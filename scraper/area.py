import re

from scraper.utils import string_to_int

__all__ = ['scrape_area', 'scrape_buildings']

area_cost_regex = re.compile(r'Kosten pro Hektar:\s+</td>\s+.+\s+.+\s+([0-9\.]+)')
area_construction_regex = re.compile(r'Hektar\s+</td>\s+<td align="center">\s+([0-9\.]+)\s+</td>')
building_cost_regex = re.compile(r'Kosten pro Geb.+:\s+</td>\s+.+\s+.+\s+([0-9\.]+)', re.UNICODE)
building_free_regex = re.compile(r'([0-9\.]+)\s+</b> Hektar unbebautes Land')


def scrape_area_cost(html):
    return [
        string_to_int(area_cost_regex.search(html).group(1)),
        string_to_int(area_construction_regex.search(html).group(1))
    ]


def scrape_buildings(html):
    return [
        string_to_int(building_cost_regex.search(html).group(1)),
        string_to_int(building_free_regex.search(html).group(1))
    ]