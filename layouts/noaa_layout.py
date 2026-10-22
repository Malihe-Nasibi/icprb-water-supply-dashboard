"""
NOAA layout module.

This file builds the Climate Outlooks tab.

It also defines image_card(), a small reusable function that creates one
clickable image box with a title, source text, and image. The same image_card()
function is also used by the Precipitation tab.
"""

from dash import html

from config import NOAA_OUTLOOK_IMAGES


# Outlook image card

def image_card(item, group, index, card_style=None):
    return html.Div(
        style={
            "backgroundColor": "white",
            "padding": "18px",
            "borderRadius": "14px",
            "boxShadow": "0px 2px 7px rgba(0,0,0,0.18)",
            "marginBottom": "24px",
            "border": "1px solid #e1e7ef",
            "width": "520px",
            **(card_style or {})
        },
        children=[
            html.H3(
                item["title"],
                style={
                    "textAlign": "center",
                    "fontSize": "24px",
                    "fontWeight": "bold",
                    "marginTop": "0px",
                    "marginBottom": "6px",
                    "color": "#1f2d3d"
                }
            ),
            html.P(
                item["source"],
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
                        src=item["url"],
                        style={
                            "width": "100%",
                            "border": "1px solid lightgray",
                            "cursor": "pointer"
                        }
                    )
                ]
            )
        ]
    )


# Outlook section

def outlook_section(title, items, group, index_offset):
    return html.Div(
        style={
            "width": "100%",
            "maxWidth": "1300px",
            "margin": "0 auto"
        },
        children=[
            html.H3(
                title,
                style={
                    "fontSize": "25px",
                    "fontWeight": "bold",
                    "color": "#1f2d3d",
                    "marginTop": "8px",
                    "marginBottom": "12px",
                    "textAlign": "left"
                }
            ),
            html.Div(
                style={
                    "display": "grid",
                    "gridTemplateColumns": "repeat(auto-fit, minmax(min(100%, 500px), 1fr))",
                    "gap": "12px",
                    "alignItems": "start",
                    "justifyItems": "center",
                    "width": "100%",
                    "marginBottom": "12px"
                },
                children=[
                    image_card(
                        item,
                        group,
                        index_offset + i,
                        card_style={
                            "width": "100%",
                            "maxWidth": "644px",
                            "minWidth": "0",
                            "boxSizing": "border-box",
                            "padding": "12px",
                            "marginBottom": "0px"
                        }
                    )
                    for i, item in enumerate(items)
                ]
            )
        ]
    )


# Climate Outlooks tab layout

def noaa_outlooks_layout():
    monthly_items = NOAA_OUTLOOK_IMAGES["monthly"]
    seasonal_items = NOAA_OUTLOOK_IMAGES["seasonal"]

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
                        "Climate Outlooks",
                        style={
                            "fontSize": "28px",
                            "fontWeight": "bold",
                            "marginTop": "0px"
                        }
                    ),
                    html.P(
                        "NOAA Climate Prediction Center monthly and seasonal outlook products.",
                        style={
                            "fontSize": "16px",
                            "marginBottom": "0px"
                        }
                    )
                ]
            ),
            outlook_section(
                title="Monthly Outlooks",
                items=monthly_items,
                group="noaa",
                index_offset=0
            ),
            outlook_section(
                title="Seasonal Outlooks",
                items=seasonal_items,
                group="noaa",
                index_offset=len(monthly_items)
            )
        ]
    )