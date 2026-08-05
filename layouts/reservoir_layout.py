"""
Reservoir layout module.

This file builds the Reservoir Storage tab, including reservoir summary cards,
the reservoir dropdown, and the reservoir storage graph container.
"""

from dash import dcc, html

from config import RESERVOIR_DEFAULT_COLUMN, RESERVOIR_STORAGE_COLUMNS
from styles import DROPDOWN_TITLE_STYLE, DROPDOWN_CLASS_NAME
from data_fetching.reservoir import (
    load_reservoir_storage,
    get_available_reservoir_columns
)
from figures.reservoir_figures import (
    reservoir_latest_cards,
    build_reservoir_storage_figure
)




def reservoir_storage_layout():
    try:
        df = load_reservoir_storage()
        available_columns = get_available_reservoir_columns(df)

        if not available_columns:
            raise ValueError("No reservoir storage columns were found in the reservoir file.")

        default_column = (
            RESERVOIR_DEFAULT_COLUMN
            if RESERVOIR_DEFAULT_COLUMN in available_columns
            else available_columns[0]
        )

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
                            "Reservoir Storage",
                            style={
                                "fontSize": "28px",
                                "fontWeight": "bold",
                                "marginTop": "0px",
                                "marginBottom": "0px"
                            }
                        )
                    ]
                ),

                reservoir_latest_cards(df),

                html.Div(
                    style={
                        "width": "430px",
                        "padding": "14px",
                        "backgroundColor": "white",
                        "borderRadius": "12px",
                        "boxShadow": "0px 1px 5px rgba(0,0,0,0.18)",
                        "marginBottom": "22px"
                    },
                    children=[
                        html.Label(
                            "Select reservoir/storage variable:",
                            style=DROPDOWN_TITLE_STYLE
                        ),
                        dcc.Dropdown(
                            className=DROPDOWN_CLASS_NAME,
                            id="reservoir-storage-dropdown",
                            options=[
                                {
                                    "label": RESERVOIR_STORAGE_COLUMNS[column],
                                    "value": column
                                }
                                for column in available_columns
                            ],
                            value=default_column,
                            clearable=False,
                            style={"marginTop": "8px"}
                        )
                    ]
                ),

                html.Div(
                    style={
                        "backgroundColor": "white",
                        "padding": "18px",
                        "borderRadius": "14px",
                        "boxShadow": "0px 2px 7px rgba(0,0,0,0.18)",
                        "marginBottom": "24px",
                        "border": "1px solid #e1e7ef"
                    },
                    children=[
                        dcc.Graph(
                            id="reservoir-storage-graph",
                            figure=build_reservoir_storage_figure(default_column)
                        )
                    ]
                )
            ]
        )

    except Exception as e:
        return html.Div(
            style={
                "backgroundColor": "white",
                "padding": "30px",
                "borderRadius": "12px",
                "boxShadow": "0px 1px 5px rgba(0,0,0,0.18)",
                "textAlign": "center"
            },
            children=[
                html.H2("Reservoir Storage"),
                html.Div(
                    style={
                        "padding": "18px",
                        "border": "1px solid #e1e7ef",
                        "borderRadius": "10px",
                        "backgroundColor": "#fff7f7",
                        "color": "#8a1f1f",
                        "whiteSpace": "pre-wrap",
                        "fontSize": "14px",
                        "textAlign": "left"
                    },
                    children=str(e)
                )
            ]
        )