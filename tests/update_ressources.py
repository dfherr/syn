from unipath import Path

from login.login import LoggedInSession
from syn_utils import overview_link, RES_DIR
from stats.rankings import syndicate_link


def update_captcha(session):
    session.img.save(
        Path(RES_DIR, 'captcha/new_captcha.png')
    )


def update_syndicates(session):
    c = session.s.get(syndicate_link(11)).content
    with open(Path(RES_DIR, 'syndicate/new_syndicate.html'), 'w') as f:
        f.write(c)


def update_home(session):
    c = session.s.get(overview_link).content
    with open(Path(RES_DIR, 'home/home_basic.html'), 'w') as f:
        f.write(c)


if __name__ == '__main__':
    with LoggedInSession.get_session() as session:
        # update_captcha(session)
        # update_syndicates(session)
        update_home(session)