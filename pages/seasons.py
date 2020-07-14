import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objs as go
from data_reader import *
from app import app

season_list = list(df_seasons["year"])
season_list.sort(reverse=True)

# for get_driver_race_results_table
df_circuits_seasons = df_circuits[["circuitId", "country"]]
df_races_seasons = df_races[["year", "circuitId", "raceId"]]

# for get_driver_standings_table
df_drivers_seasons = df_drivers[
    ["driverId", "driverRef", "code", "forename", "surname"]
]
df_results_seasons = df_results[["resultId", "raceId", "driverId", "points"]]


# get country list given a year
def get_locations_by_year(year):
    merge_table = pd.merge(
        df_circuits_seasons, df_races_seasons, how="inner", on=["circuitId"]
    )
    races_country_year = merge_table[merge_table["year"] == year].sort_values(
        by=["raceId"]
    )
    season_country_list = list(races_country_year["country"])

    return season_country_list


# get full table of driver's results with points earned, round, circuit, track name
def get_driver_race_results_table(driver, year):
    merge_table = pd.merge(
        df_drivers_seasons, df_results_seasons, how="inner", on=["driverId"]
    )
    merge_with_races = pd.merge(merge_table, df_races, how="inner", on=["raceId"])
    driver_points_table_by_year = merge_with_races[
        (merge_with_races["driverRef"] == driver) & (merge_with_races["year"] == year)
    ]

    return driver_points_table_by_year


# get full table of a driver's result with current point total, WDC ranking at the time of a race, etc
def get_driver_standings_table(driver, year):
    merge_table = pd.merge(
        df_drivers_seasons, df_driver_standings, how="inner", on=["driverId"]
    )
    merge_with_races = pd.merge(merge_table, df_races, how="inner", on=["raceId"])
    merge_with_circuits = pd.merge(
        merge_with_races,
        df_circuits[["circuitId", "country"]],
        how="inner",
        on=["circuitId"],
    )
    driver_standings_points_by_year = merge_with_circuits[
        (merge_with_circuits["driverRef"] == driver)
        & (merge_with_circuits["year"] == year)
    ]

    return driver_standings_points_by_year.sort_values(by=["round"])


def generate_driver_list(year):
    merge_table = pd.merge(
        df_drivers_seasons, df_driver_standings, how="inner", on=["driverId"]
    )
    merge_with_races = pd.merge(merge_table, df_races, how="inner", on=["raceId"])
    by_year = merge_with_races[(merge_with_races["year"] == year)]
    final_round = by_year["round"].max()
    final_standings = by_year.loc[by_year["round"] == final_round]
    final_standings_sorted = final_standings.sort_values(by=["points"], ascending=False)
    return list(final_standings_sorted.driverRef.unique())


def season_graph(year, selected_drivers):

    fig = go.Figure()

    # drivers = generate_driver_list(year)
    for driver in selected_drivers:
        df_driver = get_driver_standings_table(driver, year)

        fig.add_trace(
            go.Scatter(
                x=list(df_driver["name"]),
                y=list(df_driver["points"]),
                name=df_driver.forename.unique()[0]
                + " "
                + df_driver.surname.unique()[0],
                mode="lines+markers",
            )
        )

    fig.update_layout(
        autosize=False,
        height=600,
        xaxis_title="Races",
        yaxis_title="Points",
        legend_orientation="v",
        legend=dict(x=-0.5, y=0.95),
        xaxis_tickangle=45,
        margin=dict(l=80, r=80, b=120, t=40),
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
                                html.H6("Select Year"),
                                dcc.Dropdown(
                                    id="year-dropdown",
                                    options=[
                                        {"label": i, "value": i} for i in season_list
                                    ],
                                    value=2020,
                                ),
                                html.H6("Select Driver(s)"),
                                dcc.Loading(
                                    children=[
                                        dcc.Dropdown(id="driver-dropdown", multi=True)
                                    ],
                                    type="circle",
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
                                dcc.Loading(
                                    children=[dcc.Graph(id="season-graph")],
                                    type="circle",
                                )
                            ]
                        )
                    ),
                    width=8,
                ),
            ]
        )
    ]


@app.callback(
    Output("season-graph", "figure"),
    [Input("year-dropdown", "value"), Input("driver-dropdown", "value")],
)
def update_season_Graph(year, drivers):
    if drivers is not None:
        return season_graph(year, drivers)
    else:
        raise PreventUpdate


@app.callback(Output("driver-dropdown", "options"), [Input("year-dropdown", "value")])
def update_driver_dropdown(year):
    drivers = generate_driver_list(year)
    options = []
    for driver in drivers:
        df_driver = get_driver_standings_table(driver, year)
        fullName = df_driver.forename.unique()[0] + " " + df_driver.surname.unique()[0]
        options.append({"label": fullName, "value": driver})
    return options


@app.callback(Output("driver-dropdown", "value"), [Input("year-dropdown", "value")])
def get_default_drivers(year):
    default_drivers = generate_driver_list(year)
    return default_drivers[:6]
