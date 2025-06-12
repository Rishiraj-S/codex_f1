"""Pit stop analysis utilities."""

from __future__ import annotations

from functools import lru_cache

import pandas as pd
import fastf1
import plotly.express as px


@lru_cache(maxsize=32)
def stint_chart(year: int, grand_prix: str):
    """Return a horizontal bar chart of tyre stints for each driver.

    The chart visualises the start and end lap of every compound stint for
    each driver in the race.

    Parameters
    ----------
    year:
        Championship year.
    grand_prix:
        Event name (grand prix).

    Returns
    -------
    plotly.graph_objs.Figure
        Timeline chart showing lap ranges coloured by tyre compound.
    """
    session = fastf1.get_session(year, grand_prix, "R")
    session.load()  # type: ignore

    laps = session.laps
    cols = ["Driver", "Stint", "Compound", "LapNumber"]
    stints = laps[cols].dropna(subset=["Stint", "Compound"])

    if stints.empty:
        return px.timeline()

    stint_ranges = (
        stints.groupby(["Driver", "Stint", "Compound"])["LapNumber"]
        .agg(StartLap="min", EndLap="max")
        .reset_index()
    )
    # Extend end lap so the bar covers the full final lap
    stint_ranges["EndLap"] += 1

    fig = px.timeline(
        stint_ranges,
        x_start="StartLap",
        x_end="EndLap",
        y="Driver",
        color="Compound",
        title=f"Tyre Stints - {grand_prix} {year}",
    )
    fig.update_yaxes(autorange="reversed", title="Driver")
    fig.update_xaxes(title="Lap")
    return fig
