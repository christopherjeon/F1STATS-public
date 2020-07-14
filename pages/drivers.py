import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objs as go
import requests
import json
import wikipedia
from bs4 import BeautifulSoup
import re
from urllib.request import urlopen
import collections
from app import app
from data_reader import *
from pages.seasons import get_driver_standings_table

season_list = list(df_seasons["year"])
season_list.sort(reverse=True)

df_circuits_seasons = df_circuits[["circuitId", "country"]]
df_races_seasons = df_races[["year", "circuitId", "raceId"]]
df_drivers_seasons = df_drivers[
    ["driverId", "driverRef", "code", "forename", "surname"]
]
df_results_seasons = df_results[["resultId", "raceId", "driverId", "points"]]


def get_driver_dict():
    keys = list(df_drivers["forename"] + " " + df_drivers["surname"])
    values = list(df_drivers["driverRef"])
    driver_dict = dict(zip(keys, values))

    return {k: v for k, v in sorted(driver_dict.items(), key=lambda item: item[1])}


total_drivers_list = get_driver_dict()


def get_driver_photo(driver_name):
    driver_id = total_drivers_list[driver_name]
    URL_driver_photo = "http://ergast.com/api/f1/drivers/%s.json" % driver_id
    data_driver_photo = requests.get(url=URL_driver_photo).json()

    for driver in data_driver_photo["MRData"]["DriverTable"]["Drivers"]:
        driver_wiki_link = driver["url"]

    html = urlopen(driver_wiki_link)
    bs = BeautifulSoup(html, "html.parser")
    images = bs.find_all("img", {"src": re.compile(".jpg")})

    try:
        image = images[0]["src"]
    except IndexError:
        image = "null"

    image_link = image[2:]
    image_link = "https://" + image_link

    return image_link


def get_driver_results_list(driver_name):
    driver_id = total_drivers_list[driver_name]
    merge_table = pd.merge(
        df_drivers_seasons, df_results_seasons, how="inner", on=["driverId"]
    )
    merge_with_races = pd.merge(merge_table, df_races, how="inner", on=["raceId"])
    merge_with_results = pd.merge(
        merge_with_races,
        df_results[["resultId", "constructorId", "grid", "position", "fastestLapTime"]],
        how="inner",
        on=["resultId"],
    )
    merge_with_constructors = pd.merge(
        merge_with_results,
        df_constructors[["constructorId", "name"]],
        how="inner",
        on=["constructorId"],
    )
    driver_points_table = merge_with_constructors[
        (merge_with_constructors["driverRef"] == driver_id)
    ]
    driver_points_table.position = driver_points_table.position.replace({r"\N": "DNF"})
    driver_points_table.fastestLapTime = driver_points_table.fastestLapTime.replace(
        {r"\N": r"N/A"}
    )
    reorder = (
        driver_points_table.rename(
            columns={
                "name_x": "Event",
                "name_y": "Constructor",
                "year": "Year",
                "grid": "Qualifying",
                "position": "Finished",
                "fastestLapTime": "Fastest Lap Time",
            }
        )
        .sort_values(by=["resultId"])
        .iloc[::-1]
    )
    results = reorder[
        ["Event", "Year", "Qualifying", "Finished", "Fastest Lap Time", "Constructor"]
    ]

    return results


def driver_information(driver_name):
    driver_id = total_drivers_list[driver_name]
    df_profile = df_drivers[
        ["driverRef", "number", "forename", "surname", "dob", "nationality"]
    ]
    select_driver = df_profile[(df_profile["driverRef"]) == driver_id]
    full_name = (
        select_driver.forename.unique()[0] + " " + select_driver.surname.unique()[0]
    )
    date_of_birth = select_driver.dob.unique()[0]
    nationality = select_driver.nationality.unique()[0]

    results_table = get_driver_results_list(driver_name)
    num_wins = (results_table.Finished == "1").sum()
    num_podiums = (
        (results_table.Finished == "1").sum()
        + (results_table.Finished == "2").sum()
        + (results_table.Finished == "3").sum()
    )
    num_poles = (results_table.Qualifying == 1).sum()
    seasons_active = list(results_table["Year"].unique())
    num_szns_active = len(seasons_active)

    return html.Div(
        [
            html.H4(full_name),
            html.P("Date of Birth: " + date_of_birth),
            html.P("Nationality: " + nationality),
            html.P("Race Wins: " + str(num_wins)),
            html.P("Podium Finishes: " + str(num_podiums)),
            html.P("Pole Positions: " + str(num_poles)),
            html.P("Seasons: " + str(num_szns_active)),
        ]
    )


def wins_table(driver_name):
    results_table = get_driver_results_list(driver_name)
    first_places = results_table[(results_table["Finished"] == "1")].sort_values(
        by=["Year"], ascending=False
    )
    first_place_table = first_places[["Event", "Year", "Constructor"]]

    return first_place_table


def podiums_table(driver_name):
    results = get_driver_results_list(driver_name)
    podium_places = results[
        (results["Finished"] == "1")
        | (results["Finished"] == "2")
        | (results["Finished"] == "3")
    ].sort_values(by=["Year"], ascending=False)
    podium_place_table = podium_places[["Event", "Year", "Finished", "Constructor"]]

    return podium_place_table


def season_line_graph(driver_name, year):
    driver_id = total_drivers_list[driver_name]
    fig = go.Figure()

    df_driver = get_driver_standings_table(driver_id, year)

    fig.add_trace(
        go.Scatter(
            x=list(df_driver["name"]), y=list(df_driver["points"]), mode="lines+markers"
        )
    )

    fig.update_layout(
        autosize=False,
        xaxis_title="Races",
        yaxis_title="Points",
        xaxis_tickangle=45,
        margin=dict(l=80, r=20, b=120, t=40),
    )

    return fig


