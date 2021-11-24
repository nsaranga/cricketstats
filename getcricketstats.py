# getcricketstats is a script for getting team and player statistics from the cricsheet.org database for data analysis.
# Copyright (C) 2021  Saranga Sudarshan
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.

import getstats
import matplotlib.pyplot as plt
import pandas as pd

Ozbowlers = ["PJ Cummins", "JR Hazlewood", "MA Starc", "JA Richardson", "A Zampa", "AC Agar", "NT Ellis", "MP Stoinis",
             "MR Marsh", "MJ Swepson", "MG Neser", "NM Lyon", "CD Green"]
Ozbatters = ["DA Warner", "SPD Smith", "MR Marsh", "GJ Maxwell", "MP Stoinis", "MS Wade", "JP Inglis", "M Labuschagne",
             "UT Khawaja", "TM Head", "MS Harris", "CD Green", "TD Paine"]
result = getstats.getstats("/home/saranga/Documents/cricketstatsproject/data/all/", (2021, 4, 1),
                           (2021, 12, 1), betweenovers=[1, 60], players=Ozbatters, matchtype=["MDM", "Test"])

# getstats input arguments.  sex=[], teams=[], opposition=[], venue=[], event=[], matchtype=[], matchresult=""
# getstats output -> pandas dataframe

# Stats Comparison
print(result[["Average", "Boundary %", "Strike Rate",
      "Strike Rate MeanAD", "Balls Faced"]])


# Plotting
# Decide on what plotting package to use here.

# plt.scatter(x=playerscompresultdf.loc["Australia", "All Scores"], y=playerscompresultdf.loc["Australia", "All Outs"],)
# playerscompresultdf.sort_values(by="Boundary %", ascending=False)[["Boundary %", "Dot Ball %", "Balls Faced"]].plot(kind="bar", rot=15, fontsize=8, secondary_y="Balls Faced", title="Overs 1-20 in all T20s since start of 2018")

# plt.grid(axis = 'y')
# plt.legend()
# plt.title("source: cricsheet.org", fontsize=10)
# plt.show()


# How will program work
# 1 Wrapper CLI interface -> user inputs query.
# 2 Query -> Call query class and create object for query. attributes will be the paramters?
# 3 Query Object calls/uses getstats func.
# 4 Class init playerstats ={} and teamstats={}.
# 5 get stats runs -> raw stats.
# 6 pass raw stats to stats process that gets derived metrics.? YES this way this I can change based on what I collect?
# display final stats query object as pandas dataframe
# ask if I want plot of dataframe?
# data structures, if derived stats are processed after main func, then allplayerstats, and allteams stats has to be defiend in its own class.
# also there has to be function that does reverse look up, say looks up at all teams/bowlers/batters/fielders, then feeds that list back into getstats function. that will given me top 10 lists and such: basically function that records all bowlers, batters or fielders, in given parameters then inputs them into getstatsfunc.with same parameters.
# also have field for saving the transposed dataframe as csv?
# another thing to do is have the outputs stats set as variables of the class, and then edited by the functions under it. YES THIS MAKES SENSE.
# have like a "stats process function"
# woudl it be easier to load json files as data frame then scrape data that way?
# I have to make the data from json load an object, an dcreate methods for that object
# okay but json.load actually creats a dict object. so that has to be done before and outside the get stats methods.
# the wrapper should also insert the correct titles for graphs and overs tsuff depending on inputs.
# add importing of players csv as dataframe to search for players.
# add opposing bowler and batter checks
# requried arguments should be database what else, over intervals can be optional, if false just look at all overs. do this for time as well?
# have to do innings specific check as well for tests.and draw/tie checks. also recording scores for 3rd and 4th innings.
# do ingestion of all files into on big list, then loop through.
