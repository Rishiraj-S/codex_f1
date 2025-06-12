"""Circuit-specific utilities."""

from __future__ import annotations

from functools import lru_cache
from typing import Iterable

import pandas as pd
import fastf1
import plotly.express as px


@lru_cache(maxsize=32)
def lap_time_boxplot(circuit: str, years: Iterable[int]):
    """Return a boxplot of lap times for all drivers at a circuit.

    Parameters
    ----------
    circuit:
        The event name (grand prix) corresponding to the circuit.
    years:
        Iterable of championship years to include.

    Returns
    -------
    plotly.graph_objs.Figure
        Boxplot visualising lap time distribution for each year.
    """
    all_laps = []
    for year in years:
        try:
            session = fastf1.get_session(year, circuit, "R")
            session.load()  # type: ignore
        except Exception:
            continue

        laps = session.laps[["Driver", "LapTime"]].copy()
        laps["LapTimeSeconds"] = laps["LapTime"].dt.total_seconds()
        laps["Year"] = year
        all_laps.append(laps)

    if not all_laps:
        return px.box()

    df = pd.concat(all_laps, ignore_index=True)
    fig = px.box(
        df,
        x="Year",
        y="LapTimeSeconds",
        points="all",
        color="Driver",
        labels={"LapTimeSeconds": "Lap Time (s)"},
        title=f"Lap Time Distribution at {circuit}",
    )
    return fig
