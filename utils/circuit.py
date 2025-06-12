"""Circuit-specific utilities."""

from __future__ import annotations

from functools import lru_cache
from typing import Iterable
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import plotly.express as px
import fastf1
import requests
import logging

from utils.data import load_session

logger = logging.getLogger(__name__)


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

    def _load(y: int):
        try:
            return load_session(y, circuit, "R")
        except (fastf1.FastF1Error, requests.RequestException) as err:
            logger.warning("Failed to load session %s %s: %s", circuit, y, err)
            return None

    with ThreadPoolExecutor() as pool:
        sessions = list(pool.map(_load, years))

    for year, session in zip(years, sessions):
        if session is None:
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
