"""
Main dashboard application.

This file creates the Dash app, applies dashboard CSS, builds the main page,
registers callbacks, provides the server object for deployment, and starts the
dashboard when running locally with python app.py.
"""

from dash import Dash, dcc, html

from callbacks import register_callbacks
from styles import DROPDOWN_CSS
from layouts.home_layout import home_layout
from layouts.streamflow_layout import streamflow_layout


# Build Dash app

app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server


# CSS for dropdown labels and options

app.index_string = f"""
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <style>
        {DROPDOWN_CSS}
        </style>
    </head>
    <body>
        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
"""


# Dashboard menu styles

MENU_TAB_STYLE = {
    "width": "100%",
    "boxSizing": "border-box",
    "padding": "17px 18px",
    "margin": "0 auto 12px auto",
    "borderRadius": "12px",
    "backgroundColor": "#e7eef6",
    "color": "#1f2d3d",
    "fontSize": "20px",
    "fontWeight": "bold",
    "border": "1px solid #c7d4e3",
    "boxShadow": "0px 3px 7px rgba(0,0,0,0.16)",
    "cursor": "pointer",
    "textAlign": "center"
}

MENU_TAB_SELECTED_STYLE = {
    "width": "100%",
    "boxSizing": "border-box",
    "padding": "17px 18px",
    "margin": "0 auto 12px auto",
    "borderRadius": "12px",
    "backgroundColor": "#1f4e79",
    "color": "white",
    "fontSize": "20px",
    "fontWeight": "900",
    "border": "1px solid #153650",
    "boxShadow": (
        "inset 1px 1px 2px rgba(255,255,255,0.35), "
        "inset -2px -2px 4px rgba(0,0,0,0.25), "
        "0px 5px 10px rgba(0,0,0,0.24)"
    ),
    "cursor": "pointer",
    "textAlign": "center"
}


# Main app layout

