import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
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

df_races_test = df_races.rename(columns={"name": "race_name", "url": "race_url"})
season_list = list(df_seasons["year"])
season_list.sort(reverse=True)


def get_constructor_dict():
    keys = list(df_constructors["name"])
    values = list(df_constructors["constructorRef"])
    constructor_dict = dict(zip(keys, values))

    return {k: v for k, v in sorted(constructor_dict.items(), key=lambda item: item[1])}


total_constructors_list = get_constructor_dict()


def constructor_standings_by_year(year):
    merge_standings = pd.merge(
        df_constructors, df_constructor_standings, how="inner", on=["constructorId"]
    )
    merge_standings = merge_standings.rename(
        columns={"name": "constructor_name", "url": "constructor_url"}
    )

    merge_standings_races = pd.merge(
        merge_standings, df_races_test, how="inner", on=["raceId"]
    )
    merge_standings_races_filtered = merge_standings_races[
        [
            "constructor_name",
            "nationality",
            "points",
            "positionText",
            "wins",
            "year",
            "round",
        ]
    ]
    standings_all_rounds = merge_standings_races_filtered[
        (merge_standings_races_filtered["year"] == year)
    ].sort_values(by=["round", "points"], ascending=False)
    final_round = standings_all_rounds["round"].max()
    standings_final_round = standings_all_rounds[
        standings_all_rounds["round"] == final_round
    ]
    standings_final_round = standings_final_round[
        ["positionText", "constructor_name", "nationality", "points", "wins"]
    ]
    standings_final_round = standings_final_round.rename(
        columns={
            "constructor_name": "Constructor",
            "nationality": "Nationality",
            "points": "Points",
            "positionText": "Rank",
            "wins": "Wins",
            "year": "Year",
        }
    )

    return standings_final_round


def donut_chart(year):
    fig = go.Figure()
    df = constructor_standings_by_year(year)

    labels = list(df.Constructor)
    values = list(df.Points)

    fig.add_trace(go.Pie(labels=labels, values=values, hole=0.4))

    fig.update_traces(textinfo="percent")

    fig.update_layout(
        legend_orientation="v",
        annotations=[dict(text=str(year), font_size=20, showarrow=False, x=0.5, y=0.5)],
        showlegend=True,
        margin=dict(l=0, r=0),
    )

    return fig


def layout():
    return [
        dbc.Row(
            children=[
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            children=[
                                dbc.CardHeader("Standings by Year:"),
                                dcc.Dropdown(
                                    id="constructor-year-column",
                                    options=[
                                        {"label": i, "value": i} for i in season_list
                                    ],
                                    clearable=True,
                                    searchable=True,
                                    value=2020,
                                ),
                                html.Div(id="constructor-standings-card"),
                            ]
                        )
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            children=[
                                dbc.CardHeader("Point Distribution"),
                                dcc.Loading(
                                    children=[
                                        html.Div(
                                            id="pie-graph", style={"width": "600px"}
                                        )
                                    ],
                                    type="circle",
                                ),
                            ]
                        )
                    ),
                    width=8,
                ),
            ]
        )
    ]


@app.callback(
    Output("constructor-standings-card", "children"),
    [Input("constructor-year-column", "value")],
)
def get_constructor_standings(year):
    if year is not None:
        df = constructor_standings_by_year(year)
        return dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict("records"),
            page_current=0,
            style_header={"backgroundColor": "white", "fontWeight": "bold"},
            style_cell={"textAlign": "center"},
            style_cell_conditional=[
                {"if": {"column_id": "Finished"}, "textAlign": "center"}
            ],
            style_as_list_view=True,
        )
    else:
        raise PreventUpdate


@app.callback(
    Output("pie-graph", "children"), [Input("constructor-year-column", "value")]
)
def get_point_pie_chart(year):
    if year is not None:
        return dcc.Graph(figure=donut_chart(year))
    else:
        raise PreventUpdate
