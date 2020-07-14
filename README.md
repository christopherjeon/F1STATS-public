# Formula 1 Statistics Page

_*ATTENTION: This version of F1STATS in this repository is made with the open source version of [Dash](https://plotly.com/dash/) and [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/).*_

_*My published version of F1STATS (found [here](https://formula1stats.herokuapp.com/)) was built with [Dash Design Kit](https://plotly.com/dash/design-kit/), a commercially licensed software, which is why I have set my original repository to private. This version of the app contains the exact same graphing tools and information - the only difference are the UI components.*_

_*If you have questions regarding the difference between the open source version of Dash and Dash Enterprise, feel free to reach out!*_

This web application produces race results, driver and constructor rankings, up-to-date timetables, and comparisons of Formula 1 seasons from 1950 to the present.

Built with Python, Dash, and the Ergast Developer API (Motor Racing Data), this application will provide users an in-depth look at the numbers behind Formula 1.

Dash is an open-source Python framework that is used for building data visualization applications - combining Dash with the [Ergast Developer API](http://ergast.com/mrd/), this application offers a useful, interactive platform for old and new fans of the motorsport. 

The application will be divided into four categories/tabs:

* Home
* Seasons
* Drivers
* Constructors
* Grand Prix

## Home Tab (Coming Soon)
The Home page will display:

* Results of the most recent race (top five drivers)
* Countdown to the next Grand Prix
* Recent headlines regarding Formula 1

## Seasons Tab
The Seasons page will feature an interactive line graph that shows the trajectory of points of earned at each Grand Prix for each driver. By default, the top six drivers will be shown but the user will be given the option to add or remove drivers to this graph. 

## Drivers
The Drivers tab will display:

* Driver's bio
* Points line graph by year
* Individual race results
* List of race wins
* List of podium finishes

## Constructors
The constructors tab will display:

* Constructor standings by year
* Pie graph that shows the proportion of points earned by constructor 

## Grand Prix
The Grand Prix tab will display:

* Circuit layout
* Driver with most wins
* Driver with most pole positions
* Fastest Lap Record and record holder

## Running The Script

In order to access the single-page application, open up Terminal and make sure to change the working directory to exactly where you saved this folder:

* Create a virtual environment and activate it
* Run __pip install -r requirements.txt__
* Run __python3 index.py__ on Terminal
* Your app will be accesible on any web browswer at the address: 127.0.0.1:8050

## Built With
* [Dash](https://dash.plot.ly)
* [Ergast Developer API](http://ergast.com/mrd/)

## Contributing
Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Authors
* [Chris Jeon](https://github.com/christopherjeon)

## Acknowledgements
Thank you to Ergast for providing the necessary data. The following statistics that helped build this app can be found [here](http://ergast.com/mrd/).

