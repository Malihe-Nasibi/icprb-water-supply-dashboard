"""
NOAA layout module.

This file builds the NOAA Outlooks tab.
It also defines image_card(), a reusable function that creates one
clickable image box with a title, source text, and image. 
The same image_card() function is also used by the Precipitation tab.
"""

from datetime import date

from dash import html

from config import NOAA_OUTLOOK_IMAGES


# Reusable image card

def image_card(group, index, title, source, url):
    cache_buster = date.today().strftime("%Y%m%d")
    image_url = f"{url}?v={cache_buster}"

    return html.Div(
        style={
            "backgroundColor": "white",
            "padding": "18px",
            "borderRadius": "12px",
            "boxShadow": "0px 1px 5px rgba(0,0,0,0.18)",
            "marginBottom": "22px"
        },
        children=[
            html.H3(
                title,
                style={
                    "textAlign": "center",
                    "fontSize": "23px",
                    "fontWeight": "bold",
                    "marginTop": "0px",
                    "marginBottom": "6px"
                }
            ),
            html.P(
                source,
                style={
                    "textAlign": "center",
                    "fontSize": "14px",
                    "color": "gray",
                    "marginTop": "0px",
                    "marginBottom": "8px"
                }
            ),
            html.Div(
                style={"textAlign": "center"},
                children=[
                    html.Img(
                        id={
                            "type": "outlook-image",
                            "group": group,
                            "index": index
                        },
                        n_clicks=0,
                        src=image_url,
                        style={
                            "width": "95%",
                            "maxWidth": "950px",
                            "border": "1px solid lightgray",
                            "cursor": "pointer"
                        }
                    )
                ]
            )
        ]
    )


# NOAA Outlooks tab layout

def noaa_outlooks_layout():
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
                        "NOAA Climate Outlooks",
                        style={
                            "fontSize": "28px",
                            "fontWeight": "bold",
                            "marginTop": "0px"
                        }
                    ),
                    html.P(
                        "Official 30-day temperature and precipitation probability outlooks from NOAA Climate Prediction Center.",
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
                    "gridTemplateColumns": "repeat(auto-fit, minmax(420px, 1fr))",
                    "gap": "22px"
                },
                children=[
                    image_card(
                        "noaa",
                        index,
                        item["title"],
                        item["source"],
                        item["url"]
                    )
                    for index, item in enumerate(NOAA_OUTLOOK_IMAGES)
                ]
            )
        ]
    )