def drivers_active_years(driver_name):
    results_table = get_driver_results_list(driver_name)
    years_active = results_table["Year"].unique().tolist()

    return years_active


def layout():
    return [
        dbc.Row(
            children=[
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            children=[
                                dbc.CardHeader("Select Driver Here"),
                                dcc.Dropdown(
                                    id="driver-column",
                                    options=[
                                        {"label": i, "value": i}
                                        for i in list(total_drivers_list.keys())
                                    ],
                                    clearable=True,
                                    searchable=True,
                                    value="Lewis Hamilton",
                                ),
                                dbc.Row(
                                    children=[
                                        html.Img(
                                            id="driver-name-card",
                                            style={
                                                "padding-top": "10%",
                                                "height": "300px",
                                                "width": "160px",
                                                "padding-left": "5%",
                                            },
                                        ),
                                        html.Div(
                                            id="profile-about-section",
                                            style={
                                                "padding-left": "5%",
                                                "padding-top": "10%",
                                            },
                                        ),
                                    ]
                                ),
                            ]
                        )
                    ),
                    width=4,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            children=[
                                dbc.CardHeader("# of Points After Each Race"),
                                dcc.Dropdown(id="year-dropdown-2"),
                                dcc.Loading(
                                    children=[
                                        dcc.Graph(
                                            id="season-line-graph",
                                            style={"width": "720px"},
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
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            children=[
                                dbc.CardHeader("Driver Background (from Wikipedia)"),
                                dcc.Loading(
                                    children=[
                                        html.P(
                                            id="driver-about-card",
                                            style={"margin": "5 10px"},
                                        )
                                    ],
                                    type="circle",
                                ),
                            ]
                        )
                    ),
                    width=5,
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody(
                            children=[
                                dbc.CardHeader("Individual Race Results"),
                                html.Div(id="individual-result-table"),
                            ]
                        )
                    ),
                    width=7,
                ),
            ]
        ),
        html.Div(
            children=[
                dbc.CardDeck(
                    [
                        dbc.Card(
                            dbc.CardBody(
                                children=[
                                    dbc.CardHeader("List of Race Wins"),
                                    html.Div(
                                        id="wins-result-table", style={"width": "500px"}
                                    ),
                                ]
                            )
                        ),
                        dbc.Card(
                            dbc.CardBody(
                                children=[
                                    dbc.CardHeader("List of Podium Finishes"),
                                    html.Div(id="podiums-result-table"),
                                ]
                            )
                        ),
                    ]
                )
            ],
            style={"padding-left": "15px", "padding-right": "15px"},
        ),
    ]


@app.callback(
    Output("driver-about-card", "children"), [Input("driver-column", "value")]
)
def get_driver_about_card(name):
    if name is not None:
        return wikipedia.summary(name, sentences=5)
    else:
        raise PreventUpdate


@app.callback(Output("driver-name-card", "src"), [Input("driver-column", "value")])
def get_driver_name_card(name):
    if name is not None:
        return get_driver_photo(name)
    else:
        raise PreventUpdate


@app.callback(
    Output("individual-result-table", "children"), [Input("driver-column", "value")]
)
def get_individual_race_results_card(name):
    if name is not None:
        df = get_driver_results_list(name)
        df.Year = df.Year.astype(str)
        df.Qualifying = df.Qualifying.astype(str)
        return dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict("records"),
            page_current=0,
            page_size=10,
            filter_action="native",
        )
    else:
        raise PreventUpdate


@app.callback(
    Output("profile-about-section", "children"), [Input("driver-column", "value")]
)
def get_driver_profile_section(name):
    if name is not None:
        return driver_information(name)
    else:
        raise PreventUpdate


@app.callback(
    Output("wins-result-table", "children"), [Input("driver-column", "value")]
)
def get_wins_table(name):
    if name is not None:
        df = wins_table(name)
        return dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict("records"),
            page_current=0,
            page_size=10,
            style_header={"backgroundColor": "white", "fontWeight": "bold"},
            style_cell={"textAlign": "center"},
            style_as_list_view=True,
        )
    else:
        raise PreventUpdate


@app.callback(
    Output("podiums-result-table", "children"), [Input("driver-column", "value")]
)
def get_podiums_table(name):
    if name is not None:
        df = podiums_table(name)
        return dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict("records"),
            page_current=0,
            page_size=10,
            style_header={"backgroundColor": "white", "fontWeight": "bold"},
            style_cell={"textAlign": "center"},
            style_cell_conditional=[
                {"if": {"column_id": "Finished"}, "textAlign": "center"}
            ],
            style_as_list_view=True,
        )
    else:
        raise PreventUpdate


@app.callback(Output("year-dropdown-2", "options"), [Input("driver-column", "value")])
def update_driver_years(name):
    years = drivers_active_years(name)
    years.sort(reverse=True)
    if name is not None:
        years = [{"label": i, "value": i} for i in years]
        return years
    else:
        raise PreventUpdate


@app.callback(
    Output("season-line-graph", "figure"),
    [Input("driver-column", "value"), Input("year-dropdown-2", "value")],
)
def get_season_line_graph(name, year):
    if name is not None:
        return season_line_graph(name, year)
    else:
        raise PreventUpdate


@app.callback(Output("year-dropdown-2", "value"), [Input("driver-column", "value")])
def get_recent_year(name):
    years = drivers_active_years(name)
    years.sort(reverse=True)
    return years[0]
