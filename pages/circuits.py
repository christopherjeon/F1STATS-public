import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objs as go
import os
import unicodedata
import requests
import json
import wikipedia
from bs4 import BeautifulSoup
import re
from urllib.request import urlopen
from data_reader import *
from app import app


files = os.listdir("assets/images/circuits")
circuit_list = [x.split(".")[0] for x in files]
df_circuits_2020 = df_circuits[df_circuits.circuitRef.isin(circuit_list)]

merge_races_circuits = pd.merge(df_circuits, df_races, how="inner", on="circuitId")
merge_races_circuits = merge_races_circuits[
    ["circuitId", "circuitRef", "location", "country", "raceId", "date"]
]

merge_results_drivers = pd.merge(df_results, df_drivers, how="inner", on="driverId")
merge_results_drivers = merge_results_drivers[
    [
        "resultId",
        "raceId",
        "driverId",
        "constructorId",
        "grid",
        "position",
        "time",
        "fastestLapTime",
        "driverRef",
    ]
]

all_individual_results = pd.merge(
    merge_races_circuits, merge_results_drivers, how="inner", on="raceId"
)
all_individual_results = pd.merge(
    all_individual_results, df_drivers, how="inner", on="driverRef"
)
all_individual_results["fullName"] = all_individual_results["forename"].str.cat(
    all_individual_results["surname"], sep=" "
)


def get_circuit_dict():
    keys = list(df_circuits_2020["name"])
    values = list(df_circuits_2020["circuitRef"])
    circuit_dict = dict(zip(keys, values))

    return {k: v for k, v in sorted(circuit_dict.items(), key=lambda item: item[1])}


current_circuits = get_circuit_dict()


def circuit_layout(circuit_name):
    circuit_id = current_circuits[circuit_name]
    return circuit_id


def most_wins(circuit_name):
    circuit_id = current_circuits[circuit_name]

    if circuit_id == "hanoi":
        return "N/A"

    all_results_by_gp = all_individual_results[
        (all_individual_results["circuitRef"] == circuit_id)
        & (all_individual_results["position"] == "1")
    ]

    gp_winners_dict = all_results_by_gp["fullName"].value_counts().to_dict()
    most_wins_driver = list(gp_winners_dict.keys())[0]
    num_wins = gp_winners_dict[most_wins_driver]

    return str(str(num_wins) + ", " + most_wins_driver)


def most_poles(circuit_name):
    circuit_id = current_circuits[circuit_name]

    if circuit_id == "hanoi":
        return "N/A"

    all_results_by_gp = all_individual_results[
        (all_individual_results["circuitRef"] == circuit_id)
        & (all_individual_results["grid"] == 1)
    ]

    gp_poles_dict = all_results_by_gp["fullName"].value_counts().to_dict()
    most_poles_driver = list(gp_poles_dict.keys())[0]
    num_poles = gp_poles_dict[most_poles_driver]

    return str(str(num_poles) + ", " + most_poles_driver)


def fastest_lap(circuit_name):
    circuit_id = current_circuits[circuit_name]

    if circuit_id == "hanoi":
        return "N/A"

    all_results_by_gp = all_individual_results[
        (all_individual_results["circuitRef"] == circuit_id)
    ].sort_values(by=["fastestLapTime"])

    fastest_lap_driver = all_results_by_gp.iloc[0]["fullName"]
    fastest_lap_time = all_results_by_gp.iloc[0]["fastestLapTime"]

    return str(fastest_lap_time + ", " + fastest_lap_driver)


def layout():
    return [
        html.Div(
            children=[
                dbc.CardDeck(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader("Most Wins:"),
                                dbc.CardBody(children=[html.H6(id="winsCard")]),
                            ]
                        ),
                        dbc.Card(
                            [
                                dbc.CardHeader("Most Pole Positions:"),
                                dbc.CardBody(children=[html.H6(id="polesCard")]),
                            ]
                        ),
                        dbc.Card(
                            [
                                dbc.CardHeader("Fastest Lap Record:"),
                                dbc.CardBody(children=[html.H6(id="lapCard")]),
                            ]
                        ),
                    ]
                )
            ],
            style={"padding-left": "15px", "padding-right": "15px"},
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Select Circuit"),
                            dbc.CardBody(
                                children=[
                                    dcc.Dropdown(
                                        id="gp-column",
                                        options=[
                                            {"label": i, "value": i}
                                            for i in list(current_circuits.keys())
                                        ],
                                        clearable=True,
                                        searchable=True,
                                        value="Albert Park Grand Prix Circuit",
                                        style={"width": "300px"},
                                    ),
                                    dcc.Loading(
                                        children=[
                                            html.P(
                                                id="circuit-about-card",
                                                style={"margin": "5 10px"},
                                            )
                                        ],
                                        type="circle",
                                    ),
                                ]
                            ),
                        ]
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader("Circuit Layout"),
                            dbc.CardBody(
                                children=[
                                    html.Img(
                                        id="circuit-layout",
                                        # todo: find better way to size this
                                        style={"height": "450px", "width": "700px"},
                                    )
                                ]
                            ),
                        ]
                    ),
                    width=8,
                ),
            ]
        ),
    ]


@app.callback(Output("circuit-about-card", "children"), [Input("gp-column", "value")])
def get_circuit_about_card(name):
    if name is not None:
        return wikipedia.summary(name, sentences=5)
    else:
        raise PreventUpdate


@app.callback(Output("circuit-layout", "src"), [Input("gp-column", "value")])
def get_circuit_layout(name):
    if name is not None:
        file_name = circuit_layout(name)
        return app.get_asset_url("images/circuits/{}.png").format(file_name)
    else:
        raise PreventUpdate


@app.callback(Output("winsCard", "children"), [Input("gp-column", "value")])
def get_most_wins(name):
    if name is not None:
        return most_wins(name)
    else:
        raise PreventUpdate


@app.callback(Output("polesCard", "children"), [Input("gp-column", "value")])
def get_most_poles(name):
    if name is not None:
        return most_poles(name)
    else:
        raise PreventUpdate


@app.callback(Output("lapCard", "children"), [Input("gp-column", "value")])
def get_fastest_lap(name):
    if name is not None:
        return fastest_lap(name)
    else:
        raise PreventUpdate
