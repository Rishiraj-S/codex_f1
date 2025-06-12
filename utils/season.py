"""Season-level utilities."""

from functools import lru_cache
import fastf1

from .data import get_session


@lru_cache(maxsize=32)
def load_session(year: int, session_code: str):
    """Return the first event session of a season loaded with FastF1.

    Parameters
    ----------
    year:
        The championship year.
    session_code:
        The session identifier such as 'R' for race or 'Q' for qualifying.

    Returns
    -------
    fastf1.core.Session
        The loaded FastF1 session instance.
    """
    schedule = fastf1.get_event_schedule(year, include_testing=False)
    event_name = schedule.iloc[0]["EventName"]
    f1_session = get_session(year, event_name, session_code)
    f1_session.load()  # type: ignore
    return f1_session
