import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objs as go
import os
import pandas as pd
from dash.dependencies import Input, Output, State


from app import app

import pages


server = app.server

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        dbc.Navbar(
            children=[
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Img(
                                    src=app.get_asset_url("logo.png"), height="30px"
                                )
                            ),
                            dbc.Col(
                                dbc.NavbarBrand(
                                    "Formula 1 Stats Page", className="ml-2"
                                )
                            ),
                        ],
                        no_gutters=True,
                        className="ml-auto flex-nowrap mt-3 mt-md-0",
                        align="center",
                    ),
                    href=app.get_relative_path("/"),
                ),
                dbc.Row(
                    children=[
                        dbc.NavLink("Home", href=app.get_relative_path("/")),
                        dbc.NavLink("Seasons", href=app.get_relative_path("/seasons")),
                        dbc.NavLink("Drivers", href=app.get_relative_path("/drivers")),
                        dbc.NavLink(
                            "Constructors", href=app.get_relative_path("/constructors")
                        ),
                        dbc.NavLink(
                            "Circuits", href=app.get_relative_path("/circuits")
                        ),
                    ],
                    style={"paddingLeft": "480px"},
                ),
            ]
        ),
        html.Div(id="page-content"),
    ]
)


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def display_page_content(pathname):
    path = app.strip_relative_path(pathname)
    if not path:
        return pages.home.layout()
    elif path == "seasons":
        return pages.seasons.layout()
    elif path == "circuits":
        return pages.circuits.layout()
    elif path == "drivers":
        return pages.drivers.layout()
    elif path == "constructors":
        return pages.constructors.layout()
    else:
        return "404"


if __name__ == "__main__":
    app.run_server(debug=True)
