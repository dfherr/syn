#!/usr/bin/env python
from stats.rankings import generate_rankings
from syn_utils import generate_session

if __name__ == '__main__':
    session = generate_session()
    # scrape_own_stats()
    z = generate_rankings(session)
    for x in z:
        print(x)