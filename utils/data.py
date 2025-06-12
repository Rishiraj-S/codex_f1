"""Utility functions for fetching and caching F1 data using FastF1."""

from functools import lru_cache
import fastf1


@lru_cache(maxsize=32)
def get_session(year: int, grand_prix: str, session: str):
    """Return a FastF1 session with caching."""
    return fastf1.get_session(year, grand_prix, session)


@lru_cache(maxsize=32)
def load_session(year: int, grand_prix: str, session: str):
    """Return a loaded FastF1 session with caching."""
    sess = fastf1.get_session(year, grand_prix, session)
    sess.load()
    return sess
