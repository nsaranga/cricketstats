# get-cricket-stats is a script for getting team and player statistics from the cricsheet.org database for data analysis.
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

# How to use this script

# 1. Create a search object. Input arguments: players=[] or teams=[]
# For ease of use declare a list of players or teams to search stats for and then call that variable
Ozbatters = ["DA Warner", "SPD Smith", "MR Marsh", "GJ Maxwell", "MP Stoinis", "MS Wade", "JP Inglis", "M Labuschagne",
             "UT Khawaja", "TM Head", "MS Harris", "CD Green"]

search1 = getstats.search(players=Ozbatters)

# 2. Apply the "getstats()" method to the search object which is "search1" in this case with the necessary arguments.
# If optional arguments are not given then all matches compatible with that argument will be searched

# Required input arguments:
database = "C:/Users/mane/Downloads/all_json.zip" # Path of cricsheet.org's all matches json zip file.
from_date = (2018, 1, 1) # The (Year, Month, Day) from which to start search
to_date = (2021, 12, 1) # The (Year, Month, Day) from which to end search
matchtype = ["Test", "MDM", "ODI", "ODM", "T20", "IT20"]

# Optional Arguments:
sex = ["male", "female"]
opposition = [] 
venue = []
event = []
matchresult=["winner", "draw","tie"]
innings = []

search1.getstats(database, from_date, to_date, matchtype)

# 3. Print result. Output is a pandas dataframe.
# Use the follwing line to get a list of all the stats that are collected: print(search1.result.columns)
print(search1.result[["Caps", "Won", "Average", "Score MeanAD", "Strike Rate", "Strike Rate MeanAD"]])


# 4. Plotting
# You can use the plotting methods from the pandas package for simple plots.
search1.result.sort_values(by="Average", ascending=False)[["Average", "Score MeanAD", "Strike Rate", "Strike Rate MeanAD"]].plot(kind="bar", rot=15, fontsize=8, title="Test since start of 2018 (data: cricsheet.org)")
plt.grid(axis = 'y')
plt.legend()
plt.show()
