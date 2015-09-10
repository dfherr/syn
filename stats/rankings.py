import re

from login.login import main_link
from syn_utils import string_to_int

personal_stats_regex = re.compile(
    (r'tableInner[12]">\s+<td [\w="]+> <a [a-z:=(\',]+'
     '(sl|nof|uic|neb|bf)[\') \w="]+>'  # class
     '<[=:"\w\'/\.\- ]+></a></td>\s+'
     '<[=:"\w ]+>[&nbsp;]+'
     '<[=:"\w&\. \-\?;]+>'
     '([\w&\.\-_ ]+)</a>[&nbsp;]+</td>\s+<td[ a-z="]+>\s+'  # name
     '[ \w\.\-/":=><\s_%,]+</td>\s+'
     '<td[ a-z="]+>([0-9\.]+)[&nbsp;]+</td>\s+'  # land
     '<td[ a-z="]+>([0-9\.]+)[&nbsp;]+</td>'),  # networth
    re.UNICODE
)

syn_stats_regex = re.compile(
    r'"absmiddle">[&nbsp;]+<strong>([0-9\.]+)</strong>[&nbsp;]+</td>'
)


def link_syndicate(syn_number):
    return main_link('php/syndicate.php?rid={0}'.format(syn_number))


def generate_rankings(session):
    # TODO: find a way to automatically determine
    # the upper bound of the available syndicates
    rankings = []
    for i in range(1, 31):
        c = session.s.get(link_syndicate(i)).content
        rankings += scrape_syndicate(i, c)
    return generate_user_rankings(rankings)


def generate_user_rankings(rankings):
    return sorted(rankings, key=lambda x: x[3], reverse=True)


def reformat_personal_stats(stats, syn_number):
    reformat = []
    for person in stats:
        reformat.append([
            person[0],
            person[1],
            string_to_int(person[2]),
            string_to_int(person[3]),
            syn_number
        ])
    return reformat


def scrape_syndicate(syn_number, html):
    """
    Scrapes a syndicate to generate a live rating

    personal stats are like
    [('class', 'username', 'land', 'networth'), ...]
    syndicate stats are saved in syn_net and syn_land

    implements a check for self consistency:
    the sum of the scraped personal stats has to be equal
    to the scraped syndicate stats
    if not self consistent -> save in error table
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
    check_land = sum(map(lambda x: x[2], personal_stats))
    check_net = sum(map(lambda x: x[3], personal_stats))
    if check_land != syn_land or check_net != syn_net:
        # raise InconsistencyException(
        #     message="Sum of stats of syndicate members "
        #             "doesn't match syndicate stats!"
        # )
        # TODO: handle incorrect rankings
        print('FAIL')
        return []
    return personal_stats