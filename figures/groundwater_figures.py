"""
Groundwater figure module.

This file builds the groundwater Plotly figure using prepared USGS groundwater
data from data_fetching/groundwater.py.
"""

import numpy as np
import pandas as pd
from datetime import date

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import GROUNDWATER_WELLS
from data_fetching.groundwater import load_groundwater_record


# Groundwater calculations and figure

def groundwater_monthly_climatology(df):

    climo = (
        df
        .groupby("Month")["Depth_ft"]
        .agg(
            Mean="mean",
            P10=lambda x: np.percentile(x.dropna(), 10),
            P25=lambda x: np.percentile(x.dropna(), 25),
            P75=lambda x: np.percentile(x.dropna(), 75),
            P90=lambda x: np.percentile(x.dropna(), 90),
            Count="count"
        )
        .reset_index()
    )

    return climo


def add_segmented_groundwater_trace(fig, df, row, col, name, line_color, line_width, showlegend):

    if df.empty:
        return

    df_sorted = df.sort_values("Date").copy()
    df_sorted["Gap"] = df_sorted["Date"].diff().dt.days > 60
    df_sorted["Segment"] = df_sorted["Gap"].cumsum()

    first_segment = True

    for _, segment in df_sorted.groupby("Segment"):
        fig.add_trace(
            go.Scatter(
                x=segment["Date"],
                y=segment["Depth_ft"],
                mode="lines",
                name=name if first_segment and showlegend else None,
                showlegend=first_segment and showlegend,
                line=dict(color=line_color, width=line_width),
                hovertemplate=(
                    "<b>Date:</b> %{x|%b %d, %Y}<br>"
                    "<b>Depth:</b> %{y:.2f} ft below land surface"
                    "<extra></extra>"
                )
            ),
            row=row,
            col=col
        )
        first_segment = False


def build_groundwater_figure(well_name):

    site_no = GROUNDWATER_WELLS[well_name]
    df, source_type = load_groundwater_record(well_name)

    if df.empty:
        raise ValueError(f"No groundwater data available for {well_name}.")

    current_year = date.today().year
    latest = df.loc[df["Date"].idxmax()]
    latest_date = latest["Date"]
    latest_depth = latest["Depth_ft"]

    df_current = df[df["Year"] == current_year].copy()
    cutoff = latest_date - pd.DateOffset(months=12)
    df_last = df[df["Date"] >= cutoff].copy()
    climo = groundwater_monthly_climatology(df)

    if df_last.empty:
        df_last = df.tail(50).copy()

    date_range = pd.date_range(df_last["Date"].min(), df_last["Date"].max(), freq="D")
    band_df = pd.DataFrame({"Date": date_range})
    band_df["Month"] = band_df["Date"].dt.month
    band_df = band_df.merge(
        climo[["Month", "Mean", "P10", "P25", "P75", "P90"]],
        on="Month",
        how="left"
    )

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=False,
        vertical_spacing=0.14,
        row_heights=[0.58, 0.42],
        subplot_titles=("Historical Record", "Last 12 Months with Monthly Climatology")
    )

    add_segmented_groundwater_trace(fig, df, 1, 1, "Historical", "rgba(120,120,120,0.45)", 1, True)
    add_segmented_groundwater_trace(fig, df_current, 1, 1, str(current_year), "black", 3, True)

    fig.add_trace(
        go.Scatter(
            x=[latest_date],
            y=[latest_depth],
            mode="markers",
            name="Latest value",
            marker=dict(size=11, color="red"),
            hovertemplate=(
                "<b>Latest:</b> %{x|%b %d, %Y}<br>"
                "<b>Depth:</b> %{y:.2f} ft below land surface"
                "<extra></extra>"
            )
        ),
        row=1,
        col=1
    )

    fig.add_trace(go.Scatter(x=band_df["Date"], y=band_df["P90"], mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"), row=2, col=1)
    fig.add_trace(go.Scatter(x=band_df["Date"], y=band_df["P10"], mode="lines", line=dict(width=0), fill="tonexty", name="10th-90th percentile", fillcolor="rgba(70, 130, 220, 0.14)", hoverinfo="skip"), row=2, col=1)
    fig.add_trace(go.Scatter(x=band_df["Date"], y=band_df["P75"], mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"), row=2, col=1)
    fig.add_trace(go.Scatter(x=band_df["Date"], y=band_df["P25"], mode="lines", line=dict(width=0), fill="tonexty", name="25th-75th percentile", fillcolor="rgba(70, 130, 220, 0.24)", hoverinfo="skip"), row=2, col=1)
    fig.add_trace(go.Scatter(x=band_df["Date"], y=band_df["Mean"], mode="lines", name="Monthly mean", line=dict(color="#E07B39", width=2, dash="dash"), hovertemplate="<b>Date:</b> %{x|%b %d, %Y}<br><b>Monthly mean:</b> %{y:.2f} ft<extra></extra>"), row=2, col=1)

    add_segmented_groundwater_trace(fig, df_last, 2, 1, "Observed", "black", 3, True)

    fig.add_trace(
        go.Scatter(
            x=[latest_date],
            y=[latest_depth],
            mode="markers",
            name="Latest value",
            marker=dict(size=11, color="red"),
            showlegend=False,
            hovertemplate=(
                "<b>Latest:</b> %{x|%b %d, %Y}<br>"
                "<b>Depth:</b> %{y:.2f} ft below land surface"
                "<extra></extra>"
            )
        ),
        row=2,
        col=1
    )

    fig.update_yaxes(
        autorange="reversed",
        title_text="Depth to water<br>(ft below land surface)",
        tickfont=dict(size=14, color="black"),
        row=1,
        col=1
    )
    fig.update_yaxes(
        autorange="reversed",
        title_text="Depth to water<br>(ft below land surface)",
        tickfont=dict(size=14, color="black"),
        row=2,
        col=1
    )
    fig.update_xaxes(tickfont=dict(size=14, color="black"), showgrid=True, row=1, col=1)
    fig.update_xaxes(tickfont=dict(size=14, color="black"), showgrid=True, row=2, col=1)

    record_start = df["Date"].min().strftime("%Y-%m-%d")
    record_end = df["Date"].max().strftime("%Y-%m-%d")

    fig.update_layout(
        title=dict(
            text=(
                f"Groundwater Level — {well_name} — USGS {site_no}"
                f"<br><sup>Parameter 72019: depth to water level, feet below land surface. "
                f"Source: {source_type}; record: {record_start} to {record_end}</sup>"
            ),
            x=0.5,
            xanchor="center",
            font=dict(size=24, color="black")
        ),
        template="plotly_white",
        height=850,
        hovermode="x unified",
        legend=dict(
            x=0.98,
            y=0.98,
            xanchor="right",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="lightgray",
            borderwidth=1,
            font=dict(size=14, color="black")
        ),
        margin=dict(l=95, r=45, t=145, b=75)
    )

    return fig


def make_groundwater_error_figure(error_message):
    fig = go.Figure()
    fig.update_layout(
        title="Groundwater plot could not be loaded",
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