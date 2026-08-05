"""
Flow Forecasts layout module.

This file builds the Flow Forecasts tab, including forecast station/model
dropdowns, MARFC forecast image panels, and the NOAA/NWPS graph panel.
"""

from datetime import date

from dash import dcc, html

from config import FLOW_FORECAST_STATIONS, FLOW_FORECAST_MODELS
from styles import DROPDOWN_TITLE_STYLE, DROPDOWN_CLASS_NAME
from figures.forecast_figures import build_marfc_image_url, build_nwps_forecast_figure


# MARFC ensemble image panel

def marfc_ensemble_image_panel(selected_station_id, selected_model):
    station = FLOW_FORECAST_STATIONS[selected_station_id]
    model_label = FLOW_FORECAST_MODELS[selected_model]
    cache_buster = date.today().strftime("%Y%m%d")
    image_url = f"{build_marfc_image_url(selected_station_id, selected_model)}?v={cache_buster}"
    modal_index = f"{selected_station_id}|{selected_model}"

    return html.Div(
        style={
            "backgroundColor": "white",
            "padding": "18px",
            "borderRadius": "14px",
            "boxShadow": "0px 2px 7px rgba(0,0,0,0.18)",
            "marginBottom": "24px",
            "border": "1px solid #e1e7ef"
        },
        children=[
            html.H3(
                f"MARFC Ensemble River Forecast — {model_label}",
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
                f"{station['subtitle']}",
                style={
                    "textAlign": "center",
                    "fontSize": "15px",
                    "fontWeight": "bold",
                    "color": "#44546a",
                    "marginTop": "0px",
                    "marginBottom": "6px"
                }
            ),
            html.P(
                "NOAA / Middle Atlantic River Forecast Center",
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
                            "group": "marfc",
                            "index": modal_index
                        },
                        n_clicks=0,
                        src=image_url,
                        style={
                            "width": "100%",
                            "maxWidth": "1150px",
                            "border": "1px solid lightgray",
                            "cursor": "pointer"
                        }
                    )
                ]
            )
        ]
    )


# NOAA/NWPS official forecast panel

def nwps_official_forecast_panel(selected_station_id):
    station = FLOW_FORECAST_STATIONS[selected_station_id]

    return html.Div(
        style={
            "backgroundColor": "white",
            "padding": "18px",
            "borderRadius": "14px",
            "boxShadow": "0px 2px 7px rgba(0,0,0,0.18)",
            "marginBottom": "24px",
            "border": "1px solid #e1e7ef"
        },
        children=[
            html.H3(
                "NOAA/NWPS Official Forecast",
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
                f"{station['subtitle']}",
                style={
                    "textAlign": "center",
                    "fontSize": "15px",
                    "fontWeight": "bold",
                    "color": "#44546a",
                    "marginTop": "0px",
                    "marginBottom": "6px"
                }
            ),
            dcc.Graph(
                id="nwps-official-forecast-graph",
                figure=build_nwps_forecast_figure(selected_station_id),
                config={"displaylogo": False}
            )
        ]
    )


# Forecast product selector

def flow_forecast_products(selected_station_id, selected_model):
    if selected_model == "NWPS":
        return nwps_official_forecast_panel(selected_station_id)

    return marfc_ensemble_image_panel(selected_station_id, selected_model)


# Flow Forecasts tab layout

def flow_forecasts_layout():
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
                        "Flow Forecasts",
                        style={
                            "fontSize": "28px",
                            "fontWeight": "bold",
                            "marginTop": "0px"
                        }
                    ),
                    html.P(
                        "MARFC ensemble forecasts and NOAA/NWPS official forecast products for selected Potomac River forecast points.",
                        style={
                            "fontSize": "16px",
                            "marginBottom": "0px"
                        }
                    )
                ]
            ),
            html.Div(
                style={
                    "display": "flex",
                    "gap": "20px",
                    "flexWrap": "wrap",
                    "marginBottom": "22px"
                },
                children=[
                    html.Div(
                        style={
                            "width": "420px",
                            "padding": "14px",
                            "backgroundColor": "white",
                            "borderRadius": "12px",
                            "boxShadow": "0px 1px 5px rgba(0,0,0,0.18)"
                        },
                        children=[
                            html.Label("Select forecast station:", style=DROPDOWN_TITLE_STYLE),
                            dcc.Dropdown(
                                className=DROPDOWN_CLASS_NAME,
                                id="forecast-station-dropdown",
                                options=[
                                    {
                                        "label": item["label"],
                                        "value": station_id
                                    }
                                    for station_id, item in FLOW_FORECAST_STATIONS.items()
                                ],
                                value="BRKM2",
                                clearable=False,
                                style={"marginTop": "8px"}
                            )
                        ]
                    ),
                    html.Div(
                        style={
                            "width": "320px",
                            "padding": "14px",
                            "backgroundColor": "white",
                            "borderRadius": "12px",
                            "boxShadow": "0px 1px 5px rgba(0,0,0,0.18)"
                        },
                        children=[
                            html.Label("Select forecast product/model:", style=DROPDOWN_TITLE_STYLE),
                            dcc.Dropdown(
                                className=DROPDOWN_CLASS_NAME,
                                id="forecast-model-dropdown",
                                options=[
                                    {
                                        "label": model_label,
                                        "value": model_id
                                    }
                                    for model_id, model_label in FLOW_FORECAST_MODELS.items()
                                ],
                                value="NAEFS",
                                clearable=False,
                                style={"marginTop": "8px"}
                            )
                        ]
                    )
                ]
            ),
            html.Div(
                id="forecast-products-container",
                children=flow_forecast_products("BRKM2", "NAEFS")
            )
        ]
    )