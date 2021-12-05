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

# How to use this script

# 1. Create a search object. Input arguments: players=[] or teams=[]
# For ease of use declare a list of players or teams to search stats for and then call that variable
Ozbatters = ["DA Warner", "SPD Smith", "MR Marsh", "GJ Maxwell", "MP Stoinis", "MS Wade", "JP Inglis", "M Labuschagne",
             "UT Khawaja", "TM Head", "MS Harris", "CD Green"]
bbl = ["Sydney Thunder", "Melbourne Renegades", "Brisbane Heat", "Sydney Sixers", "Melbourne Stars", "Perth Scorchers", "Adelaide Strikers", "Hobart Hurricanes"]
search1 = getstats.search(players=Ozbatters, teams=bbl)

# 2. Apply the "getstats()" method to the search object which is "search1" in this case with the necessary arguments.
# Arguments are mostly lists, with items separated by commans.

# Required input arguments:
database = "/home/saranga/Downloads/all_json.zip" # Path of cricsheet.org's all matches json zip file.
from_date = (2018, 1, 1) # The (Year, Month, Day) from which to start search
to_date = (2021, 12, 31) # The (Year, Month, Day) from which to end search
matchtype = ["T20"] # Options: ["Test", "MDM", "ODI", "ODM", "T20", "IT20"]

# I have ot put list off all possible options for event at least.
# Optional Arguments:
betweenovers = [1,20]
innings = [] # Options: 1, 2, 3, 4 eg. innings = [1,3]
sex = [] # Options: "male", "female" eg. sex = ["female"] 
playerteams=[] # Options: team names eg. ["Australia", "England"]
oppositionbatters=[] # Options: batter names
oppositionbowlers=[] # Options: bowler names
oppositionteams=[] # Options: team names eg. ["Australia", "England"]
venue = [] # Options: Cricket Grounds eg. ["Sydney Cricket Ground", "Melbourne Cricket Ground"]
event = ["Big Bash League"] # Options: Name of League or Tournament eg. ["Sheffield Shield", "ICC World Cup"] 
matchresult = [] # Options "winner", "draw","tie" eg. ["winner", "draw"]

# getstats method applied on search object
search1.getstats(database, from_date, to_date, matchtype, betweenovers=betweenovers, innings=innings, sex=sex, playerteams=playerteams, oppositionbatters=oppositionbatters, oppositionbowlers=oppositionbowlers, oppositionteams=oppositionteams, venue=venue, event=event, matchresult=matchresult)

# 3. Print result. Output is a pandas dataframe.
# Use the follwing line to get a list of all the stats that are collected: 
# print(search1.result.columns)
print(search1.result[["Boundary %", "Boundary Given %", "Net Boundary %"]])


#shoudl option with ".loc" option for rows and columns
# 4. Plotting
# You can use the plotting methods from the pandas package for simple plots.
search1.result.sort_values(by="Average", ascending=False)[["Average", "Score MeanAD", "Strike Rate", "Strike Rate MeanAD"]].plot(kind="bar", rot=15, fontsize=8, title="Test since start of 2018 (data: cricsheet.org)")
plt.grid(axis = 'y')
plt.legend()
plt.show()
