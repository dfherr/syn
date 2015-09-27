def check_success(html):
    """
    If action successful always:
    ...
    is displayed.
    """
    raise NotImplementedError


def string_to_int(x):
    """
    transform the scraped string in a machine readable format
    """
    return int(x.replace('.', ''))


def machine_readable_stats(d):
    """ applies string_to_int to a whole dict """
    for key in d.keys():
        d[key] = string_to_int(d[key])
    return d