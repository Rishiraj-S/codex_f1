"""Driver telemetry comparison tab."""

from __future__ import annotations

import datetime

import fastf1
import streamlit as st

from utils.telemetry import compare_fastest_lap_telemetry


def _get_drivers(year: int, event: str) -> list[str]:
    """Return a list of driver abbreviations for a given race."""
    session = fastf1.get_session(year, event, "R")
    session.load()  # type: ignore
    return session.results["Abbreviation"].dropna().sort_values().unique().tolist()


def render() -> None:
    """Render the telemetry comparison tab."""
    st.title("Telemetry Comparison")

    years = list(range(2018, datetime.date.today().year + 1))
    year = st.selectbox(
        "Year",
        years,
        index=len(years) - 1,
        key="telemetry_year",
    )

    schedule = fastf1.get_event_schedule(year, include_testing=False)
    races = schedule["EventName"].tolist()
    race = st.selectbox("Race", races, key="telemetry_race")

    drivers = _get_drivers(year, race) if race else []
    driver1 = st.selectbox("Driver 1", drivers, key="telemetry_driver1")
    driver2 = st.selectbox(
        "Driver 2",
        drivers,
        index=1 if len(drivers) > 1 else 0,
        key="telemetry_driver2",
    )

    if drivers:
        speed_fig, throttle_fig, brake_fig = compare_fastest_lap_telemetry(
            year, race, "R", driver1, driver2
        )
        st.plotly_chart(speed_fig, use_container_width=True)
        st.plotly_chart(throttle_fig, use_container_width=True)
        st.plotly_chart(brake_fig, use_container_width=True)
