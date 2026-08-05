"""
Streamflow figure module.

This file prepares streamflow percentile statistics and builds the Plotly
streamflow figure.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go

from config import STATIONS
from data_fetching.streamflow_usgs import load_station_record


# Prepare streamflow percentile data

def prepare_percentile_data(site_id, selected_year, flow_type):

    selected_year = int(selected_year)

    station_name = STATIONS[site_id]
    df_all = load_station_record(site_id)

    if flow_type == "7day":
        flow_col = "Flow_7Day_cfs"
        flow_label = "7-Day Average Flow"
    else:
        flow_col = "Flow_cfs"
        flow_label = "Daily Flow"

    df_selected = df_all[df_all["Year"] == selected_year].copy()
    df_selected = df_selected.dropna(subset=[flow_col]).copy()
    df_selected = df_selected.sort_values("Plot_Date")

    if df_selected.empty:
        raise ValueError(
            f"No {flow_label.lower()} data are available for station {site_id} in {selected_year}."
        )

    selected_start = df_selected["Date"].min().strftime("%b %d, %Y")
    selected_end = df_selected["Date"].max().strftime("%b %d, %Y")

    df_hist = df_all.copy()
    df_hist = df_hist.dropna(subset=[flow_col]).copy()

    if df_hist.empty:
        raise ValueError(
            f"No historical {flow_label.lower()} data are available for station {site_id}."
        )

    hist_start_date = df_hist["Date"].min()
    hist_end_date = df_hist["Date"].max()

    hist_start_year = int(hist_start_date.year)
    hist_end_year = int(hist_end_date.year)

    df_stats = (
        df_hist
        .groupby("Month_Day")[flow_col]
        .agg(
            Min="min",
            P5=lambda x: np.percentile(x, 5),
            P10=lambda x: np.percentile(x, 10),
            P25=lambda x: np.percentile(x, 25),
            Median="median",
            P75=lambda x: np.percentile(x, 75),
            P90=lambda x: np.percentile(x, 90),
            P95=lambda x: np.percentile(x, 95),
            Max="max"
        )
        .reset_index()
    )

    # 2001 is only a dummy non-leap plotting year used to place Month-Day
    # values on a Jan-Dec x-axis. It does not mean the data are from 2001.
    df_stats["Plot_Date"] = pd.to_datetime("2001-" + df_stats["Month_Day"])
    df_stats = df_stats.sort_values("Plot_Date")

    q10_threshold = np.percentile(df_hist[flow_col], 10)

    print("--------------------------------------")
    print(f"USGS station: {site_id} - {station_name}")
    print(f"Selected black-line year: {selected_year}")
    print(f"Selected flow type: {flow_label}")
    print(f"Selected-year period: {selected_start} to {selected_end}")
    print(f"Percentile period: {hist_start_date.date()} to {hist_end_date.date()}")
    print(f"Q10 threshold: {q10_threshold:.2f} cfs")
    print(f"Number of black-line records: {len(df_selected)}")
    print("--------------------------------------")

    return (
        df_stats,
        df_selected,
        q10_threshold,
        selected_year,
        hist_start_year,
        hist_end_year,
        station_name,
        flow_col,
        flow_label
    )


# Build streamflow figure

def build_streamflow_figure(site_id, selected_year, flow_type):

    (
        df_stats,
        df_selected,
        q10_threshold,
        selected_year,
        hist_start_year,
        hist_end_year,
        station_name,
        flow_col,
        flow_label
    ) = prepare_percentile_data(site_id, selected_year, flow_type)

    black_line_label = f"{selected_year} {flow_label}"

    fig = go.Figure()

    percentile_bands = [
        {
            "name": "0–5 Percentile",
            "lower": "Min",
            "upper": "P5",
            "color": "rgba(111, 111, 111, 0.95)"
        },
        {
            "name": "5–10 Percentile",
            "lower": "P5",
            "upper": "P10",
            "color": "rgba(168, 159, 143, 0.95)"
        },
        {
            "name": "10–25 Percentile",
            "lower": "P10",
            "upper": "P25",
            "color": "rgba(215, 200, 168, 0.95)"
        },
        {
            "name": "25–75 Percentile",
            "lower": "P25",
            "upper": "P75",
            "color": "rgba(238, 245, 223, 0.95)"
        },
        {
            "name": "75–90 Percentile",
            "lower": "P75",
            "upper": "P90",
            "color": "rgba(199, 221, 235, 0.95)"
        },
        {
            "name": "90–95 Percentile",
            "lower": "P90",
            "upper": "P95",
            "color": "rgba(143, 177, 207, 0.95)"
        },
        {
            "name": "95–100 Percentile",
            "lower": "P95",
            "upper": "Max",
            "color": "rgba(79, 121, 167, 0.95)"
        }
    ]

    # USGS-style percentile bands
    for band in percentile_bands:
        fig.add_trace(
            go.Scatter(
                x=df_stats["Plot_Date"],
                y=df_stats[band["upper"]],
                mode="lines",
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip"
            )
        )

        fig.add_trace(
            go.Scatter(
                x=df_stats["Plot_Date"],
                y=df_stats[band["lower"]],
                mode="lines",
                line=dict(width=0),
                fill="tonexty",
                name=band["name"],
                fillcolor=band["color"],
                hoverinfo="skip"
            )
        )

    # Historical median
    fig.add_trace(
        go.Scatter(
            x=df_stats["Plot_Date"],
            y=df_stats["Median"],
            mode="lines",
            name="Median",
            line=dict(width=1.5, color="gray")
        )
    )

    # Selected year, shown in bold black
    fig.add_trace(
        go.Scatter(
            x=df_selected["Plot_Date"],
            y=df_selected[flow_col],
            mode="lines",
            name=black_line_label,
            line=dict(width=3.5, color="black"),
            hovertemplate=(
                "<b>Date:</b> %{x|%b %d}<br>"
                "<b>Flow:</b> %{y:,.0f} cfs"
                "<extra></extra>"
            )
        )
    )

    # Low-flow threshold: Q10
    fig.add_trace(
        go.Scatter(
            x=[
                df_stats["Plot_Date"].min(),
                df_stats["Plot_Date"].max()
            ],
            y=[
                q10_threshold,
                q10_threshold
            ],
            mode="lines",
            name=f"Low-flow threshold (Q10 = {q10_threshold:,.0f} cfs)",
            line=dict(color="gray", width=2, dash="dash"),
            hovertemplate=(
                "<b>Low-flow threshold (Q10):</b> %{y:,.0f} cfs"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        title=dict(
            text=(
                f"{flow_label}, {station_name} — USGS {site_id}"
                f"<br><sup>Historical percentiles based on full available record: "
                f"{hist_start_year}–{hist_end_year}</sup>"
            ),
            x=0.5,
            xanchor="center",
            font=dict(size=24, color="black")
        ),

        template="plotly_white",
        hovermode="x unified",
        height=730,

        yaxis=dict(
            type="log",
            title=dict(
                text="cfs (log scale)",
                font=dict(size=20, color="black")
            ),
            tickmode="array",
            tickvals=[10, 100, 1000, 10000, 100000, 1000000],
            ticktext=["10¹", "10²", "10³", "10⁴", "10⁵", "10⁶"],
            tickfont=dict(size=18, color="black"),
            showgrid=True
        ),

        xaxis=dict(
            title=dict(text="", font=dict(size=20, color="black")),
            tickformat="%b",
            dtick="M1",
            tickfont=dict(size=18, color="black"),
            showgrid=True
        ),

        legend=dict(
            x=0.5,
            y=-0.18,
            xanchor="center",
            yanchor="top",
            orientation="h",
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="lightgray",
            borderwidth=1,
            font=dict(size=14, color="black")
        ),

        margin=dict(l=95, r=45, t=145, b=150)
    )

    return fig


# Error figure helper
# Build a simple error figure if the streamflow plot fails

def make_error_figure(error_message):
    fig = go.Figure()
    fig.update_layout(
        title="Streamflow plot could not be loaded",
        template="plotly_white",
        height=550
    )
    fig.add_annotation(
        text=f"Error: {error_message}",
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=16, color="red"),
        align="center"
    )
    return fig