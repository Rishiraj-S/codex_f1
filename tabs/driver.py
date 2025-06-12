"""Driver lap time analysis tab."""

from __future__ import annotations

import datetime

import fastf1
import streamlit as st

from utils.driver import lap_time_chart


def _get_drivers(year: int, event: str) -> list[str]:
    """Return a list of driver abbreviations for a given event."""
    session = fastf1.get_session(year, event, "R")
    session.load()  # type: ignore
    return (
        session.results["Abbreviation"].dropna().sort_values().unique().tolist()
    )


def render() -> None:
    """Render the driver performance tab."""
    st.title("Driver Lap Time Performance")

    years = list(range(2018, datetime.date.today().year + 1))
    year = st.selectbox(
        "Year",
        years,
        index=len(years) - 1,
        key="driver_year",
    )

    try:
        schedule = fastf1.get_event_schedule(year, include_testing=False)
    except Exception:
        st.error("Unable to load event schedule. Check network connection.")
        return

    events = schedule["EventName"].tolist()

    drivers = _get_drivers(year, events[0]) if events else []
    driver = st.selectbox("Driver", drivers, key="driver_driver")

    races = st.multiselect("Races", events, default=events[:1])

    if driver and races:
        fig = lap_time_chart(year, driver, races)
        st.plotly_chart(fig, use_container_width=True)
