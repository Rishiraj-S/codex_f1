"""Driver-specific utilities."""

from __future__ import annotations

from typing import Iterable

import pandas as pd
import fastf1
import plotly.express as px


def lap_time_chart(year: int, driver: str, races: Iterable[str]):
    """Return a line chart of lap times for a driver over selected races.

    Parameters
    ----------
    year:
        Championship year.
    driver:
        Driver identifier such as ``'VER'`` for Max Verstappen.
    races:
        Iterable of race (grand prix) names in that season.

    Returns
    -------
    plotly.graph_objs.Figure
        Line chart with lap times for the driver coloured by race.
    """
    all_laps = []
    for gp in races:
        session = fastf1.get_session(year, gp, "R")
        session.load()  # type: ignore

        laps = session.laps.pick_driver(driver)[["LapNumber", "LapTime"]].copy()
        laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()
        laps["Race"] = gp
        all_laps.append(laps)

    if not all_laps:
        return px.line()

    df = pd.concat(all_laps, ignore_index=True)
    fig = px.line(
        df,
        x="LapNumber",
        y="LapTimeSeconds",
        color="Race",
        labels={"LapNumber": "Lap", "LapTimeSeconds": "Lap Time (s)"},
        title=f"{driver} Lap Times",
    )
    return fig
