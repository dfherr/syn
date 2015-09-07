import re

from login.login import main_link

# TODO: umlaute
match_personal_stats = re.compile(
    (r'tableInner[12]">\s+<td [a-z="]+> <a [a-z:=(\',]+'
     '(sl|nof|uic|neb|bf)[\') a-zA-Z="]+>'  # class
     '<[=:"a-zA-Z0-9\'/\.\- ]+></a></td>\s+'
     '<[=:"a-zA-Z0-9& ]+>[&nbsp;]+'
     '<[=:"a-zA-Z0-9&\. \?]+>'
     '([a-zA-Z\w&\.\-_ ]+)</a>[&nbsp;]+</td>\s+<td[ a-z="]+>\s+'  # name
     '[ a-zA-Z0-9_\.\-/":=><\s]+</td>\s+'
     '<td[ a-z="]+>([0-9\.]+)[&nbsp;]+</td>\s+'  # land
     '<td[ a-z="]+>([0-9\.]+)[&nbsp;]+</td>')  # networth
)

match_syn_stats = re.compile(
    r'"absmiddle">[&nbsp;]+<strong>([0-9\.]+)</strong>[&nbsp;]+</td>'
)

def link_syndicate(syn_number):
    return main_link('php/syndicate.php?rid={0}'.format(syn_number))


def iterate_syndicates(session):
    for i in range(1, 2):
        c = session.s.get(link_syndicate(i)).content
        scrape_syndicate(i, c)


def scrape_syndicate(i, html):
    # SCRAPE RANKINGS
    # Integrity Check! vs Sum -> ErrorLog
    start_index = html.find('Anzeige der Konzerne: START')
    end_index = html.find('Anzeige der Konzerne: ENDE')
    html = html[start_index:end_index]
    print(i, match_personal_stats.findall(html))
    print(match_syn_stats.findall(html))