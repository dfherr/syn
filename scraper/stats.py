import re

from .utils import string_to_int

spy_regex = re.compile(
    r'erlittene Spionageaktionen</b></td>\s+<td>([0-9]+)</font>'
)


def scrape_spies(html):
    """
    scrapes the amount of spys against the owner
    """
    return string_to_int(spy_regex.search(html).group(1))