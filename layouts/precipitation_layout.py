"""
Precipitation layout module.

This file builds the Precipitation tab.
"""

from dash import html

from config import PRECIPITATION_IMAGES
from layouts.noaa_layout import image_card


# Precipitation tab layout

def precipitation_layout():
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
                        "Precipitation Forecasts",
                        style={
                            "fontSize": "28px",
                            "fontWeight": "bold",
                            "marginTop": "0px"
                        }
                    ),
                    html.P(
                        "Observed and forecasted precipitation amount products from MARFC and NWS/WPC.",
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
                    "gridTemplateColumns": "repeat(auto-fit, minmax(min(100%, 500px), 1fr))",
                    "gap": "12px",
                    "alignItems": "start",
                    "justifyItems": "center",
                    "width": "100%",
                    "maxWidth": "1300px",
                    "margin": "0 auto"
                },
                children=[
                    image_card(
                        item,
                        "precipitation",
                        index,
                        card_style={
                            "width": "100%",
                            "maxWidth": "644px",
                            "minWidth": "0",
                            "boxSizing": "border-box",
                            "padding": "12px",
                            "marginBottom": "0px"
                        }
                    )
                    for index, item in enumerate(PRECIPITATION_IMAGES)
                ]
            )
        ]
    )