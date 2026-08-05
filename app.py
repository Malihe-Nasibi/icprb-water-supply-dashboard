"""
Main dashboard application.

This file creates the Dash app, applies dashboard CSS, builds the main page,
registers callbacks, provides the server object for deployment, and starts the
dashboard when running locally with python app.py.
"""

from dash import Dash, dcc, html

from callbacks import register_callbacks
from styles import DROPDOWN_CSS
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


# Main app layout

app.layout = html.Div(
    style={
        "fontFamily": "Arial",
        "backgroundColor": "#f7f9fb",
        "minHeight": "100vh",
        "padding": "25px"
    },
    children=[
        html.H1(
            "Water Supply Outlook Dashboard",
            style={
                "textAlign": "center",
                "fontSize": "34px",
                "fontWeight": "bold",
                "marginBottom": "8px"
            }
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
                        "top": "20px"
                    },
                    children=[
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
                        dcc.RadioItems(
                            id="dashboard-tab",
                            options=[
                                {"label": " Streamflow", "value": "streamflow"},
                                {"label": " Flow Forecasts", "value": "flow_forecasts"},
                                {"label": " Groundwater", "value": "groundwater"},
                                {"label": " Drought Monitor", "value": "drought"},
                                {"label": " Reservoir Storage", "value": "reservoir"},
                                {"label": " NOAA Outlooks", "value": "noaa"},
                                {"label": " Precipitation", "value": "precip"}
                            ],
                            value="streamflow",
                            labelStyle={
                                "display": "block",
                                "padding": "18px 20px",
                                "marginBottom": "15px",
                                "borderRadius": "13px",
                                "backgroundColor": "#dfe8f3",
                                "cursor": "pointer",
                                "fontSize": "20px",
                                "fontWeight": "bold",
                                "color": "#1f2d3d",
                                "boxShadow": "0px 4px 8px rgba(0,0,0,0.18)",
                                "border": "2px solid #c7d4e3",
                                "minWidth": "190px"
                            },
                            inputStyle={
                                "marginRight": "12px",
                                "transform": "scale(1.25)"
                            }
                        )
                    ]
                ),

                html.Div(
                    id="main-content",
                    style={
                        "flex": "1",
                        "minWidth": "0"
                    },
                    children=streamflow_layout()
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