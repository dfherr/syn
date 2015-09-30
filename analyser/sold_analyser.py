import re

import pandas as pd

from api import links
from api import LoggedInSession
from scraper.utils import string_to_int

# TODO: NOT WORKING PROPERLY, FIX REGEX(?) BEFORE USAGE!

# Examples:
# <i>132 Behemoth</i> von ihnen gekauft. Sie haben dadurch <b>888.492 Cr</b> eingenommen
# <i>2.010</i> <i>Behemoth</i> von ihnen gekauft.<br>Sie haben dadurch <b>13.692.120 Cr</b>

sales_regex = re.compile(
    r'<i>([0-9\.]+)</i> <i>([a-zA-Z]+)</i>[ a-zA-Z\.<>/]+([0-9\.]+)'
)
tender_regex = re.compile(
    r'<i>([0-9\.]+) ([a-zA-Z]+)</i>[ a-zA-Z\.<>/]+([0-9\.]+)'
)

params = {
    'action': 'ajax',
    '1': 'false',
    '2': 'false',
    '3': 'false',
    '4': 'false',
    '5': 'true',  # Einheitenmarkt
    '6': 'false',
    '7': 'false',
    '8': 'false',
    '9': 'false',
    '10': 'false',
}

if __name__ == '__main__':
    session = LoggedInSession.get_session()
    r = session.get(links['news'], params=params)

    sales = map(
        list,
        sales_regex.findall(r.content)  # + tender_regex.findall(r.content)
    )
    for sale in sales:
        sale[0] = string_to_int(sale[0])
        sale[2] = string_to_int(sale[2])
    df = pd.DataFrame(sales)
    grouped = df.groupby(1).sum()

    print(grouped)

    pd.set_option('display.max_rows', 1000)

    with open('test_log', 'w') as f:
        f.write(r.content)
        f.write('\n\n\n\n')
        f.write(str(df))
        f.write(str(grouped))

    session.save_session()