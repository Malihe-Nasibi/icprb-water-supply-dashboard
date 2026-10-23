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


# Dashboard layout styles

LAYOUT_CSS = """
.dashboard-page {
    padding: 16px;
}

.dashboard-header {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin-bottom: 10px;
}

.dashboard-logo {
    width: clamp(60px, 7vw, 85px);
    height: auto;
    flex-shrink: 0;
    object-fit: contain;
}

.dashboard-heading {
    min-width: 0;
    text-align: center;
}

.dashboard-organization {
    font-size: clamp(18px, 2vw, 26px);
    font-weight: bold;
    line-height: 1.2;
    color: #1f2d3d;
    margin-bottom: 4px;
    overflow-wrap: break-word;
}

.dashboard-title {
    font-size: clamp(20px, 2.2vw, 28px);
    font-weight: bold;
    line-height: 1.2;
    margin: 0;
    color: #1f2d3d;
    overflow-wrap: break-word;
}

.dashboard-navigation {
    background-color: white;
    border-radius: 12px;
    box-shadow: 0px 2px 7px rgba(0,0,0,0.16);
    padding: 8px;
    margin-bottom: 12px;
}

.dashboard-tabs {
    display: grid !important;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    grid-auto-rows: 1fr;
    gap: 8px;
    width: 100%;
    min-width: 0;
    border: none !important;
}

.dashboard-tabs .dashboard-menu-tab {
    display: flex !important;
    align-items: center;
    justify-content: center;
    width: 100% !important;
    min-width: 0 !important;
    min-height: 44px;
    height: 100%;
    white-space: normal;
    overflow-wrap: break-word;
}

@media (min-width: 1550px) {
    .dashboard-tabs {
        grid-template-columns: repeat(8, minmax(0, 1fr));
    }
}

@media (max-width: 600px) {
    .dashboard-page {
        padding: 10px;
    }

    .dashboard-header {
        flex-direction: column;
        gap: 6px;
        margin-bottom: 10px;
    }

    .dashboard-navigation {
        padding: 6px;
        margin-bottom: 12px;
    }

    .dashboard-tabs {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 6px;
    }
}
"""


# CSS for dropdown labels, options, and dashboard layout

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
        {LAYOUT_CSS}
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
    "boxSizing": "border-box",
    "padding": "clamp(8px, 0.9vw, 10px) clamp(8px, 1vw, 12px)",
    "margin": "0",
    "borderRadius": "10px",
    "backgroundColor": "#e7eef6",
    "color": "#1f2d3d",
    "fontSize": "clamp(14px, 1.4vw, 17px)",
    "fontWeight": "bold",
    "border": "1px solid #c7d4e3",
    "boxShadow": "0px 3px 7px rgba(0,0,0,0.16)",
    "cursor": "pointer",
    "textAlign": "center",
    "lineHeight": "1.3"
}

MENU_TAB_SELECTED_STYLE = {
    "boxSizing": "border-box",
    "padding": "clamp(8px, 0.9vw, 10px) clamp(8px, 1vw, 12px)",
    "margin": "0",
    "borderRadius": "10px",
    "backgroundColor": "#1f4e79",
    "color": "white",
    "fontSize": "clamp(14px, 1.4vw, 17px)",
    "fontWeight": "900",
    "border": "1px solid #153650",
    "boxShadow": (
        "inset 1px 1px 2px rgba(255,255,255,0.35), "
        "inset -2px -2px 4px rgba(0,0,0,0.25), "
        "0px 5px 10px rgba(0,0,0,0.24)"
    ),
    "cursor": "pointer",
    "textAlign": "center",
    "lineHeight": "1.3"
}


# Main app layout

