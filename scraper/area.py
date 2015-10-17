import re

from scraper.utils import machine_readable_stats, string_to_int

__all__ = ['scrape_area']

area_cost_regex = re.compile(r'Kosten pro Hektar:\s+</td>\s+.+\s+.+\s+([0-9\.]+)')


def scrape_area_cost(html):
    return string_to_int(area_cost_regex.search(html).group(1))