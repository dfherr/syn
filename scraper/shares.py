import re

from .utils import string_to_int

shares_regex = re.compile(r'<td [a-z0-9 "_=:\(\);]+>&nbsp;\[<font id="plus_([0-9]+)">\+</font>.+</td>\s+'
                          '<td [a-z0-9 "_=:\(\);]+>([0-9\.]+)[&nbsp;]+</td>\s+'
                          '<td [a-z0-9 "_=:\(\);]+><em>([0-9,]+) %</em>[&nbsp;]+</td>\s+'
                          '<td [a-z0-9 "_=:\(\);]+>([0-9\.]+)[&nbsp;]+</td>\s+'
                          '<td [a-z0-9 "_=:\(\);]+>([0-9\.]+)[&nbsp;]+</td>')


def scrape_shares(html):
    """
    scrapes all shares stats
    {syn: (owning_abs, owning_percentage, volume, price), ...}
    """
    shares = {}

    for x in shares_regex.findall(html):
        shares[int(x[0])] = [
            string_to_int(x[1]),
            float(x[2].replace(',', '.')),
            string_to_int(x[3]),
            string_to_int(x[4])
        ]

    return shares
