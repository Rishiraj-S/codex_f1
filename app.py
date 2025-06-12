"""Entry point for the Streamlit F1 dashboard using FastF1."""

import fastf1
import streamlit as st
from pathlib import Path
from tabs import circuit, driver, season, telemetry

# Ensure the cache directory exists, then enable on-disk caching for FastF1.
# This significantly speeds up repeated data access by storing session data
# locally.
Path("cache").mkdir(parents=True, exist_ok=True)
fastf1.Cache.enable_cache("cache")

def main():
    st.set_page_config(
        page_title="F1 Dashboard",
        page_icon="\U0001F3C1",
        layout="wide",
    )

    st.sidebar.image(
        "https://upload.wikimedia.org/wikipedia/commons/3/33/F1.svg",
        width=150,
    )
    st.sidebar.title("F1 Dashboard")

    tab_driver, tab_season, tab_circuit, tab_telemetry = st.tabs([
        "Driver",
        "Season",
        "Circuit",
        "Telemetry",
    ])

    with tab_driver:
        driver.render()

    with tab_season:
        season.render()

    with tab_circuit:
        circuit.render()

    with tab_telemetry:
        telemetry.render()


if __name__ == "__main__":
    main()
