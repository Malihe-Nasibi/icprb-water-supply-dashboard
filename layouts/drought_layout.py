"""
Drought Monitor layout module.

This file builds the Drought Monitor tab with the national USDM map and the
Potomac Basin drought map.
"""

from datetime import date

from dash import html

from config import USDM_CURRENT_MAP_URL
from data_fetching.streamflow_usgs import get_daily_cache_key
from figures.drought_figures import build_potomac_usdm_map_src


# Drought Monitor tab layout

def drought_monitor_layout():

    potomac_map_src, potomac_error = build_potomac_usdm_map_src(get_daily_cache_key())

    potomac_map_children = []

    if potomac_map_src is not None:
        potomac_map_children = [
            html.Img(
                id={"type": "outlook-image", "group": "drought", "index": 1},
                n_clicks=0,
                src=potomac_map_src,
                style={
                    "width": "100%",
                    "maxWidth": "1050px",
                    "border": "1px solid lightgray",
                    "cursor": "pointer"
                }
            )
        ]
    else:
        potomac_map_children = [
            html.Div(
                style={
                    "padding": "22px",
                    "border": "1px solid #e1e7ef",
                    "borderRadius": "10px",
                    "backgroundColor": "#fff7f7",
                    "color": "#8a1f1f",
                    "whiteSpace": "pre-wrap",
                    "fontSize": "14px",
                    "textAlign": "left"
                },
                children=potomac_error
            )
        ]

    return html.Div(
        children=[
            html.Div(
                style={
                    "backgroundColor": "white",
                    "padding": "20px",
                    "borderRadius": "12px",
                    "boxShadow": "0px 1px 5px rgba(0,0,0,0.18)",
                    "marginBottom": "22px",
                    "textAlign": "center"
                },
                children=[
                    html.H2(
                        "Current U.S. Drought Monitor",
                        style={
                            "fontSize": "28px",
                            "fontWeight": "bold",
                            "marginTop": "0px"
                        }
                    ),
                    html.P(
                        "National and Potomac Basin drought-condition views based on the current U.S. Drought Monitor product.",
                        style={
                            "fontSize": "16px",
                            "marginBottom": "0px"
                        }
                    )
                ]
            ),

            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(520px, 1fr))",
                    "gap": "22px"
                },
                children=[
                    html.Div(
                        style={
                            "backgroundColor": "white",
                            "padding": "18px",
                            "borderRadius": "14px",
                            "boxShadow": "0px 2px 7px rgba(0,0,0,0.18)",
                            "border": "1px solid #e1e7ef"
                        },
                        children=[
                            html.H3(
                                "National U.S. Drought Monitor Map",
                                style={
                                    "textAlign": "center",
                                    "fontSize": "23px",
                                    "fontWeight": "bold",
                                    "marginTop": "0px",
                                    "marginBottom": "8px"
                                }
                            ),
                            html.Div(
                                style={"textAlign": "center"},
                                children=[
                                    html.Img(
                                        id={"type": "outlook-image", "group": "drought", "index": 0},
                                        n_clicks=0,
                                        src=f"{USDM_CURRENT_MAP_URL}?v={date.today().strftime('%Y%m%d')}",
                                        style={
                                            "width": "100%",
                                            "maxWidth": "1050px",
                                            "border": "1px solid lightgray",
                                            "cursor": "pointer"
                                        }
                                    )
                                ]
                            ),
                            html.P(
                                "Source: U.S. Drought Monitor, National Drought Mitigation Center.",
                                style={
                                    "textAlign": "center",
                                    "fontSize": "14px",
                                    "marginTop": "12px",
                                    "color": "gray"
                                }
                            )
                        ]
                    ),

                    html.Div(
                        style={
                            "backgroundColor": "white",
                            "padding": "18px",
                            "borderRadius": "14px",
                            "boxShadow": "0px 2px 7px rgba(0,0,0,0.18)",
                            "border": "1px solid #e1e7ef"
                        },
                        children=[
                            html.H3(
                                "Potomac Basin U.S. Drought Monitor Map",
                                style={
                                    "textAlign": "center",
                                    "fontSize": "23px",
                                    "fontWeight": "bold",
                                    "marginTop": "0px",
                                    "marginBottom": "8px"
                                }
                            ),
                            html.Div(
                                style={"textAlign": "center"},
                                children=potomac_map_children
                            ),
                            html.P(
                                "Source: U.S. Drought Monitor current GeoJSON with USGS WBD HUC8 basin/subbasin boundaries.",
                                style={
                                    "textAlign": "center",
                                    "fontSize": "14px",
                                    "marginTop": "12px",
                                    "color": "gray"
                                }
                            )
                        ]
                    )
                ]
            )
        ]
    )