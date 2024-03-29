import re

from .utils import string_to_int

# TODO: find and return user id instead of username
personal_stats_regex = re.compile(
    (r'tableInner[12]">\s+<td [\w="]+> <a [a-z:=(\',]+'
     '(sl|nof|uic|neb|bf)[\') \w="]+>'  # class
     '<[=:"\w\'/\.\- ]+></a></td>\s+'
     '<[=:"\w ]+>[&nbsp;]+'
     '<[=:"\w&\. \-\?;]+detailsid=([0-9]{1,3})[=:"\w&\. \-\?;]+>'  # id
     '([\w&,\.\-_ ]+)</a>[&nbsp;]+</td>\s+<td[ a-z="]+>\s+'  # name
     '[ \w\.\-/":=><\s_%,]+</td>\s+'
     '<td[ a-z="]+>([0-9\.]+)[&nbsp;]+</td>\s+'  # land
     '<td[ a-z="]+>([0-9\.]+)[&nbsp;]+</td>'),  # networth
    re.UNICODE
)

syn_stats_regex = re.compile(
    r'"absmiddle">[&nbsp;]+<strong>([0-9\.]+)</strong>[&nbsp;]+</td>'
)


def generate_user_rankings(rankings):
    return sorted(rankings, key=lambda x: x[4], reverse=True)


def reformat_personal_stats(stats, syn_number):
    reformat = []
    for person in stats:
        reformat.append([
            person[1],
            repr(person[2].decode('unicode-escape')),
            person[0],
            string_to_int(person[3]),
            string_to_int(person[4]),
            syn_number
        ])
    return reformat


def scrape_syndicate(syn_number, html):
    """
    Scrapes a syndicate to generate a live rating

    personal stats are like
    [('class', 'username', 'land', 'networth', 'syn'), ...]
    syndicate stats are saved in syn_net and syn_land

    implements a check for self consistency:
    the sum of the scraped personal stats has to be equal
    to the scraped syndicate stats
    if not self consistent -> TODO
    """
    # Find relevant sections of the html
    start_index = html.find('Anzeige der Konzerne: START')
    end_index = html.find('Anzeige der Konzerne: ENDE')

    # scraping of personal stats
    personal_stats = personal_stats_regex.findall(html[start_index:end_index])
    personal_stats = reformat_personal_stats(personal_stats, syn_number)

    # scraping and parsing stats of whole syndicate
    syn_land, syn_net = map(
        string_to_int,
        syn_stats_regex.findall(html[end_index:])
    )

    # self consistency check
    check_land = sum(map(lambda x: x[3], personal_stats))
    check_net = sum(map(lambda x: x[4], personal_stats))
    if check_land != syn_land or check_net != syn_net:
        print(syn_number)
        print(personal_stats)
        print('FAIL')
        return []
    return personal_stats
