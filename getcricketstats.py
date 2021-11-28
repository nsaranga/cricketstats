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
Indbatters = ["R Ashwin"]

# How to use this script

# 1. Create a search object. Input arguments: players=[] or teams=[]
search1 = getstats.search(players=Ozbatters)

# 2. Apply the "getstats()" method to the search object. getstats input arguments:  sex=[], opposition=[], venue=[], event=[], matchtype=["Test", "MDM", "ODI", "ODM", "T20", "IT20"], matchresult=["winner", "draw","tie"], innings = []
search1.getstats("/home/saranga/Downloads/all_json.zip", (2018, 1, 1), (2021, 12, 1), betweenovers=[], matchtype=["Test"])

# 3. Print result of the search object. getstats output is pandas dataframe
# Use the follwing line to get a list of all the stats that are collected: print(search1.result.columns)
print(search1.result[["Average", "Score MeanAD", "Strike Rate", "Strike Rate MeanAD"]])


# 4. Plotting
# Decide on what plotting package to use here.

# plt.scatter(x=search1.result.loc["Australia", "All Scores"], y=search1.result.loc["Australia", "All Outs"],)
search1.result.sort_values(by="Average", ascending=False)[["Average", "Score MeanAD", "Strike Rate", "Strike Rate MeanAD",]].plot(kind="bar", rot=15, fontsize=8, title="Test since start of 2018")

# plt.grid(axis = 'y')
plt.legend()
# plt.title("Average vs Strike Rate" data: cricsheet.org", fontsize=10)
plt.show()
