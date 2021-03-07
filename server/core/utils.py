"""
Utils
"""
from server.core.settings import DEFAULT_LIMIT


def skip_row(page: int = None, total: int = 0):
    skip = 0
    if page and total > DEFAULT_LIMIT * page:
        skip = DEFAULT_LIMIT * page
    return skip
