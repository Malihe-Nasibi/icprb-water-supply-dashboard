"""
Groundwater layout module.

This file builds the Groundwater tab title, well-location map, and graph
container.
"""

from dash import dcc, html


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
                    "backgroundColor": "white",
                    "padding": "10px",
                    "borderRadius": "14px",
                    "boxShadow": "0px 2px 7px rgba(0,0,0,0.18)",
                    "marginBottom": "24px",
                    "border": "1px solid #e1e7ef"
                },
                children=[
                    dcc.Graph(
                        id="groundwater-well-map",
                        config={"displayModeBar": True}
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