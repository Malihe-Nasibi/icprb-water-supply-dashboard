"""
Home layout module.

This file builds the landing page for the dashboard using a static summary
layout, prepared Water Supply Outlook figures, and tables.
"""

from dash import html

from data_fetching.streamflow_usgs import get_daily_cache_key
from figures.drought_figures import build_potomac_usdm_map_src


# Home page image paths

ADJUSTED_FLOW_IMAGE = "/assets/home/adjusted_flow.jpeg"
PRECIPITATION_12_MONTH_IMAGE = "/assets/home/precipitation_12_month.jpeg"
GROUNDWATER_LEVELS_IMAGE = "/assets/home/groundwater_levels.jpeg"


# Shared styles

CARD_STYLE = {
    "backgroundColor": "white",
    "borderRadius": "14px",
    "boxShadow": "0px 2px 7px rgba(0,0,0,0.16)",
    "border": "1px solid #e1e7ef",
    "padding": "10px",
    "boxSizing": "border-box"
}

IMAGE_STYLE = {
    "width": "100%",
    "maxWidth": "100%",
    "height": "auto",
    "display": "block",
    "objectFit": "contain"
}

TABLE_STYLE = {
    "width": "100%",
    "borderCollapse": "collapse",
    "fontSize": "15px",
    "color": "#1f2d3d"
}

TH_STYLE = {
    "backgroundColor": "#e7eef6",
    "border": "1px solid #c7d4e3",
    "padding": "8px",
    "textAlign": "center",
    "fontWeight": "bold",
    "fontSize": "14px"
}

TD_STYLE = {
    "border": "1px solid #c7d4e3",
    "padding": "8px",
    "textAlign": "center",
    "fontSize": "15px"
}


# Drought map helper

def build_home_drought_preview():
    image_src, image_error = build_potomac_usdm_map_src(get_daily_cache_key())

    if image_src is None:
        return html.Div(
            style={
                "height": "300px",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "color": "red",
                "fontSize": "16px",
                "textAlign": "center"
            },
            children=f"Potomac Basin drought map could not be loaded: {image_error}"
        )

    return html.Img(
        id={
            "type": "enlarge-content",
            "group": "home-image",
            "index": "drought"
        },
        n_clicks=0,
        src=image_src,
        style={
            **IMAGE_STYLE,
            "cursor": "pointer"
        }
    )


# Low-flow probability table

