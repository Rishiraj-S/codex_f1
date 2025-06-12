"""Season-level utilities."""

from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
import fastf1
import pandas as pd
import plotly.express as px
import streamlit as st

from utils.data import load_session


@lru_cache(maxsize=32)
def load_first_session(year: int, session: str):
    """Return the first event session of a season loaded with FastF1.

    Parameters
    ----------
    year:
        The championship year.
    session:
        The session identifier such as 'R' for race or 'Q' for qualifying.

    Returns
    -------
    fastf1.core.Session
        The loaded FastF1 session instance.
    """
    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
    except Exception:
        st.error("Unable to load event schedule. Check network connection.")
        return None

    event_name = schedule.iloc[0]["EventName"]
    sess = fastf1.get_session(year, event_name, session)
    sess.load()  # type: ignore
    return sess


@lru_cache(maxsize=32)
def team_points_chart(year: int):
    """Return a bar chart of total race points for each team in a season.

    Parameters
    ----------
    year:
        Championship year.

    Returns
    -------
    plotly.graph_objs.Figure
        Bar chart showing aggregated team points for the season.
    """
    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
    except Exception:
        st.error("Unable to load event schedule. Check network connection.")
        return px.bar()

    events = schedule["EventName"].tolist()

    team_points: dict[str, float] = {}

    with ThreadPoolExecutor() as pool:
        sessions = list(pool.map(lambda gp: load_session(year, gp, "R"), events))

    for session in sessions:
        results = session.results
        if results is None:
            continue

        grouped = results.groupby("TeamName")["Points"].sum()
        for team, pts in grouped.items():
            team_points[team] = team_points.get(team, 0.0) + float(pts)

    if not team_points:
        return px.bar()

    df = pd.DataFrame(
        {"Team": list(team_points.keys()), "Points": list(team_points.values())}
    ).sort_values("Points", ascending=False)

    fig = px.bar(df, x="Team", y="Points", title=f"{year} Team Points")
    return fig
