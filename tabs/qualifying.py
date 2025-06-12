"""Qualifying results and analysis."""

import streamlit as st
from utils.data import get_session


def render(year: int, grand_prix: str):
    session = get_session(year, grand_prix, "Q")
    session.load()  # type: ignore
    st.title(f"Qualifying - {grand_prix} {year}")
    st.write("Qualifying data will be visualized here.")
