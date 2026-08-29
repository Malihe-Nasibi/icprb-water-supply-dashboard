"""
Home layout module.

This file builds the landing page for the dashboard.
"""

from dash import dcc, html

from data_fetching.streamflow_usgs import load_station_record, get_daily_cache_key
from figures.streamflow_figures import build_streamflow_figure, make_error_figure
from figures.drought_figures import build_potomac_usdm_map_src


# Home page helper figures

def build_home_streamflow_preview():
    site_id = "01646500"
    flow_type = "daily"

    try:
        df_station = load_station_record(site_id)
        selected_year = int(df_station["Year"].max())

        fig = build_streamflow_figure(site_id, selected_year, flow_type)

        fig.update_layout(
            height=740,
            title=dict(
                text="<b>Daily Flow, Little Falls — USGS 01646500</b>",
                x=0.5,
                xanchor="center",
                y=0.965,
                yanchor="top",
                font=dict(
                    family="Arial",
                    size=16,
                    color="black"
                )
            ),
            margin=dict(
                l=80,
                r=25,
                t=65,
                b=120
            )
        )

        return fig

    except Exception as e:
        return make_error_figure(str(e))


def build_home_drought_preview():
    image_src, image_error = build_potomac_usdm_map_src(get_daily_cache_key())

    if image_src is None:
        return html.Div(
            style={
                "height": "740px",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "color": "red",
                "fontSize": "18px",
                "textAlign": "center"
            },
            children=f"Potomac Basin drought map could not be loaded: {image_error}"
        )

    return html.Div(
        style={
            "height": "740px",
            "overflow": "hidden"
        },
        children=[
            html.Img(
                src=image_src,
                style={
                    "width": "100%",
                    "height": "740px",
                    "objectFit": "contain",
                    "marginTop": "-85px"
                }
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
                    "padding": "24px",
                    "borderRadius": "16px",
                    "boxShadow": "0px 3px 9px rgba(0,0,0,0.18)",
                    "border": "1px solid #e1e7ef"
                },
                children=[
                    html.P(
                        "ICPRB’s Section for Cooperative Water Supply Operations on the Potomac (CO-OP) was established in 1979 to serve as a cooperative technical center on water resources in the Potomac basin. "
                        "It supports the Washington, D.C., metropolitan water supply system through long-term planning, drought monitoring, operations coordination, drought exercises, and seasonal Water Supply Outlook & Status reports. "
                        "This dashboard brings together key water-supply indicators for the Potomac River Basin, including streamflow, flow forecasts, precipitation, groundwater, drought conditions, reservoir storage, and climate outlooks, "
                        "to support water supply decision-making.",
                        style={
                            "fontSize": "22px",
                            "lineHeight": "1.55",
                            "color": "#1f2d3d",
                            "width": "100%",
                            "maxWidth": "none",
                            "margin": "0 0 12px 0",
                            "textAlign": "justify"
                        }
                    ),

                    html.Div(
                        style={
                            "display": "flex",
                            "gap": "14px",
                            "flexWrap": "nowrap",
                            "alignItems": "flex-start"
                        },
                        children=[
                            html.Div(
                                style={
                                    "flex": "1.05",
                                    "minWidth": "0"
                                },
                                children=[
                                    dcc.Graph(
                                        figure=build_home_streamflow_preview(),
                                        config={"displaylogo": False}
                                    )
                                ]
                            ),

                            html.Div(
                                style={
                                    "flex": "1",
                                    "minWidth": "0"
                                },
                                children=[
                                    build_home_drought_preview()
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )