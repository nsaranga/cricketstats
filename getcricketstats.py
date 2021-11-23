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
# df.to_csv("./pandasoutput.csv")

# playerscompresultdf["All Scores"]=playerscompresultdf["All Scores"].astype(float)
# print(playerscompresultdf.loc["Australia", ["Chased Scores", "overschased"]])
# print(playerscompresultdf["All Scores"])
# playerscompresultdf.explode("All Scores")

# print(playerscompresultdf.sort_values(by="Boundary Given %", ascending=False)[["Boundary Given %", "Dot Ball Bowled %", "Balls Bowled"]])
# df.style.set_table_attributes("style='display:inline'").set_caption('Caption table')
print(result[["Average", "Boundary %", "Strike Rate", "Strike Rate MeanAD", "Balls Faced"]])

# print(playerscompresultdf.loc["SPD Smith","Average"])
# print(playerscompresultdf[["Boundary Given %", "Economy Rate","Economy Rate MeanAD"]])

# Plotting

# df=playerscompresultdf.loc["Australia", "All Scores"]

# playerscompresultdf.loc["Australia", "All Scores"].plot(kind="hist", fontsize=8)
# plt.scatter(x=playerscompresultdf.loc["Australia", "All Scores"], y=playerscompresultdf.loc["Australia", "All Outs"],)

# playerscompresultdf.sort_values(by="Boundary %", ascending=False)[["Boundary %", "Dot Ball %", "Balls Faced"]].plot(kind="bar", rot=15, fontsize=8, secondary_y="Balls Faced", title="Overs 1-20 in all T20s since start of 2018")
# plt.grid(axis = 'y')
plt.legend()
# plt.title("source: cricsheet.org", fontsize=10)
plt.show()
