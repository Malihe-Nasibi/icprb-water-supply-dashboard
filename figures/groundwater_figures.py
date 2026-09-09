"""
Groundwater figure module.

This file builds the groundwater Plotly figure using prepared USGS groundwater
data from data_fetching/groundwater.py. It also builds the groundwater well map.
"""

import json
import os
from datetime import date

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import GROUNDWATER_WELLS, POTOMAC_BASIN_GEOJSON_FILE
from data_fetching.groundwater import load_groundwater_record, load_groundwater_well_metadata


# Potomac Basin boundary helper

def load_potomac_basin_boundary_coordinates():
    """
    Read the Potomac Basin GeoJSON boundary and return coordinate rings.

    Each ring is a list of [longitude, latitude] coordinate pairs.
    """

    if not os.path.exists(POTOMAC_BASIN_GEOJSON_FILE):
        return []

    with open(POTOMAC_BASIN_GEOJSON_FILE, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    boundary_rings = []

    for feature in geojson_data.get("features", []):
        geometry = feature.get("geometry", {})
        geometry_type = geometry.get("type")
        coordinates = geometry.get("coordinates", [])

        if geometry_type == "Polygon":
            for ring in coordinates:
                boundary_rings.append(ring)

        elif geometry_type == "MultiPolygon":
            for polygon in coordinates:
                for ring in polygon:
                    boundary_rings.append(ring)

    return boundary_rings


def add_potomac_basin_boundary_to_map(fig):
    """
    Add the Potomac Basin boundary outline to the groundwater map.

    The GeoJSON may contain multiple rings/polygon parts. Only the first
    boundary trace is shown in the legend so the legend label does not repeat.
    """

    boundary_rings = load_potomac_basin_boundary_coordinates()
    first_ring = True

    for ring in boundary_rings:
        if not ring:
            continue

        lons = [point[0] for point in ring]
        lats = [point[1] for point in ring]

        fig.add_trace(
            go.Scattermapbox(
                lon=lons,
                lat=lats,
                mode="lines",
                name="Potomac Basin Boundary",
                line=dict(
                    width=3,
                    color="#124A9F"
                ),
                hoverinfo="skip",
                showlegend=first_ring
            )
        )

        first_ring = False

    return fig


# Groundwater condition helpers

def groundwater_condition_color(percentile):
    """
    Return marker color based on groundwater depth-to-water percentile.

    For depth-to-water, larger depth means lower/drier groundwater conditions.
    Therefore, low depth percentiles are better/wetter and high depth percentiles
    are worse/drier.
    """

    if percentile is None or pd.isna(percentile):
        return "lightgray"

    if percentile <= 25:
        return "#5BA061"   
    elif percentile <= 50:
        return "#E6B800"   
    elif percentile <= 75:
        return "#E07B39"   
    else:
        return "#C00000"


def groundwater_condition_label(percentile):
    """
    Return condition label based on groundwater depth-to-water percentile.
    """

    if percentile is None or pd.isna(percentile):
        return "Not available"

    if percentile <= 25:
        return "High groundwater / wetter than normal"
    elif percentile <= 50:
        return "Near normal"
    elif percentile <= 75:
        return "Below normal / dry"
    else:
        return "Low groundwater / much drier than normal"


def calculate_current_groundwater_percentile(well_name):
    """
    Calculate the latest groundwater depth percentile for one well.

    The latest depth is compared against historical values from the same month.
    This avoids comparing, for example, August groundwater levels with winter
    groundwater levels.
    """

    try:
        df, source_type = load_groundwater_record(well_name)

        if df.empty:
            return None, None, None, None

        df = df.dropna(subset=["Date", "Depth_ft"]).copy()

        if df.empty:
            return None, None, None, None

        latest = df.loc[df["Date"].idxmax()]
        latest_date = latest["Date"]
        latest_depth = latest["Depth_ft"]
        latest_month = latest_date.month

        same_month_values = df.loc[
            df["Date"].dt.month == latest_month,
            "Depth_ft"
        ].dropna()

        if same_month_values.empty:
            return latest_date, latest_depth, None, source_type

        percentile = (
            (same_month_values <= latest_depth).sum()
            / len(same_month_values)
            * 100.0
        )

        return latest_date, latest_depth, percentile, source_type

    except Exception as e:
        print(f"Groundwater percentile calculation error for {well_name}: {e}")
        return None, None, None, None


def add_groundwater_conditions_to_metadata(metadata):
    """
    Add latest groundwater depth, percentile, condition, and color to the
    groundwater well metadata table.
    """

    metadata = metadata.copy()

    latest_dates = []
    latest_depths = []
    percentiles = []
    conditions = []
    colors = []

    for well_name in metadata["Well_Name"]:
        latest_date, latest_depth, percentile, source_type = calculate_current_groundwater_percentile(well_name)

        latest_dates.append(latest_date)
        latest_depths.append(latest_depth)
        percentiles.append(percentile)
        conditions.append(groundwater_condition_label(percentile))
        colors.append(groundwater_condition_color(percentile))

    metadata["Latest_Date"] = latest_dates
    metadata["Latest_Depth_ft"] = latest_depths
    metadata["Current_Percentile"] = percentiles
    metadata["Condition"] = conditions
    metadata["Marker_Color"] = colors

    return metadata


# Groundwater well map

def build_groundwater_well_map(selected_well=None):
    """
    Build a clickable groundwater well-location map.

    Wells are colored by current groundwater depth-to-water percentile.
    Because larger depth means lower/drier groundwater conditions, the color
    interpretation is reversed:
        <= 25th percentile   = green
        25th-50th percentile = yellow
        50th-75th percentile = orange
        > 75th percentile    = red

    The selected well is shown as a larger marker.
    """

    metadata = load_groundwater_well_metadata()

    if selected_well is None or selected_well not in metadata["Well_Name"].values:
        selected_well = "VA51S7"

    metadata = add_groundwater_conditions_to_metadata(metadata)

    fig = go.Figure()

    # Add Potomac Basin boundary first so groundwater wells are plotted on top.
    fig = add_potomac_basin_boundary_to_map(fig)

    # Add groundwater wells by condition group.
    condition_groups = [
        {
            "name": "≤ 25th percentile",
            "color": "#5BA061",
            "filter": metadata["Current_Percentile"] <= 25
        },
        {
            "name": "25th–50th percentile",
            "color": "#E6B800",
            "filter": (metadata["Current_Percentile"] > 25) & (metadata["Current_Percentile"] <= 50)
        },
        {
            "name": "50th–75th percentile",
            "color": "#E07B39",
            "filter": (metadata["Current_Percentile"] > 50) & (metadata["Current_Percentile"] <= 75)
        },
        {
            "name": "> 75th percentile",
            "color": "#C00000",
            "filter": metadata["Current_Percentile"] > 75
        },
        {
            "name": "No current condition",
            "color": "lightgray",
            "filter": metadata["Current_Percentile"].isna()
        }
    ]

    for group in condition_groups:
        df_group = metadata[group["filter"]].copy()

        if df_group.empty:
            continue

        fig.add_trace(
            go.Scattermapbox(
                lon=df_group["Longitude"],
                lat=df_group["Latitude"],
                mode="markers",
                name=group["name"],
                text=df_group["Well_Name"],
                customdata=np.stack(
                    (
                        df_group["Well_Name"],
                        df_group["Site_ID"],
                        df_group["Latitude"],
                        df_group["Longitude"]
                    ),
                    axis=-1
                ),
                marker=dict(
                    size=15,
                    color=group["color"],
                    opacity=0.9
                ),
                hoverlabel=dict(
                    font_size=16,
                    font_family="Arial",
                    bgcolor="white"
                ),
                hovertemplate=(
                    "<b>Well:</b> %{customdata[0]}<br>"
                    "<b>Site ID:</b> %{customdata[1]}<br>"
                    "<b>Latitude:</b> %{customdata[2]:.4f}<br>"
                    "<b>Longitude:</b> %{customdata[3]:.4f}"
                    "<extra></extra>"
                )
            )
        )

    # Add selected well again on top as a larger marker.
    selected_metadata = metadata[metadata["Well_Name"] == selected_well].copy()

    if not selected_metadata.empty:
        fig.add_trace(
            go.Scattermapbox(
                lon=selected_metadata["Longitude"],
                lat=selected_metadata["Latitude"],
                mode="markers",
                name="Selected well",
                text=selected_metadata["Well_Name"],
                customdata=np.stack(
                    (
                        selected_metadata["Well_Name"],
                        selected_metadata["Site_ID"],
                        selected_metadata["Latitude"],
                        selected_metadata["Longitude"]
                    ),
                    axis=-1
                ),
                marker=dict(
                    size=24,
                    color=selected_metadata["Marker_Color"].iloc[0],
                    opacity=1.0
                ),
                showlegend=False,
                hoverlabel=dict(
                    font_size=16,
                    font_family="Arial",
                    bgcolor="white"
                ),
                hovertemplate=(
                    "<b>Well:</b> %{customdata[0]}<br>"
                    "<b>Site ID:</b> %{customdata[1]}<br>"
                    "<b>Latitude:</b> %{customdata[2]:.4f}<br>"
                    "<b>Longitude:</b> %{customdata[3]:.4f}"
                    "<extra></extra>"
                )
            )
        )

    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center=dict(
                lat=39.0,
                lon=-78.1
            ),
            zoom=6.5
        ),
        template="plotly_white",
        height=600,
        showlegend=True,
        legend=dict(
            x=0.01,
            y=0.99,
            xanchor="left",
            yanchor="top",
            bgcolor="rgba(255,255,255,0.88)",
            bordercolor="lightgray",
            borderwidth=1,
            font=dict(size=12, color="black")
        ),
        margin=dict(l=10, r=10, t=10, b=10)
    )

    return fig


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

    fig.add_trace(
        go.Scatter(
            x=band_df["Date"],
            y=band_df["P90"],
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip"
        ),
        row=2,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=band_df["Date"],
            y=band_df["P10"],
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            name="10th-90th percentile",
            fillcolor="rgba(70, 130, 220, 0.14)",
            hoverinfo="skip"
        ),
        row=2,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=band_df["Date"],
            y=band_df["P75"],
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip"
        ),
        row=2,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=band_df["Date"],
            y=band_df["P25"],
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            name="25th-75th percentile",
            fillcolor="rgba(70, 130, 220, 0.24)",
            hoverinfo="skip"
        ),
        row=2,
        col=1
    )

    fig.add_trace(
        go.Scatter(
            x=band_df["Date"],
            y=band_df["Mean"],
            mode="lines",
            name="Monthly mean",
            line=dict(color="#E07B39", width=2, dash="dash"),
            hovertemplate=(
                "<b>Date:</b> %{x|%b %d, %Y}<br>"
                "<b>Monthly mean:</b> %{y:.2f} ft"
                "<extra></extra>"
            )
        ),
        row=2,
        col=1
    )

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

    fig.update_xaxes(
        tickfont=dict(size=14, color="black"),
        showgrid=True,
        row=1,
        col=1
    )

    fig.update_xaxes(
        tickfont=dict(size=14, color="black"),
        showgrid=True,
        row=2,
        col=1
    )

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