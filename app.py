"""Entry point for the Streamlit F1 dashboard using FastF1."""

import streamlit as st
from tabs import overview, qualifying, race

TABS = {
    "Overview": overview.render,
    "Qualifying": qualifying.render,
    "Race": race.render,
}


def main():
    st.sidebar.title("F1 Dashboard")
    selection = st.sidebar.radio("Go to", list(TABS.keys()))

    if selection == "Overview":
        TABS[selection]()
    else:
        year = st.sidebar.number_input("Season", value=2023)
        grand_prix = st.sidebar.text_input("Grand Prix", value="Bahrain")
        TABS[selection](year, grand_prix)


if __name__ == "__main__":
    main()
