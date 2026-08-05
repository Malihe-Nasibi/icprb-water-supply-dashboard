"""
Reservoir figure module.

This file builds reservoir summary cards and the reservoir storage Plotly
figure using prepared reservoir data from data_fetching/reservoir.py.
"""

import numpy as np
import plotly.graph_objects as go
from dash import html

from config import RESERVOIR_STORAGE_COLUMNS
from data_fetching.reservoir import load_reservoir_storage, get_available_reservoir_columns


# Reservoir summary cards

def reservoir_latest_cards(df):
    cards = []

    for column, label in RESERVOIR_STORAGE_COLUMNS.items():
        if column not in df.columns:
            latest_text = "Missing"
            date_text = "Column not found"
        else:
            valid = df[["Date", column]].dropna().copy()

            if valid.empty:
                latest_text = "No data"
                date_text = ""
            else:
                latest_row = valid.iloc[-1]
                latest_text = f"{latest_row[column]:.2f} BG"
                date_text = latest_row["Date"].strftime("%b %d, %Y")

        cards.append(
            html.Div(
                style={
                    "backgroundColor": "white",
                    "borderRadius": "12px",
                    "boxShadow": "0px 1px 5px rgba(0,0,0,0.15)",
                    "padding": "14px",
                    "border": "1px solid #e1e7ef",
                    "minHeight": "105px"
                },
                children=[
                    html.Div(
                        label,
                        style={
                            "fontWeight": "bold",
                            "fontSize": "19px",
                            "color": "#1f2d3d",
                            "marginBottom": "8px"
                        }
                    ),
                    html.Div(
                        latest_text,
                        style={
                            "fontSize": "24px",
                            "fontWeight": "bold",
                            "color": "#0f3b63"
                        }
                    ),
                    html.Div(
                        date_text,
                        style={
                            "fontSize": "17px",
                            "fontWeight": "bold",
                            "color": "gray",
                            "marginTop": "4px"
                        }
                    )
                ]
            )
        )

    return html.Div(
        style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fit, minmax(230px, 1fr))",
            "gap": "14px",
            "marginBottom": "22px"
        },
        children=cards
    )


# Reservoir storage figure

def build_reservoir_storage_figure(selected_column):
    df = load_reservoir_storage()
    available_columns = get_available_reservoir_columns(df)

    if not available_columns:
        raise ValueError("No reservoir storage columns are available for plotting.")

    if selected_column not in available_columns:
        selected_column = available_columns[0]

    label = RESERVOIR_STORAGE_COLUMNS[selected_column]
    y = df[selected_column]

    valid = df[["Date", selected_column]].dropna().copy()

    if valid.empty:
        raise ValueError(f"No valid storage values are available for {label}.")

    latest = valid.iloc[-1]
    latest_date = latest["Date"]
    latest_value = latest[selected_column]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["Date"],
            y=y,
            mode="lines+markers",
            name=label,
            line=dict(width=3, color="#1f5f99"),
            marker=dict(size=5, color="#1f5f99"),
            connectgaps=False,
            hovertemplate=(
                "<b>Date:</b> %{x|%b %d, %Y}<br>"
                "<b>Storage:</b> %{y:.2f} BG"
                "<extra></extra>"
            )
        )
    )

    fig.add_trace(
        go.Scatter(
            x=[latest_date],
            y=[latest_value],
            mode="markers",
            name=f"Latest value ({latest_value:.2f} BG)",
            marker=dict(size=12, color="red"),
            hovertemplate=(
                "<b>Latest:</b> %{x|%b %d, %Y}<br>"
                "<b>Storage:</b> %{y:.2f} BG"
                "<extra></extra>"
            )
        )
    )

    y_max = np.nanmax(y)
    y_range_max = max(1, y_max * 1.12)

    fig.update_layout(
        title=dict(
            text=(
                f"Reservoir Storage — {label}"
                f"<br><sup>Latest value: {latest_value:.2f} BG on "
                f"{latest_date.strftime('%b %d, %Y')}</sup>"
            ),
            x=0.5,
            xanchor="center",
            font=dict(size=24, color="black")
        ),
        template="plotly_white",
        hovermode="x unified",
        height=680,
        xaxis=dict(
            title=dict(text="Date", font=dict(size=18, color="black")),
            tickfont=dict(size=14, color="black"),
            showgrid=True,
            rangeslider=dict(visible=False)
        ),
        yaxis=dict(
            title=dict(text="Usable storage (billion gallons)", font=dict(size=18, color="black")),
            tickfont=dict(size=14, color="black"),
            showgrid=True,
            range=[0, y_range_max]
        ),
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
        margin=dict(l=85, r=45, t=125, b=85)
    )

    return fig


# Reservoir error figure

def make_reservoir_error_figure(error_message):
    fig = go.Figure()
    fig.update_layout(
        title="Reservoir storage plot could not be loaded",
        template="plotly_white",
        height=540
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