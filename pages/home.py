import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
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
import sqlite3
import dash_twitter_widget

from app import app
from data_reader import *
from pages.constructors import constructor_standings_by_year

URL_seasons = "http://ergast.com/api/f1/seasons.json?limit=80"

data_seasons = requests.get(url=URL_seasons).json()

season_list = []
for year in data_seasons["MRData"]["SeasonTable"]["Seasons"]:
    season_list.append(year["season"])

season_list.reverse()

df_races_test = df_races.rename(columns={"name": "race_name", "url": "race_url"})
df_homepage_constructors = constructor_standings_by_year(2020)


def generate_recent_driver_standings():
    merge_standings = pd.merge(
        df_drivers, df_driver_standings, how="inner", on=["driverId"]
    )

    merge_standings_races = pd.merge(
        merge_standings, df_races_test, how="inner", on=["raceId"]
    )

    merge_standings_races_filtered = merge_standings_races[
        [
            "forename",
            "surname",
            "nationality",
            "points",
            "positionText",
            "wins",
            "year",
            "round",
        ]
    ]

    standings_all_rounds = merge_standings_races_filtered[
        (merge_standings_races_filtered["year"] == 2020)
    ].sort_values(by=["round", "points"], ascending=False)
    standings_all_rounds["driverName"] = (
        standings_all_rounds["forename"].astype(str)
        + " "
        + standings_all_rounds["surname"]
    )
    final_round = standings_all_rounds["round"].max()
    standings_final_round = standings_all_rounds[
        standings_all_rounds["round"] == final_round
    ]
    standings_final_round = standings_final_round[
        ["positionText", "driverName", "nationality", "points", "wins"]
    ]

    standings_final_round = standings_final_round.rename(
        columns={
            "driverName": "Name",
            "nationality": "Nationality",
            "points": "Points",
            "positionText": "Rank",
            "wins": "Wins",
            "year": "Year",
        }
    )
    return standings_final_round


df_homepage_drivers = generate_recent_driver_standings()


def layout():
    return [
        dbc.Col(
            dbc.Card(
                children=[
                    dbc.CardHeader("WELCOME TO F1STATS!"),
                    dbc.CardBody(
                        [
                            dcc.Markdown(
                                """
                                This web application produces race results, driver and constructor rankings, up-to-date timetables, circuit layouts, and comparisons of Formula 1 seasons from 1950 to the present.

                                Built with Python, [Dash](https://plotly.com/dash/), and the [Ergast Developer API](http://ergast.com/mrd/) (Motor Racing Data), this application provides users an in-depth look at the numbers behind Formula 1.

                                Questions, comments, or concerns? Feel free to reach out on [LinkedIn](https://www.linkedin.com/in/jeonchristopher/) and check out the source code [here](https://github.com/christopherjeon/F1STATS-public).
                                """,
                                style={"margin": "0 10px"},
                            )
                        ]
                    ),
                ]
            ),
            width=12,
        ),
        html.Div(
            children=[
                dbc.CardDeck(
                    [
                        dbc.Card(
                            children=[
                                dbc.CardHeader("LATEST DRIVER STANDINGS, TOP 10"),
                                dbc.CardBody(
                                    children=[
                                        dash_table.DataTable(
                                            columns=[
                                                {"name": i, "id": i}
                                                for i in df_homepage_drivers.columns
                                            ],
                                            data=df_homepage_drivers.to_dict("records"),
                                            page_current=0,
                                            page_size=10,
                                            style_header={
                                                "backgroundColor": "white",
                                                "fontWeight": "bold",
                                            },
                                            style_cell={
                                                "textAlign": "center",
                                                "font-size": "10px",
                                            },
                                            style_cell_conditional=[
                                                {
                                                    "if": {"column_id": "Finished"},
                                                    "textAlign": "center",
                                                }
                                            ],
                                            style_as_list_view=True,
                                        )
                                    ]
                                ),
                            ]
                        ),
                        dbc.Card(
                            children=[
                                dbc.CardHeader("LATEST CONSTRUCTOR STANDINGS"),
                                dbc.CardBody(
                                    children=[
                                        dash_table.DataTable(
                                            columns=[
                                                {"name": i, "id": i}
                                                for i in df_homepage_constructors.columns
                                            ],
                                            data=df_homepage_constructors.to_dict(
                                                "records"
                                            ),
                                            page_current=0,
                                            style_header={
                                                "backgroundColor": "white",
                                                "fontWeight": "bold",
                                            },
                                            style_cell={"textAlign": "center"},
                                            style_cell_conditional=[
                                                {
                                                    "if": {"column_id": "Finished"},
                                                    "textAlign": "center",
                                                }
                                            ],
                                            style_as_list_view=True,
                                        )
                                    ]
                                ),
                            ]
                        ),
                        dbc.Card(
                            children=[
                                dash_twitter_widget.DashTwitterWidget(
                                    id="input", value="SkySportsF1"
                                )
                            ]
                        ),
                    ]
                )
            ],
            style={"padding-left": "15px", "padding-right": "15px"},
        ),
    ]

