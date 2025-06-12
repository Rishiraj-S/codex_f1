"""Driver-specific utilities."""

from __future__ import annotations

from typing import Iterable
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import fastf1
import plotly.express as px

from utils.data import load_session


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
    with ThreadPoolExecutor() as pool:
        sessions = list(
            pool.map(lambda gp: load_session(year, gp, "R"), races)
        )

    for gp, session in zip(races, sessions):
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


def race_summary(year: int, grand_prix: str, driver: str) -> str:
    """Return a Markdown summary of a driver's race performance.

    The summary highlights lap pace, pit strategy and how the driver's
    position changed from start to finish.

    Parameters
    ----------
    year:
        Championship year.
    grand_prix:
        Event name of the race.
    driver:
        Driver abbreviation such as ``'ALO'`` or ``'VER'``.

    Returns
    -------
    str
        A single paragraph in Markdown describing the race.
    """

    session = load_session(year, grand_prix, "R")

    laps = session.laps.pick_driver(driver)
    if laps.empty:
        return ""

    results = session.results
    start_pos = None
    finish_pos = None
    if results is not None:
        row = results[results["Abbreviation"] == driver]
        if not row.empty:
            start_pos = int(row.iloc[0].get("GridPosition", 0))
            finish_pos = int(row.iloc[0].get("Position", 0))

    fastest = laps["LapTime"].min()
    average = laps["LapTime"].mean()
    pit_stops = laps["PitOutTime"].notna().sum()

    if start_pos is not None and finish_pos is not None:
        pos_change = start_pos - finish_pos
        if pos_change > 0:
            pos_desc = (
                f"gaining {pos_change} position{'s' if pos_change != 1 else ''}"
            )
        elif pos_change < 0:
            pos_desc = (
                f"losing {abs(pos_change)} position{'s' if pos_change != -1 else ''}"
            )
        else:
            pos_desc = "finishing where they started"
    else:
        pos_desc = ""

    fastest_s = pd.to_timedelta(fastest).total_seconds()
    average_s = pd.to_timedelta(average).total_seconds()

    summary = (
        f"{driver} started {start_pos} on the grid and finished {finish_pos}, {pos_desc}. "
        f"Across {len(laps)} laps the driver averaged {average_s:.2f}s per lap with a "
        f"fastest time of {fastest_s:.2f}s. {driver} made {pit_stops} pit stop"
        f"{'s' if pit_stops != 1 else ''} during the race."
    )

    return summary
