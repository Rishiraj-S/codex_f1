"""Driver-specific utilities."""

from __future__ import annotations

from typing import Iterable, Any
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import datetime

import requests

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


_FALLBACK_DRIVERS: dict[str, dict[str, str]] = {
    "VER": {
        "name": "Max Verstappen",
        "image": "https://upload.wikimedia.org/wikipedia/commons/3/3d/Max_Verstappen_2017_Malaysia_2.jpg",
        "dob": "1997-09-30",
        "nationality": "Dutch",
        "team": "Red Bull Racing",
    },
    "HAM": {
        "name": "Lewis Hamilton",
        "image": "https://upload.wikimedia.org/wikipedia/commons/2/27/Lewis_Hamilton_2016_Malaysia_podium_1.jpg",
        "dob": "1985-01-07",
        "nationality": "British",
        "team": "Mercedes",
    },
    "ALO": {
        "name": "Fernando Alonso",
        "image": "https://upload.wikimedia.org/wikipedia/commons/6/62/Fernando_Alonso_2016_Malaysia_podium_1.jpg",
        "dob": "1981-07-29",
        "nationality": "Spanish",
        "team": "Aston Martin",
    },
    "LEC": {
        "name": "Charles Leclerc",
        "image": "https://upload.wikimedia.org/wikipedia/commons/9/9e/F1_2019_Monaco_GP_Sunday_QP_%2847019031094%29_%28cropped%29.jpg",
        "dob": "1997-10-16",
        "nationality": "Monegasque",
        "team": "Ferrari",
    },
}


@lru_cache(maxsize=32)
def driver_metadata(year: int, driver: str) -> dict[str, Any]:
    """Return basic metadata for a driver in a given season.

    The function attempts to gather data using FastF1 and external services.
    If that fails (for example in an offline environment) a small internal
    dictionary is used as a fallback.

    Parameters
    ----------
    year:
        Championship year.
    driver:
        Driver abbreviation such as ``'VER'`` or ``'HAM'``.

    Returns
    -------
    dict[str, Any]
        Dictionary containing ``name``, ``image``, ``age``, ``nationality`` and
        ``team`` keys. Values may be ``None`` if unavailable.
    """

    name = None
    team = None

    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
        if not schedule.empty:
            first_event = schedule.iloc[0]["EventName"]
            session = load_session(year, first_event, "R")
            results = session.results
            if results is not None:
                row = results[results["Abbreviation"] == driver]
                if not row.empty:
                    name = row.iloc[0].get("FullName") or row.iloc[0].get("Driver")
                    team = row.iloc[0].get("TeamName")
    except Exception:
        pass

    nationality = None
    dob: datetime.date | None = None
    image = None

    try:
        resp = requests.get(
            f"https://ergast.com/api/f1/drivers/{driver}.json?limit=1",
            timeout=5,
        )
        if resp.ok:
            data = resp.json()
            drv = data["MRData"]["DriverTable"]["Drivers"][0]
            nationality = drv.get("nationality")
            dob_str = drv.get("dateOfBirth")
            if dob_str:
                dob = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()
            if name is None:
                given = drv.get("givenName", "")
                family = drv.get("familyName", "")
                name = (given + " " + family).strip()
    except Exception:
        pass

    if name and image is None:
        wiki_name = name.replace(" ", "_")
        try:
            resp = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{wiki_name}",
                timeout=5,
            )
            if resp.ok:
                data = resp.json()
                image = data.get("thumbnail", {}).get("source")
        except Exception:
            pass

    if dob is not None:
        age = (datetime.date(year, 12, 31) - dob).days // 365
    else:
        age = None

    # Apply fallback data for missing fields
    fallback = _FALLBACK_DRIVERS.get(driver.upper())
    if fallback:
        if name is None:
            name = fallback["name"]
        if image is None:
            image = fallback["image"]
        if nationality is None:
            nationality = fallback["nationality"]
        if team is None:
            team = fallback["team"]
        if age is None and fallback.get("dob"):
            dob = datetime.datetime.strptime(fallback["dob"], "%Y-%m-%d").date()
            age = (datetime.date(year, 12, 31) - dob).days // 365

    return {
        "name": name,
        "image": image,
        "age": age,
        "nationality": nationality,
        "team": team,
    }

