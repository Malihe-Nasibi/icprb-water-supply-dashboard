"""
Dashboard callbacks module.

This file contains the Dash callback functions that update tabs, dropdowns,
figures, forecast products, and image popups.
"""

from datetime import date

import plotly.graph_objects as go
from dash import Input, Output, ctx, ALL
from dash.exceptions import PreventUpdate
from config import (
    PRECIPITATION_IMAGES,
    NOAA_OUTLOOK_IMAGES,
    USDM_CURRENT_MAP_URL,
    FLOW_FORECAST_STATIONS,
    FLOW_FORECAST_MODELS
)
from data_fetching.streamflow_usgs import load_station_record, get_daily_cache_key
from figures.streamflow_figures import build_streamflow_figure, make_error_figure
from figures.groundwater_figures import build_groundwater_figure, make_groundwater_error_figure
from figures.reservoir_figures import build_reservoir_storage_figure, make_reservoir_error_figure
from figures.drought_figures import build_potomac_usdm_map_src
from figures.forecast_figures import build_marfc_image_url
from layouts.streamflow_layout import streamflow_layout
from layouts.groundwater_layout import groundwater_layout
from layouts.drought_layout import drought_monitor_layout
from layouts.noaa_layout import noaa_outlooks_layout
from layouts.precipitation_layout import precipitation_layout
from layouts.forecasts_layout import flow_forecasts_layout, flow_forecast_products
from layouts.reservoir_layout import reservoir_storage_layout


# Register callbacks

