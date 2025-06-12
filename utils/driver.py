"""Utilities for analysing driver performance."""

from functools import lru_cache
from typing import Iterable

import altair as alt
import fastf1
import pandas as pd


@lru_cache(maxsize=8)
def lap_time_chart(year: int, races: Iterable[int], driver: str) -> alt.Chart:
    """Return a line chart of lap times for ``driver`` across ``races``.

    Parameters
    ----------
    year:
        Season year.
    races:
        Iterable of round numbers to include in the chart.
    driver:
        Driver identifier (e.g. ``'VER'``).
    """
    laps_list = []
    for rnd in races:
        session = fastf1.get_session(year, rnd, "R")
        session.load()  # type: ignore
        laps = session.laps.pick_driver(driver)
        if laps.empty:
            continue
        subset = laps[["LapNumber", "LapTime"]].copy()
        subset["Race"] = session.event.EventName
        laps_list.append(subset)

    if not laps_list:
        raise ValueError("No laps found for given driver and races")

    all_laps = pd.concat(laps_list, ignore_index=True)
    all_laps["LapTimeSeconds"] = all_laps["LapTime"].dt.total_seconds()

    return (
        alt.Chart(all_laps)
        .mark_line()
        .encode(
            x=alt.X("LapNumber:Q", title="Lap"),
            y=alt.Y("LapTimeSeconds:Q", title="Lap Time (s)"),
            color=alt.Color("Race:N", title="Race"),
        )
    )
