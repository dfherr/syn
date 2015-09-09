from unipath import Path

from syn_utils import RES_DIR, generate_session
from stats.rankings import link_syndicate
from stats.owner_stats import link_home


def update_captcha(session):
    session.img.save(
        Path(RES_DIR, 'captcha/new_captcha.png')
    )


def update_syndicates(session):
    c = session.s.get(link_syndicate(11)).content
    with open(Path(RES_DIR, 'syndicate/new_syndicate.html'), 'w') as f:
        f.write(c)


def update_home(session):
    c = session.s.get(link_home()).content
    with open(Path(RES_DIR, 'home/home_basic.html'), 'w') as f:
        f.write(c)


if __name__ == '__main__':
    session = generate_session()
    # update_captcha(session)
    # update_syndicates(session)
    update_home(session)