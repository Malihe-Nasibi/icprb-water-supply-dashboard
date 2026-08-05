"""
Forecast figure module.

This file builds the MARFC forecast image URL and the NOAA/NWPS Plotly
forecast graph.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from config import FLOW_FORECAST_STATIONS, FLOOD_STAGE_LEVELS
from data_fetching.forecast_nwps import (
    get_nwps_stageflow_dataframe,
    get_nwps_forecast_issue_text
)


# MARFC forecast image URL

def build_marfc_image_url(selected_station_id, selected_model):
    return (
        "https://www.weather.gov/images/erh/mmefs/"
        f"{selected_station_id}.{selected_model}.SSTG.expvalue.png"
    )


# NOAA/NWPS official forecast figure

def build_nwps_forecast_figure(selected_station_id):
    """
    Builds a custom Plotly version of the NOAA/NWPS official forecast graph.

    The figure keeps the main trace on stage (ft) and adds a right-side flow
    axis from the same NWPS stageflow data.
    """

    station = FLOW_FORECAST_STATIONS[selected_station_id]
    gauge_id = station["nwps_gauge_id"]

    try:
        df = get_nwps_stageflow_dataframe(gauge_id)

        df_obs = df[df["Series"] == "Observed"].copy().sort_values("Time")
        df_fcst = df[df["Series"] == "Forecast"].copy().sort_values("Time")

        if df_obs.empty and df_fcst.empty:
            raise ValueError("No observed or forecast records could be plotted.")

        if not df_obs.empty:
            forecast_start = df_obs["Time"].max()
        elif not df_fcst.empty:
            forecast_start = df_fcst["Time"].min()
        else:
            forecast_start = df["Time"].max()

        x_min_data = df["Time"].min()
        x_max_data = df["Time"].max()

        x_1d = [forecast_start - pd.Timedelta(hours=12), forecast_start + pd.Timedelta(hours=12)]
        x_2d = [forecast_start - pd.Timedelta(days=1), forecast_start + pd.Timedelta(days=1)]
        x_7d = [forecast_start - pd.Timedelta(days=3.5), forecast_start + pd.Timedelta(days=3.5)]
        x_14d = [forecast_start - pd.Timedelta(days=7), forecast_start + pd.Timedelta(days=7)]
        x_all = [x_min_data, max(x_max_data, forecast_start + pd.Timedelta(days=7))]

        stage_min = 0
        stage_max = max(10, float(np.nanmax(df["Stage_ft"])) + 1.0)
        stage_max = np.ceil(stage_max)

        flood_levels = FLOOD_STAGE_LEVELS.get(gauge_id, {})
        visible_flood_levels = flood_levels.copy()

        if visible_flood_levels:
            stage_max = max(stage_max, max(visible_flood_levels.values()) + 0.5)
            stage_max = np.ceil(stage_max)

        flow_values = df["Flow_kcfs"].dropna()
        if not flow_values.empty:
            flow_max = max(5, float(flow_values.max()) * 1.15)
            flow_max = np.ceil(flow_max)
        else:
            flow_max = 5

        fig = go.Figure()

        def make_hover(series_label):
            return (
                f"<b>{series_label}</b><br>"
                "<b>Site time:</b> %{x|%b %d, %Y %I:%M %p}<br>"
                "<b>Stage:</b> %{y:.2f} ft<br>"
                "<b>Flow:</b> %{customdata[0]:.2f} kcfs"
                "<extra></extra>"
            )

        if not df_obs.empty:
            fig.add_trace(
                go.Scatter(
                    x=df_obs["Time"],
                    y=df_obs["Stage_ft"],
                    customdata=np.stack([df_obs["Flow_kcfs"].fillna(np.nan)], axis=-1),
                    mode="lines+markers",
                    name="Observed",
                    showlegend=False,
                    line=dict(color="#2459A6", width=3.2),
                    marker=dict(size=4.2, color="#2459A6"),
                    hovertemplate=make_hover("Observed")
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=df_obs["Time"],
                    y=df_obs["Flow_kcfs"],
                    mode="lines",
                    yaxis="y2",
                    showlegend=False,
                    hoverinfo="skip",
                    line=dict(color="rgba(0,0,0,0)", width=0)
                )
            )

        if not df_fcst.empty:
            fig.add_trace(
                go.Scatter(
                    x=df_fcst["Time"],
                    y=df_fcst["Stage_ft"],
                    customdata=np.stack([df_fcst["Flow_kcfs"].fillna(np.nan)], axis=-1),
                    mode="lines+markers",
                    name="Official forecast",
                    showlegend=False,
                    line=dict(color="#6F3FB2", width=3.2),
                    marker=dict(size=6.2, color="#6F3FB2", symbol="square"),
                    hovertemplate=make_hover("Official forecast")
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=df_fcst["Time"],
                    y=df_fcst["Flow_kcfs"],
                    mode="lines",
                    yaxis="y2",
                    showlegend=False,
                    hoverinfo="skip",
                    line=dict(color="rgba(0,0,0,0)", width=0)
                )
            )

        # Forecast-start divider
        fig.add_trace(
            go.Scatter(
                x=[forecast_start, forecast_start],
                y=[stage_min, stage_max],
                mode="lines",
                name="Forecast start",
                showlegend=False,
                hoverinfo="skip",
                line=dict(color="#1685D9", width=2.5, dash="dash")
            )
        )

        flood_shapes = []
        flood_annotations = []

        flood_band_colors = {
            "Below Action": "rgba(230, 230, 230, 0.45)",
            "Action": "rgba(255, 255, 210, 0.58)",
            "Minor": "rgba(255, 242, 218, 0.66)",
            "Moderate": "rgba(255, 220, 220, 0.58)",
            "Major": "rgba(242, 214, 255, 0.62)"
        }

        sorted_flood_levels = sorted(visible_flood_levels.items(), key=lambda item: item[1])
        flood_level_dict = dict(sorted_flood_levels)

        if sorted_flood_levels:
            action_stage = flood_level_dict.get("Action", sorted_flood_levels[0][1])

            if action_stage > stage_min:
                flood_shapes.append(
                    dict(
                        type="rect",
                        xref="x",
                        yref="y",
                        x0=x_all[0].strftime("%Y-%m-%d %H:%M:%S"),
                        x1=forecast_start.strftime("%Y-%m-%d %H:%M:%S"),
                        y0=stage_min,
                        y1=action_stage,
                        fillcolor=flood_band_colors["Below Action"],
                        line=dict(width=0),
                        layer="below"
                    )
                )

            for i, (label, level) in enumerate(sorted_flood_levels):
                if i < len(sorted_flood_levels) - 1:
                    next_level = sorted_flood_levels[i + 1][1]
                else:
                    next_level = stage_max

                if next_level > level:
                    flood_shapes.append(
                        dict(
                            type="rect",
                            xref="paper",
                            yref="y",
                            x0=0,
                            x1=1,
                            y0=level,
                            y1=next_level,
                            fillcolor=flood_band_colors.get(label, "rgba(255, 245, 200, 0.30)"),
                            line=dict(width=0),
                            layer="below"
                        )
                    )

            for label, level in sorted_flood_levels:
                flood_shapes.append(
                    dict(
                        type="line",
                        xref="paper",
                        yref="y",
                        x0=0,
                        x1=1,
                        y0=level,
                        y1=level,
                        line=dict(color="black", width=1.2),
                        layer="above"
                    )
                )

                flood_annotations.append(
                    dict(
                        xref="paper",
                        yref="y",
                        x=0.008,
                        y=level,
                        text=f"{label}: {level:g} ft",
                        showarrow=False,
                        font=dict(size=13, color="black"),
                        xanchor="left",
                        yanchor="bottom",
                        bgcolor="rgba(255,255,255,0.55)"
                    )
                )

        latest_obs_text = ""
        if not df_obs.empty:
            latest_obs = df_obs.loc[df_obs["Time"].idxmax()]
            latest_obs_text = (
                f"Latest observed: {latest_obs['Stage_ft']:.2f} ft "
                f"at {latest_obs['Time'].strftime('%b %d, %Y %I:%M %p')} EDT"
            )

        issued_text = get_nwps_forecast_issue_text(gauge_id)
        if issued_text:
            subtitle = f"NWSLI: {gauge_id}. {latest_obs_text}. Forecast information: {issued_text}"
        else:
            subtitle = f"NWSLI: {gauge_id}. {latest_obs_text}. Site time shown in EDT."

        def rng(pair):
            return [
                pair[0].strftime("%Y-%m-%d %H:%M:%S"),
                pair[1].strftime("%Y-%m-%d %H:%M:%S")
            ]

        def relayout_for_range(pair):
            return {"xaxis.range": rng(pair)}

        fig.update_layout(
            title=dict(
                text=(
                    f"NOAA/NWPS Official Forecast — {station['label']}"
                    f"<br><sup>{subtitle}</sup>"
                ),
                x=0.5,
                xanchor="center",
                font=dict(size=24, color="#10233F")
            ),
            template="plotly_white",
            height=760,
            hovermode="closest",
            showlegend=False,
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis=dict(
                title=dict(text="Site Time (EDT)", font=dict(size=17, color="#334155")),
                tickfont=dict(size=14, color="black"),
                showgrid=True,
                gridcolor="rgba(0,0,0,0.10)",
                tickformat="%I %p<br>%b %d",
                range=rng(x_14d)
            ),
            yaxis=dict(
                title=dict(text="Stage (FT)", font=dict(size=18, color="black")),
                tickfont=dict(size=14, color="black"),
                showgrid=True,
                gridcolor="rgba(0,0,0,0.12)",
                range=[stage_min, stage_max],
                zeroline=False
            ),
            yaxis2=dict(
                title=dict(text="Flow (KCFS)", font=dict(size=18, color="black")),
                tickfont=dict(size=14, color="black"),
                overlaying="y",
                side="right",
                showgrid=False,
                range=[0, flow_max],
                zeroline=False
            ),
            updatemenus=[
                dict(
                    type="buttons",
                    direction="right",
                    x=0,
                    y=-0.20,
                    xanchor="left",
                    yanchor="top",
                    bgcolor="rgba(255,255,255,0.95)",
                    bordercolor="rgba(210,210,210,0.85)",
                    borderwidth=1,
                    pad={"r": 4, "t": 4, "b": 4, "l": 4},
                    buttons=[
                        dict(label="1d", method="relayout", args=[relayout_for_range(x_1d)]),
                        dict(label="2d", method="relayout", args=[relayout_for_range(x_2d)]),
                        dict(label="7d", method="relayout", args=[relayout_for_range(x_7d)]),
                        dict(label="14d", method="relayout", args=[relayout_for_range(x_14d)]),
                        dict(label="All", method="relayout", args=[relayout_for_range(x_all)]),
                    ]
                )
            ],
            shapes=flood_shapes,
            annotations=flood_annotations,
            margin=dict(l=85, r=90, t=130, b=130)
        )

        return fig

    except Exception as e:
        fig = go.Figure()
        fig.update_layout(
            title="NOAA/NWPS official forecast could not be loaded",
            template="plotly_white",
            height=560
        )
        fig.add_annotation(
            text=(f"Gauge: {gauge_id}<br>Error: {str(e)}"),
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="red"),
            align="center"
        )
        return fig