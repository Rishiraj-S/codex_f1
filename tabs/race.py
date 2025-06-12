"""Race results and analysis."""

import streamlit as st
from utils.data import get_session


def render(year: int, grand_prix: str):
    session = get_session(year, grand_prix, "R")
    session.load()  # type: ignore
    st.title(f"Race - {grand_prix} {year}")
    st.write("Race data will be visualized here.")