app.layout = html.Div(
    style={
        "fontFamily": "Arial",
        "backgroundColor": "#f7f9fb",
        "minHeight": "100vh",
        "padding": "25px"
    },
    children=[
        html.Div(
            style={
                "width": "100%",
                "display": "flex",
                "justifyContent": "center",
                "alignItems": "center",
                "marginBottom": "18px",
                "paddingLeft": "334px",
                "boxSizing": "border-box"
            },
            children=[
                html.Div(
                    style={
                        "textAlign": "center"
                    },
                    children=[
                        html.Div(
                            "Interstate Commission on the Potomac River Basin",
                            style={
                                "fontSize": "34px",
                                "fontWeight": "bold",
                                "color": "#1f2d3d",
                                "marginBottom": "4px"
                            }
                        ),
                        html.H1(
                            "Water Supply Outlook Dashboard",
                            style={
                                "fontSize": "34px",
                                "fontWeight": "bold",
                                "margin": "0px",
                                "color": "#1f2d3d"
                            }
                        )
                    ]
                )
            ]
        ),

        html.Div(
            style={
                "display": "flex",
                "gap": "22px",
                "alignItems": "flex-start"
            },
            children=[
                html.Div(
                    style={
                        "width": "290px",
                        "backgroundColor": "white",
                        "borderRadius": "16px",
                        "boxShadow": "0px 4px 12px rgba(0,0,0,0.18)",
                        "padding": "20px",
                        "position": "sticky",
                        "top": "20px",
                        "boxSizing": "border-box"
                    },
                    children=[
                        html.Div(
                            style={
                                "textAlign": "center",
                                "marginBottom": "16px"
                            },
                            children=[
                                html.Img(
                                    src="/assets/logos/icprb.jpg",
                                    style={
                                        "height": "220px",
                                        "width": "220px",
                                        "objectFit": "contain"
                                    }
                                )
                            ]
                        ),

                        html.Div(
                            "Dashboard Menu",
                            style={
                                "fontWeight": "bold",
                                "fontSize": "23px",
                                "marginBottom": "22px",
                                "textAlign": "center",
                                "color": "#1f2d3d"
                            }
                        ),
                        dcc.Tabs(
                            id="dashboard-tab",
                            value="home",
                            vertical=True,
                            parent_style={
                                "border": "none",
                                "width": "100%"
                            },
                            style={
                                "height": "auto",
                                "border": "none",
                                "width": "100%"
                            },
                            children=[
                                dcc.Tab(
                                    label="Home",
                                    value="home",
                                    style=MENU_TAB_STYLE,
                                    selected_style=MENU_TAB_SELECTED_STYLE
                                ),
                                dcc.Tab(
                                    label="Historical Streamflow",
                                    value="streamflow",
                                    style=MENU_TAB_STYLE,
                                    selected_style=MENU_TAB_SELECTED_STYLE
                                ),
                                dcc.Tab(
                                    label="Streamflow Forecast",
                                    value="flow_forecasts",
                                    style=MENU_TAB_STYLE,
                                    selected_style=MENU_TAB_SELECTED_STYLE
                                ),
                                dcc.Tab(
                                    label="Precipitation",
                                    value="precip",
                                    style=MENU_TAB_STYLE,
                                    selected_style=MENU_TAB_SELECTED_STYLE
                                ),
                                dcc.Tab(
                                    label="Groundwater",
                                    value="groundwater",
                                    style=MENU_TAB_STYLE,
                                    selected_style=MENU_TAB_SELECTED_STYLE
                                ),
                                dcc.Tab(
                                    label="Drought Monitor",
                                    value="drought",
                                    style=MENU_TAB_STYLE,
                                    selected_style=MENU_TAB_SELECTED_STYLE
                                ),
                                dcc.Tab(
                                    label="Reservoir Storage",
                                    value="reservoir",
                                    style=MENU_TAB_STYLE,
                                    selected_style=MENU_TAB_SELECTED_STYLE
                                ),
                                dcc.Tab(
                                    label="Climate Outlooks",
                                    value="noaa",
                                    style=MENU_TAB_STYLE,
                                    selected_style=MENU_TAB_SELECTED_STYLE
                                )
                            ]
                        )
                    ]
                ),

                html.Div(
                    id="main-content",
                    style={
                        "flex": "1",
                        "minWidth": "0"
                    },
                    children=home_layout()
                )
            ]
        ),

        html.Div(
            id="image-modal",
            style={
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
            },
            children=[
                html.Div(
                    style={
                        "backgroundColor": "white",
                        "borderRadius": "12px",
                        "padding": "18px",
                        "maxWidth": "1200px",
                        "margin": "auto",
                        "textAlign": "center",
                        "position": "relative"
                    },
                    children=[
                        html.Button(
                            "× Close",
                            id="close-image-modal",
                            n_clicks=0,
                            style={
                                "position": "absolute",
                                "right": "15px",
                                "top": "12px",
                                "fontSize": "18px",
                                "fontWeight": "bold",
                                "backgroundColor": "#f2f2f2",
                                "border": "1px solid lightgray",
                                "borderRadius": "6px",
                                "padding": "6px 10px",
                                "cursor": "pointer"
                            }
                        ),
                        html.H3(
                            id="modal-image-title",
                            style={
                                "fontSize": "26px",
                                "fontWeight": "bold",
                                "marginTop": "35px",
                                "marginBottom": "6px"
                            }
                        ),
                        html.P(
                            id="modal-image-source",
                            style={
                                "fontSize": "15px",
                                "color": "gray",
                                "marginTop": "0px",
                                "marginBottom": "12px"
                            }
                        ),
                        html.Img(
                            id="modal-image",
                            src="",
                            style={
                                "width": "100%",
                                "maxWidth": "1120px",
                                "maxHeight": "78vh",
                                "objectFit": "contain",
                                "border": "1px solid lightgray"
                            }
                        )
                    ]
                )
            ]
        )
    ]
)


# Register callbacks

register_callbacks(app)


# Run app

if __name__ == "__main__":
    app.run(
        debug=True,
        use_reloader=False
    )