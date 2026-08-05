"""
Streamflow layout module.

This file builds the Streamflow tab controls and graph container.
"""

from dash import dcc, html

from config import STATIONS
from styles import DROPDOWN_TITLE_STYLE, DROPDOWN_CLASS_NAME


# Streamflow tab layout

def streamflow_layout():
    return html.Div(
        children=[
            html.Div(
                style={
                    "display": "flex",
                    "justifyContent": "center",
                    "gap": "20px",
                    "marginBottom": "20px",
                    "flexWrap": "wrap"
                },
                children=[
                    html.Div(
                        style={
                            "width": "360px",
                            "padding": "12px",
                            "backgroundColor": "white",
                            "borderRadius": "10px",
                            "boxShadow": "0px 1px 4px rgba(0,0,0,0.15)"
                        },
                        children=[
                            html.Label("Select station:", style=DROPDOWN_TITLE_STYLE),
                            dcc.Dropdown(
                                className=DROPDOWN_CLASS_NAME,
                                id="station-dropdown",
                                options=[
                                    {
                                        "label": f"{site_id} — {station_name}",
                                        "value": site_id
                                    }
                                    for site_id, station_name in STATIONS.items()
                                ],
                                value="01646502",
                                clearable=False
                            )
                        ]
                    ),
                    html.Div(
                        style={
                            "width": "250px",
                            "padding": "12px",
                            "backgroundColor": "white",
                            "borderRadius": "10px",
                            "boxShadow": "0px 1px 4px rgba(0,0,0,0.15)"
                        },
                        children=[
                            html.Label("Select year:", style=DROPDOWN_TITLE_STYLE),
                            dcc.Dropdown(
                                className=DROPDOWN_CLASS_NAME,
                                id="year-dropdown",
                                clearable=False
                            )
                        ]
                    ),
                    html.Div(
                        style={
                            "width": "300px",
                            "padding": "12px",
                            "backgroundColor": "white",
                            "borderRadius": "10px",
                            "boxShadow": "0px 1px 4px rgba(0,0,0,0.15)"
                        },
                        children=[
                            html.Label("Select flow type:", style=DROPDOWN_TITLE_STYLE),
                            dcc.Dropdown(
                                className=DROPDOWN_CLASS_NAME,
                                id="flow-type-dropdown",
                                options=[
                                    {"label": "Daily flow", "value": "daily"},
                                    {"label": "7-day average flow", "value": "7day"}
                                ],
                                value="daily",
                                clearable=False
                            )
                        ]
                    )
                ]
            ),
            dcc.Graph(id="streamflow-graph")
        ]
    )