def low_flow_probability_table():
    return html.Div(
        style=CARD_STYLE,
        children=[
            html.H3(
                "Outlook for natural Potomac River flow at Little Falls – Watershed conditions as of August 1, 2026",
                style={
                    "fontSize": "18px",
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "color": "#1f2d3d",
                    "marginTop": "0px",
                    "marginBottom": "8px",
                    "lineHeight": "1.3"
                }
            ),
            html.Table(
                style=TABLE_STYLE,
                children=[
                    html.Thead(
                        html.Tr(
                            children=[
                                html.Th(
                                    ["Low flow threshold", html.Br(), "(MGD)"],
                                    style=TH_STYLE
                                ),
                                html.Th(
                                    ["Low flow threshold", html.Br(), "(cfs)"],
                                    style=TH_STYLE
                                ),
                                html.Th(
                                    [
                                        "Historical probability",
                                        html.Br(),
                                        "of lower flow",
                                        html.Br(),
                                        "Aug 1 through Dec 31"
                                    ],
                                    style=TH_STYLE
                                ),
                                html.Th(
                                    [
                                        "Conditional probability",
                                        html.Br(),
                                        "of lower flow",
                                        html.Br(),
                                        "Aug 1 through Dec 31"
                                    ],
                                    style=TH_STYLE
                                )
                            ]
                        )
                    ),
                    html.Tbody(
                        children=[
                            html.Tr(
                                children=[
                                    html.Td("700", style=TD_STYLE),
                                    html.Td("1084", style=TD_STYLE),
                                    html.Td("15%", style=TD_STYLE),
                                    html.Td("16%", style=TD_STYLE)
                                ]
                            ),
                            html.Tr(
                                children=[
                                    html.Td("600", style=TD_STYLE),
                                    html.Td("929", style=TD_STYLE),
                                    html.Td("7%", style=TD_STYLE),
                                    html.Td("5%", style=TD_STYLE)
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )


# Reservoir percent-full bar table

def reservoir_percent_bar(percent, color):
    return html.Div(
        style={
            "display": "flex",
            "alignItems": "center",
            "gap": "8px"
        },
        children=[
            html.Div(
                style={
                    "height": "16px",
                    "width": "100%",
                    "backgroundColor": "#edf1f5",
                    "borderRadius": "10px",
                    "overflow": "hidden",
                    "border": "1px solid #d5dde6"
                },
                children=[
                    html.Div(
                        style={
                            "height": "100%",
                            "width": f"{percent}%",
                            "backgroundColor": color,
                            "borderRadius": "10px"
                        }
                    )
                ]
            ),
            html.Div(
                f"{percent}%",
                style={
                    "minWidth": "42px",
                    "textAlign": "right",
                    "fontWeight": "bold",
                    "fontSize": "14px",
                    "color": "#1f2d3d"
                }
            )
        ]
    )


def reservoir_storage_status_table():
    rows = [
        ("WSSC Water’s Patuxent reservoirs", 94),
        ("Fairfax Water’s Occoquan Reservoir", 100),
        ("Little Seneca Reservoir", 97),
        ("Jennings Randolph water supply", 100),
        ("Jennings Randolph water quality", 85),
        ("Savage Reservoir", 68)
    ]

    def bar_color(percent):
        if percent <= 50:
            return "#C00000"
        elif percent <= 70:
            return "#E07B39"
        elif percent <= 90:
            return "#E6B800"
        else:
            return "#5BA061"

    return html.Div(
        style=CARD_STYLE,
        children=[
            html.H3(
                "Reservoir Storage as of August 10, 2026",
                style={
                    "fontSize": "18px",
                    "fontWeight": "bold",
                    "textAlign": "center",
                    "color": "#1f2d3d",
                    "marginTop": "0px",
                    "marginBottom": "8px"
                }
            ),
            html.Table(
                style=TABLE_STYLE,
                children=[
                    html.Thead(
                        html.Tr(
                            children=[
                                html.Th(
                                    "Facility",
                                    style={
                                        **TH_STYLE,
                                        "textAlign": "left"
                                    }
                                ),
                                html.Th(
                                    "Percent Full",
                                    style=TH_STYLE
                                )
                            ]
                        )
                    ),
                    html.Tbody(
                        children=[
                            html.Tr(
                                children=[
                                    html.Td(
                                        facility,
                                        style={
                                            **TD_STYLE,
                                            "textAlign": "left",
                                            "width": "44%"
                                        }
                                    ),
                                    html.Td(
                                        reservoir_percent_bar(percent, bar_color(percent)),
                                        style={
                                            **TD_STYLE,
                                            "width": "56%"
                                        }
                                    )
                                ]
                            )
                            for facility, percent in rows
                        ]
                    )
                ]
            )
        ]
    )


# Home page layout

def home_layout():
    return html.Div(
        children=[
            html.Div(
                style={
                    "backgroundColor": "white",
                    "padding": "14px",
                    "borderRadius": "16px",
                    "boxShadow": "0px 3px 9px rgba(0,0,0,0.18)",
                    "border": "1px solid #e1e7ef"
                },
                children=[
                    # Full-width description
                    html.P(
                        "ICPRB’s Section for Cooperative Water Supply Operations on the Potomac (CO-OP) was established in 1979 to serve as a cooperative technical center on water resources in the Potomac basin. "
                        "It supports the Washington, D.C., metropolitan water supply system through long-term planning, drought monitoring, operations coordination, drought exercises, and seasonal Water Supply Outlook & Status reports. "
                        "This dashboard brings together key water-supply indicators for the Potomac River Basin, including streamflow, flow forecasts, precipitation, groundwater, drought conditions, reservoir storage, and climate outlooks, "
                        "to support water supply decision-making.",
                        style={
                            "fontSize": "18px",
                            "lineHeight": "1.45",
                            "color": "#1f2d3d",
                            "margin": "0 0 12px 0",
                            "textAlign": "justify"
                        }
                    ),

                    # Full-width summary sentence
                    html.Div(
                        style={
                            "backgroundColor": "#eaf3fb",
                            "border": "1px solid #c7d4e3",
                            "borderRadius": "12px",
                            "padding": "10px 14px",
                            "marginBottom": "12px"
                        },
                        children=[
                            html.Div(
                                "There is a near-normal probability of releases from the Washington metropolitan area’s back-up water supply reservoirs for the 2026 summer and fall seasons.",
                                style={
                                    "fontSize": "18px",
                                    "fontWeight": "bold",
                                    "lineHeight": "1.45",
                                    "color": "black",
                                    "textAlign": "center"
                                }
                            )
                        ]
                    ),

                    # Row 1: Low-flow table and 12-month precipitation plot
                    html.Div(
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "repeat(auto-fit, minmax(min(100%, 450px), 1fr))",
                            "gap": "12px",
                            "alignItems": "center",
                            "marginBottom": "12px"
                        },
                        children=[
                            html.Div(
                                id={
                                    "type": "enlarge-content",
                                    "group": "home-table",
                                    "index": "low-flow"
                                },
                                n_clicks=0,
                                style={"cursor": "pointer"},
                                children=low_flow_probability_table()
                            ),

                            html.Div(
                                style=CARD_STYLE,
                                children=[
                                    html.Img(
                                        id={
                                            "type": "enlarge-content",
                                            "group": "home-image",
                                            "index": "precipitation"
                                        },
                                        n_clicks=0,
                                        src=PRECIPITATION_12_MONTH_IMAGE,
                                        style={
                                            **IMAGE_STYLE,
                                            "cursor": "pointer"
                                        }
                                    )
                                ]
                            )
                        ]
                    ),

                    # Row 2: Adjusted flow plot and drought map
                    html.Div(
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "repeat(auto-fit, minmax(min(100%, 450px), 1fr))",
                            "gap": "12px",
                            "alignItems": "center",
                            "marginBottom": "12px"
                        },
                        children=[
                            html.Div(
                                style=CARD_STYLE,
                                children=[
                                    html.Img(
                                        id={
                                            "type": "enlarge-content",
                                            "group": "home-image",
                                            "index": "adjusted-flow"
                                        },
                                        n_clicks=0,
                                        src=ADJUSTED_FLOW_IMAGE,
                                        style={
                                            **IMAGE_STYLE,
                                            "cursor": "pointer"
                                        }
                                    )
                                ]
                            ),

                            html.Div(
                                style=CARD_STYLE,
                                children=[
                                    build_home_drought_preview()
                                ]
                            )
                        ]
                    ),

                    # Row 3: Groundwater plot and reservoir storage bar table
                    html.Div(
                        style={
                            "display": "grid",
                            "gridTemplateColumns": "repeat(auto-fit, minmax(min(100%, 450px), 1fr))",
                            "gap": "12px",
                            "alignItems": "center"
                        },
                        children=[
                            html.Div(
                                style=CARD_STYLE,
                                children=[
                                    html.Img(
                                        id={
                                            "type": "enlarge-content",
                                            "group": "home-image",
                                            "index": "groundwater"
                                        },
                                        n_clicks=0,
                                        src=GROUNDWATER_LEVELS_IMAGE,
                                        style={
                                            **IMAGE_STYLE,
                                            "cursor": "pointer"
                                        }
                                    )
                                ]
                            ),

                            html.Div(
                                id={
                                    "type": "enlarge-content",
                                    "group": "home-table",
                                    "index": "reservoir"
                                },
                                n_clicks=0,
                                style={"cursor": "pointer"},
                                children=reservoir_storage_status_table()
                            )
                        ]
                    )
                ]
            )
        ]
    )