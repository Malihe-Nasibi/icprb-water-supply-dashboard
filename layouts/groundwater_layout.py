"""
Groundwater layout module.

This file builds the Groundwater tab title, well dropdown, and graph container.
"""

from dash import dcc, html

from config import GROUNDWATER_WELLS
from styles import DROPDOWN_TITLE_STYLE, DROPDOWN_CLASS_NAME


# Groundwater tab layout

def groundwater_layout():
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
                        "Groundwater Conditions",
                        style={
                            "fontSize": "28px",
                            "fontWeight": "bold",
                            "marginTop": "0px"
                        }
                    ),
                    html.P(
                        "USGS groundwater depth-to-water observations with historical context and monthly percentile bands.",
                        style={
                            "fontSize": "16px",
                            "marginBottom": "0px"
                        }
                    )
                ]
            ),
            html.Div(
                style={
                    "width": "430px",
                    "padding": "14px",
                    "backgroundColor": "white",
                    "borderRadius": "12px",
                    "boxShadow": "0px 1px 5px rgba(0,0,0,0.18)",
                    "marginBottom": "22px"
                },
                children=[
                    html.Label("Select groundwater well:", style=DROPDOWN_TITLE_STYLE),
                    dcc.Dropdown(
                        className=DROPDOWN_CLASS_NAME,
                        id="groundwater-well-dropdown",
                        options=[
                            {
                                "label": f"{well_name} — USGS {site_no}",
                                "value": well_name
                            }
                            for well_name, site_no in GROUNDWATER_WELLS.items()
                        ],
                        value="VA51S7",
                        clearable=False,
                        style={"marginTop": "8px"}
                    )
                ]
            ),
            html.Div(
                style={
                    "backgroundColor": "white",
                    "padding": "18px",
                    "borderRadius": "14px",
                    "boxShadow": "0px 2px 7px rgba(0,0,0,0.18)",
                    "marginBottom": "24px",
                    "border": "1px solid #e1e7ef"
                },
                children=[
                    dcc.Graph(id="groundwater-graph")
                ]
            )
        ]
    )