def register_callbacks(app):

    # Main tab callback

    @app.callback(
        Output("main-content", "children"),
        Input("dashboard-tab", "value")
    )
    def render_selected_tab(selected_tab):
        if selected_tab == "streamflow":
            return streamflow_layout()
        elif selected_tab == "flow_forecasts":
            return flow_forecasts_layout()
        elif selected_tab == "groundwater":
            return groundwater_layout()
        elif selected_tab == "drought":
            return drought_monitor_layout()
        elif selected_tab == "precip":
            return precipitation_layout()
        elif selected_tab == "noaa":
            return noaa_outlooks_layout()
        elif selected_tab == "reservoir":
            return reservoir_storage_layout()

        return streamflow_layout()


    # Callback to update groundwater figure

    @app.callback(
        Output("groundwater-graph", "figure"),
        Input("groundwater-well-dropdown", "value")
    )
    def update_groundwater_graph(well_name):
        if well_name is None:
            fig = go.Figure()
            fig.update_layout(
                title="Waiting for groundwater well selection...",
                template="plotly_white",
                height=500
            )
            return fig

        try:
            return build_groundwater_figure(well_name)
        except Exception as e:
            error_message = str(e)
            print("Groundwater callback error:", error_message)
            return make_groundwater_error_figure(error_message)


    # Callback to update flow forecast products by station and product/model

    @app.callback(
        Output("forecast-products-container", "children"),
        [
            Input("forecast-station-dropdown", "value"),
            Input("forecast-model-dropdown", "value")
        ]
    )
    def update_flow_forecast_products(selected_station_id, selected_model):
        if selected_station_id is None or selected_model is None:
            raise PreventUpdate

        return flow_forecast_products(selected_station_id, selected_model)


    # Callback to enlarge NOAA / precipitation / MARFC / drought images in modal

    @app.callback(
        [
            Output("image-modal", "style"),
            Output("modal-image", "src"),
            Output("modal-image-title", "children"),
            Output("modal-image-source", "children")
        ],
        [
            Input({"type": "outlook-image", "group": ALL, "index": ALL}, "n_clicks"),
            Input("close-image-modal", "n_clicks")
        ],
        prevent_initial_call=True
    )
    def toggle_image_modal(image_clicks, close_clicks):
        hidden_style = {
            "display": "none",
            "position": "fixed",
            "zIndex": "9999",
            "left": "0",
            "top": "0",
            "width": "100%",
            "height": "100%",
            "backgroundColor": "rgba(0,0,0,0.75)",
            "padding": "30px",
            "boxSizing": "border-box"
        }

        visible_style = hidden_style.copy()
        visible_style["display"] = "block"

        trigger = ctx.triggered_id

        if trigger == "close-image-modal":
            return hidden_style, "", "", ""

        if not image_clicks or all(click is None or click == 0 for click in image_clicks):
            raise PreventUpdate

        if isinstance(trigger, dict) and trigger.get("type") == "outlook-image":
            group = trigger.get("group")
            index = trigger.get("index")
            cache_buster = date.today().strftime("%Y%m%d")

            if group == "precipitation":
                if index is not None and index < len(PRECIPITATION_IMAGES):
                    item = PRECIPITATION_IMAGES[index]
                    image_url = f"{item['url']}?v={cache_buster}"
                    return visible_style, image_url, item["title"], item["source"]

            elif group == "noaa":
                if index is not None and index < len(NOAA_OUTLOOK_IMAGES):
                    item = NOAA_OUTLOOK_IMAGES[index]
                    image_url = f"{item['url']}?v={cache_buster}"
                    return visible_style, image_url, item["title"], item["source"]

            elif group == "drought":
                if index == 0:
                    image_url = f"{USDM_CURRENT_MAP_URL}?v={cache_buster}"
                    return (
                        visible_style,
                        image_url,
                        "National U.S. Drought Monitor Map",
                        "U.S. Drought Monitor / National Drought Mitigation Center"
                    )

                if index == 1:
                    image_src, image_error = build_potomac_usdm_map_src(get_daily_cache_key())

                    if image_src is None:
                        return (
                            visible_style,
                            "",
                            "Potomac Basin U.S. Drought Monitor Map",
                            image_error or "Potomac Basin drought map could not be created."
                        )

                    return (
                        visible_style,
                        image_src,
                        "Potomac Basin U.S. Drought Monitor Map",
                        ""
                    )

            elif group == "marfc":
                try:
                    selected_station_id, selected_model = index.split("|")
                except Exception:
                    raise PreventUpdate

                if (
                    selected_station_id in FLOW_FORECAST_STATIONS
                    and selected_model in FLOW_FORECAST_MODELS
                    and selected_model != "NWPS"
                ):
                    station = FLOW_FORECAST_STATIONS[selected_station_id]
                    model_label = FLOW_FORECAST_MODELS[selected_model]
                    image_url = f"{build_marfc_image_url(selected_station_id, selected_model)}?v={cache_buster}"

                    return (
                        visible_style,
                        image_url,
                        f"MARFC Ensemble River Forecast — {station['label']} — {model_label}",
                        "NOAA / Middle Atlantic River Forecast Center"
                    )

        raise PreventUpdate


    # Callback to update available years based on selected station

    @app.callback(
        [
            Output("year-dropdown", "options"),
            Output("year-dropdown", "value")
        ],
        Input("station-dropdown", "value")
    )
    def update_year_options(site_id):
        if site_id is None:
            return [], None

        try:
            df_station = load_station_record(site_id)
            available_years = sorted(df_station["Year"].unique(), reverse=True)

            if len(available_years) == 0:
                return [], None

            default_year = int(max(available_years))

            year_options = [
                {
                    "label": str(int(year)),
                    "value": int(year)
                }
                for year in available_years
            ]

            return year_options, default_year

        except Exception as e:
            print("Year dropdown callback error:", str(e))
            return [], None


    # Callback to update streamflow figure

    @app.callback(
        Output("streamflow-graph", "figure"),
        [
            Input("station-dropdown", "value"),
            Input("year-dropdown", "value"),
            Input("flow-type-dropdown", "value")
        ]
    )
    def update_streamflow_graph(site_id, selected_year, flow_type):
        if site_id is None or selected_year is None or flow_type is None:
            fig = go.Figure()
            fig.update_layout(
                title="Waiting for station, year, and flow-type selections...",
                template="plotly_white",
                height=500
            )
            return fig

        try:
            return build_streamflow_figure(site_id, selected_year, flow_type)
        except Exception as e:
            error_message = str(e)
            print("Streamflow callback error:", error_message)
            return make_error_figure(error_message)


    # Callback to update reservoir storage figure

    @app.callback(
        Output("reservoir-storage-graph", "figure"),
        Input("reservoir-storage-dropdown", "value")
    )
    def update_reservoir_storage_graph(selected_column):
        if selected_column is None:
            fig = go.Figure()
            fig.update_layout(
                title="Waiting for reservoir selection...",
                template="plotly_white",
                height=500
            )
            return fig

        try:
            return build_reservoir_storage_figure(selected_column)
        except Exception as e:
            error_message = str(e)
            print("Reservoir storage callback error:", error_message)
            return make_reservoir_error_figure(error_message)