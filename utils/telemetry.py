"""Telemetry comparison utilities."""

from __future__ import annotations

from functools import lru_cache

import fastf1
import plotly.graph_objs as go


@lru_cache(maxsize=32)
def compare_fastest_lap_telemetry(
    year: int,
    grand_prix: str,
    session: str,
    driver1: str,
    driver2: str,
):
    """Return speed, throttle and brake comparisons for two drivers.

    The telemetry from each driver's fastest lap is overlaid on line charts.

    Parameters
    ----------
    year:
        Championship year.
    grand_prix:
        Event name (grand prix).
    session:
        Session identifier such as ``'Q'`` or ``'R'``.
    driver1:
        First driver abbreviation.
    driver2:
        Second driver abbreviation.

    Returns
    -------
    tuple[go.Figure, go.Figure, go.Figure]
        Figures for speed, throttle and brake respectively.
    """
    sess = fastf1.get_session(year, grand_prix, session)
    sess.load()  # type: ignore

    lap1 = sess.laps.pick_driver(driver1).pick_fastest()
    lap2 = sess.laps.pick_driver(driver2).pick_fastest()

    if lap1.empty or lap2.empty:
        return go.Figure(), go.Figure(), go.Figure()

    tel1 = lap1.get_car_data().add_distance()
    tel2 = lap2.get_car_data().add_distance()

    fig_speed = go.Figure()
    fig_speed.add_trace(
        go.Scatter(x=tel1["Distance"], y=tel1["Speed"], name=driver1)
    )
    fig_speed.add_trace(
        go.Scatter(x=tel2["Distance"], y=tel2["Speed"], name=driver2)
    )
    fig_speed.update_layout(
        title="Speed Comparison",
        xaxis_title="Distance (m)",
        yaxis_title="Speed (km/h)",
    )

    fig_throttle = go.Figure()
    fig_throttle.add_trace(
        go.Scatter(x=tel1["Distance"], y=tel1["Throttle"], name=driver1)
    )
    fig_throttle.add_trace(
        go.Scatter(x=tel2["Distance"], y=tel2["Throttle"], name=driver2)
    )
    fig_throttle.update_layout(
        title="Throttle Comparison",
        xaxis_title="Distance (m)",
        yaxis_title="Throttle (%)",
    )

    fig_brake = go.Figure()
    fig_brake.add_trace(
        go.Scatter(x=tel1["Distance"], y=tel1["Brake"], name=driver1)
    )
    fig_brake.add_trace(
        go.Scatter(x=tel2["Distance"], y=tel2["Brake"], name=driver2)
    )
    fig_brake.update_layout(
        title="Brake Comparison",
        xaxis_title="Distance (m)",
        yaxis_title="Brake",
    )

    return fig_speed, fig_throttle, fig_brake