app.layout = html.Div(
    className="dashboard-page",
    style={
        "fontFamily": "Arial",
        "backgroundColor": "#f7f9fb",
        "minHeight": "100vh",
        "boxSizing": "border-box"
    },
    children=[
        html.Div(
            className="dashboard-header",
            children=[
                html.Img(
                    src="/assets/logos/icprb.jpg",
                    className="dashboard-logo"
                ),
                html.Div(
                    className="dashboard-heading",
                    children=[
                        html.Div(
                            "Interstate Commission on the Potomac River Basin",
                            className="dashboard-organization"
                        ),
                        html.H1(
                            "Water Supply Outlook Dashboard",
                            className="dashboard-title"
                        )
                    ]
                )
            ]
        ),

        html.Div(
            className="dashboard-navigation",
            children=[
                dcc.Tabs(
                    id="dashboard-tab",
                    value="home",
                    vertical=False,
                    mobile_breakpoint=0,
                    parent_style={
                        "border": "none",
                        "width": "100%",
                        "minWidth": "0"
                    },
                    className="dashboard-tabs",
                    children=[
                        dcc.Tab(
                            label="Home",
                            value="home",
                            className="dashboard-menu-tab",
                            selected_className="dashboard-menu-tab",
                            style=MENU_TAB_STYLE,
                            selected_style=MENU_TAB_SELECTED_STYLE
                        ),
                        dcc.Tab(
                            label="Historical Streamflow",
                            value="streamflow",
                            className="dashboard-menu-tab",
                            selected_className="dashboard-menu-tab",
                            style=MENU_TAB_STYLE,
                            selected_style=MENU_TAB_SELECTED_STYLE
                        ),
                        dcc.Tab(
                            label="Streamflow Forecast",
                            value="flow_forecasts",
                            className="dashboard-menu-tab",
                            selected_className="dashboard-menu-tab",
                            style=MENU_TAB_STYLE,
                            selected_style=MENU_TAB_SELECTED_STYLE
                        ),
                        dcc.Tab(
                            label="Precipitation",
                            value="precip",
                            className="dashboard-menu-tab",
                            selected_className="dashboard-menu-tab",
                            style=MENU_TAB_STYLE,
                            selected_style=MENU_TAB_SELECTED_STYLE
                        ),
                        dcc.Tab(
                            label="Groundwater",
                            value="groundwater",
                            className="dashboard-menu-tab",
                            selected_className="dashboard-menu-tab",
                            style=MENU_TAB_STYLE,
                            selected_style=MENU_TAB_SELECTED_STYLE
                        ),
                        dcc.Tab(
                            label="Drought Monitor",
                            value="drought",
                            className="dashboard-menu-tab",
                            selected_className="dashboard-menu-tab",
                            style=MENU_TAB_STYLE,
                            selected_style=MENU_TAB_SELECTED_STYLE
                        ),
                        dcc.Tab(
                            label="Reservoir Storage",
                            value="reservoir",
                            className="dashboard-menu-tab",
                            selected_className="dashboard-menu-tab",
                            style=MENU_TAB_STYLE,
                            selected_style=MENU_TAB_SELECTED_STYLE
                        ),
                        dcc.Tab(
                            label="Climate Outlooks",
                            value="noaa",
                            className="dashboard-menu-tab",
                            selected_className="dashboard-menu-tab",
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
                "width": "100%",
                "minWidth": "0"
            },
            children=home_layout()
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
        ),

        # Popup for Home content and interactive graphs
        html.Div(
            id="content-modal",
            style={"display": "none"},
            children=[
                html.Div(
                    style={
                        "backgroundColor": "white",
                        "borderRadius": "12px",
                        "padding": "16px",
                        "width": "100%",
                        "maxWidth": "1500px",
                        "maxHeight": "94vh",
                        "overflowY": "auto",
                        "margin": "auto",
                        "boxSizing": "border-box"
                    },
                    children=[
                        html.Div(
                            style={
                                "display": "flex",
                                "justifyContent": "flex-end",
                                "marginBottom": "10px"
                            },
                            children=[
                                html.Button(
                                    "× Close",
                                    id="close-content-modal",
                                    n_clicks=0,
                                    style={
                                        "fontSize": "18px",
                                        "fontWeight": "bold",
                                        "backgroundColor": "#f2f2f2",
                                        "border": "1px solid lightgray",
                                        "borderRadius": "6px",
                                        "padding": "6px 10px",
                                        "cursor": "pointer"
                                    }
                                )
                            ]
                        ),
                        html.Div(id="content-modal-body")
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