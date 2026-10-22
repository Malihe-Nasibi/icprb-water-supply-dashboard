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
                className="streamflow-controls",
                style={
                    "display": "flex",
                    "justifyContent": "center",
                    "gap": "clamp(6px, 1vw, 12px)",
                    "marginBottom": "12px",
                    "flexWrap": "nowrap"
                },
                children=[
                    html.Div(
                        style={
                            "flex": "360 1 0",
                            "minWidth": "0",
                            "maxWidth": "360px",
                            "padding": "clamp(6px, 1vw, 10px)",
                            "boxSizing": "border-box",
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
                                value=list(STATIONS.keys())[0],
                                clearable=False,
                                style={"width": "100%", "minWidth": "0"}
                            )
                        ]
                    ),
                    html.Div(
                        style={
                            "flex": "250 1 0",
                            "minWidth": "0",
                            "maxWidth": "250px",
                            "padding": "clamp(6px, 1vw, 10px)",
                            "boxSizing": "border-box",
                            "backgroundColor": "white",
                            "borderRadius": "10px",
                            "boxShadow": "0px 1px 4px rgba(0,0,0,0.15)"
                        },
                        children=[
                            html.Label("Select year:", style=DROPDOWN_TITLE_STYLE),
                            dcc.Dropdown(
                                className=DROPDOWN_CLASS_NAME,
                                id="year-dropdown",
                                clearable=False,
                                style={"width": "100%", "minWidth": "0"}
                            )
                        ]
                    ),
                    html.Div(
                        style={
                            "flex": "300 1 0",
                            "minWidth": "0",
                            "maxWidth": "300px",
                            "padding": "clamp(6px, 1vw, 10px)",
                            "boxSizing": "border-box",
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
                                clearable=False,
                                style={"width": "100%", "minWidth": "0"}
                            )
                        ]
                    )
                ]
            ),

            # Enlarge the interactive streamflow graph
            html.Div(
                style={
                    "textAlign": "right",
                    "marginBottom": "6px"
                },
                children=[
                    html.Button(
                        "Enlarge ↗",
                        id={
                            "type": "enlarge-content",
                            "group": "graph",
                            "index": "streamflow-graph"
                        },
                        n_clicks=0,
                        style={
                            "fontSize": "15px",
                            "fontWeight": "bold",
                            "color": "#1f4e79",
                            "backgroundColor": "white",
                            "border": "1px solid #c7d4e3",
                            "borderRadius": "6px",
                            "padding": "6px 10px",
                            "cursor": "pointer"
                        }
                    )
                ]
            ),

            dcc.Graph(
                id="streamflow-graph",
                config={"displaylogo": False}
            ),

            html.P(
                children=[
                    "Data source: ",
                    html.A(
                        "U.S. Geological Survey (USGS) Water Data for the Nation",
                        href="https://waterdata.usgs.gov/",
                        target="_blank",
                        style={
                            "color": "#124A9F",
                            "textDecoration": "none",
                            "fontWeight": "bold"
                        }
                    )
                ],
                style={
                    "fontSize": "14px",
                    "color": "gray",
                    "textAlign": "center",
                    "marginTop": "6px",
                    "marginBottom": "0px"
                }
            )
        ]
    )