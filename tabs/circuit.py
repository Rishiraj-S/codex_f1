"""Circuit performance comparison tab."""

from __future__ import annotations

import datetime

import fastf1
import streamlit as st

from utils.circuit import lap_time_boxplot


def render() -> None:
    """Render driver performance distribution for a circuit."""
    st.title("Circuit Lap Time Distribution")

    years = list(range(2018, datetime.date.today().year + 1))
    current_year = years[-1]

    try:
        schedule = fastf1.get_event_schedule(current_year, include_testing=False)
    except Exception:
        st.error("Unable to load event schedule. Check network connection.")
        return

    circuits = schedule["EventName"].tolist()
    circuit = st.selectbox("Circuit", circuits, key="circuit_circuit")

    selected_years = st.multiselect(
        "Years",
        years,
        default=[current_year],
        key="circuit_years",
    )

    if circuit and selected_years:
        fig = lap_time_boxplot(circuit, tuple(selected_years))
        st.plotly_chart(fig, use_container_width=True)
