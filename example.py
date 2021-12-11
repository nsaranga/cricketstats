""" 
getcricketstats is a script for getting team and player statistics from the cricsheet.org database for data analysis.
Copyright (C) 2021  Saranga Sudarshan

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>. 
"""

import cricketstats
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tabulate import tabulate

# This is an example script of how you can use getcricketstats

# 1. Create a search object with "getstats.search". Input arguments: players=[] or teams=[]
# For ease of use declare a list of players or teams to search stats for and then call that variable
Ozbatters = ["DA Warner", "SPD Smith",  "M Labuschagne",  "TM Head", "MS Harris", "C Green", "AT Carey", "UT Khawaja"]
# "MR Marsh", "GJ Maxwell", "MP Stoinis", "MS Wade", "JP Inglis", "UT Khawaja",
Ozbowlers = ["PJ Cummins", "JR Hazlewood", "MA Starc", "NM Lyon"]
bbl = ["Sydney Thunder", "Melbourne Renegades", "Brisbane Heat", "Sydney Sixers", "Melbourne Stars", "Perth Scorchers", "Adelaide Strikers", "Hobart Hurricanes"]
search1 = cricketstats.search(players=Ozbatters)
search4 = cricketstats.search(players=Ozbowlers)
search2 = cricketstats.search(teams=["England", "Australia", "India", "South Africa", "West Indies", "New Zealand", "Pakistan", "Sri Lanka", "Zimbabwe", "Bangladesh", "Ireland", "Afghanistan"])
search3 = cricketstats.search(teams=bbl)

# 2. Apply the "getstats()" method to the search object with the necessary arguments.
# Arguments are mostly lists, with items separated by commans.

# Required input arguments:
database = "/home/saranga/Downloads/all_json.zip" # Path of cricsheet.org's all matches json zip file.
from_date = (2015, 10, 1) # The (Year, Month, Day) from which to start search
to_date = (2021, 12, 31) # The (Year, Month, Day) from which to end search
matchtype = ["Test"] # Options: ["Test", "MDM", "ODI", "ODM", "T20", "IT20"]

# Optional Arguments:
betweenovers = [] # Restricts search to only these overs. eg. betweenovers = [1, 20]
innings = [] #  Restricts search to these innings. Options: 1, 2, 3, 4 eg. innings = [1,3]
sex = [] # Restricts search to only matches of certain sex. Options: "male", "female" eg. sex = ["female"] 
playerteams=[] # Restricts search to matches where players have played in certain teams. Options: team names eg. ["Australia", "England"]
oppositionbatters=[] # Restricts search to overs where players have bowled against certain batters. Options: batter names
oppositionbowlers=[] # Restricts search to overs where players have batted against certain bowlers Options: bowler names
oppositionteams=[] # Restricts search to matches where opposition is only certain teams. Options: team names eg. ["Australia", "England"]
venue = [] # Restricts search to matches played only at these venues Options: Cricket Grounds eg. ["Sydney Cricket Ground", "Melbourne Cricket Ground"]
event = [] # Restricts search to matches played as part of these Leagues or Tournaments Options: Name of League or Tournament eg. ["Sheffield Shield", "ICC World Cup", "Big Bash League"] 
matchresult = [] # Restricts search to matches where players or teams have these results. Options "winner", "draw","tie" eg. ["winner", "draw"]
superover = None # Restricts search to normal innings or superover innings. Options: True, False eg. To search only superovers superover = True
battingposition = [1,2] # Restricts search to stats at certain position in batting order.
bowlingposition = [] # Restricts search to stats at certain position in bowling order.

# getstats method applied on search object
search1.getstats(database, from_date, to_date, matchtype, betweenovers=betweenovers, innings=innings, sex=sex, playerteams=playerteams, oppositionbatters=oppositionbatters, oppositionbowlers=oppositionbowlers, oppositionteams=oppositionteams, venue=venue, event=event, matchresult=matchresult, superover=superover, battingposition=battingposition, bowlingposition=bowlingposition)


# 3. Print result. Output is a pandas dataframe.
# Use the follwing line to get a list of all the stats that are collected: 
# print(search1.result.columns)
# print(search2.result[["Win %", "Runs", "Runsgiven", "Wickets"]])
# print(search1.result[["Caps", "Average", "Score MeanAD", "Balls Faced", "Economy Rate", "Economy Rate MeanAD", "Balls Bowled"]])

# Data Analysis example:
# Pythagorean Expected Win Percentage: Exponent Options: Vine2016: 7.41, SenevirathneaManage2021: maximum likelihood method, 4.71 for ODI matches and 6.06 for Twenty20. The least squares method, 5.01 and 6.56 respectively for ODI and Twenty20.
#search2.result["Exp Win %"] = ((pow(search2.result["Runs"], 7.41) / (pow(search2.result["Runs"], 7.41) + pow(search2.result["Runsgiven"], 7.41)))*100)
#print(search2.result[["Win %", "Exp Win %"]])


#show option with ".loc" option for rows and columns
# 4. Plotting
# You can use the plotting methods from the pandas package or matplotlib.pyplot for plotting.
# Handy tip, use the following list compression to extract all scores in tournament: [x for sublist in dataframe for x in sublist]

print(
search1.result[["Runs", "Batting Avg", "Balls Faced"]]
#search3.result[["Average", "Score MeanAD", "Net Boundary %"]]
#search4.result[["Bowling Average","Dot Ball Bowled %", "Boundary Given %"]]
)

#search4.result.sort_values(by="Boundary Given %", ascending=False)[["Bowling Average","Dot Ball Bowled %", "Boundary Given %"]].plot(kind="bar", rot=15, fontsize=8, title="Overs 31-80 in Tests since 01/12/2020 (data: cricsheet.org)" ,secondary_y = "Boundary Given %")


#plt.hist(search2.result.at["Australia", "2nd Innings Scores"], bins=30, label="2nd Innings Scores")
#print(search1.result.sort_values(by="Balls Faced", ascending=False)[["Balls Faced", "Average", "Score MeanAD"]])
#search1.result.sort_values(by="Balls Faced", ascending=False)[["Balls Faced", "Average", "Score MeanAD"]].plot(kind="bar", rot=15, fontsize=8, title="Overs 1-30 in Tests since 2018/2019 (data: cricsheet.org)" ,secondary_y = "Balls Faced")
#plt.title("Distribution of England 1st Innings Scores in Tests at the Gabba since 2016/2017")
# plt.legend()
# plt.show()
