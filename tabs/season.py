"""Season overview tab displaying team points."""

from __future__ import annotations

import datetime

import streamlit as st

from utils.season import team_points_chart


def render() -> None:
    """Render the season overview with team points chart."""
    st.title("Season Team Points")

    years = list(range(2018, datetime.date.today().year + 1))
    year = st.selectbox("Year", years, index=len(years) - 1)

    fig = team_points_chart(year)
    st.plotly_chart(fig, use_container_width=True)
