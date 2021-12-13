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

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import cricketstats

# This is an example script of how you can use cricketstats
# If you want to import cricketstats into your own python file, and use thelines below instead of "import cricketstats"
"""
import os
import sys
module_path = os.path.abspath(os.path.join('cricketstats'))
if module_path not in sys.path:
    sys.path.append(module_path)
from cricketstats import cricketstats 
"""


""" 1. Create a search object """
# For ease of use first declare a list of players or teams to search stats for and then call that variable
Ozbatters = ["DA Warner", "SPD Smith",  "M Labuschagne",  "TM Head", "MS Harris", "C Green", "AT Carey", "UT Khawaja", "MR Marsh", "GJ Maxwell", "MP Stoinis", "MS Wade", "JP Inglis"]

bblteams = ["Sydney Thunder", "Melbourne Renegades", "Brisbane Heat", "Sydney Sixers", "Melbourne Stars", "Perth Scorchers", "Adelaide Strikers", "Hobart Hurricanes"]

# create a search object with "cricketstats.search" based on the inputs above. Input arguments: players=[] or teams=[] You can create multiple objects at the same time.
search1 = cricketstats.search(players=Ozbatters)

# You can see below another search object setup for BBL teams. Just uncomment the line to use it.
# search2 = cricketstats.search(teams=bblteams)

""" 2. Apply the "stats()" method to the search object with the necessary arguments. """
# Arguments are mostly lists, with items separated by commans.

# First we can setup our arguments.
# Required input arguments:
database = "/home/saranga/Downloads/all_json.zip" # Path of cricsheet.org's all matches json zip file on your system. You can download the file at https://cricsheet.org/downloads/
from_date = (2018, 10, 1) # The (Year, Month, Day) from which to start search
to_date = (2021, 12, 31) # The (Year, Month, Day) from which to end search
matchtype = ["Test"] # Options: ["Test", "MDM", "ODI", "ODM", "T20", "IT20"] Explanation of what these mean is found at https://cricsheet.org/downloads/

# Optional Arguments:
betweenovers = [] # Search only these overs. eg. betweenovers = [1, 20]
innings = [] #  Search these innings. Options: 1, 2, 3, 4 eg. innings = [1,3]
sex = [] # Search only matches of certain sex. Options: "male", "female" eg. sex = ["female"] 
playerteams=[] # Search matches where players have played in certain teams. Options: team names eg. ["Australia", "England"]
fielders = [] # Search bowling stats involves these fielders.
oppositionbatters=[] # Search overs where players have bowled against certain batters. Options: batter names
oppositionbowlers=[] # Search overs where players have batted against certain bowlers Options: bowler names
oppositionteams=[] # Search matches where opposition is only certain teams. Options: team names eg. ["Australia", "England"]
venue = [] # Search matches played only at these venues Options: Cricket Grounds eg. ["Sydney Cricket Ground", "Melbourne Cricket Ground", ""Brisbane Cricket Ground, Woolloongabba""]
event = [] # Search matches played as part of these Leagues or Tournaments Options: Name of League or Tournament eg. ["Sheffield Shield", "ICC World Cup", "Big Bash League"] 
matchresult = [] # Search matches where players or teams have these results. Options "winner", "draw","tie" eg. ["winner", "draw"]
superover = None # Search normal innings or superover innings. Options: True, False eg. To search only superovers superover = True
battingposition = [] # Search stats at certain position in batting order.
bowlingposition = [] # Search stats at certain position in bowling order.

# Apply stats() method applied on search object. You have to apply the method to every search object if you want the script to actually do teh search.
search1.stats(database, from_date, to_date, matchtype, betweenovers=betweenovers, innings=innings, sex=sex, playerteams=playerteams, oppositionbatters=oppositionbatters, oppositionbowlers=oppositionbowlers, oppositionteams=oppositionteams, venue=venue, event=event, matchresult=matchresult, superover=superover, battingposition=battingposition, bowlingposition=bowlingposition, fielders=fielders)

# You can use the above template if you want or put all the values inside the brackets of the "stats()" method like I've done below for the search2 object.
# search2.stats(database="/home/saranga/Downloads/all_json.zip", from_date=(2018, 10, 1), to_date=(2021, 12, 31), matchtype=[T20], betweenovers=[], innings=[], sex=[], playerteams=[], oppositionbatters=[], oppositionbowlers=[], oppositionteams=[], venue=[], event=["Big Bash League"], matchresult=[], superover=None, battingposition=[], bowlingposition=[], fielders=[])


""" 3. Print result. Output is a pandas dataframe. """
# print(search1.result.columns) # Use this line to print all the stats that are recorded and can be displayed.

# The line below prints the columns of the stats. There are way more stats than just the four used in the line below.
print(search1.result[["Games", "Batting Avg", "Score MeanAD", "Balls Faced"]]) 

# If you want to save the search result as a csv file that you can open in excel you can use the line below.
# search1.result.to_csv(./YOUR FILE LOCATION)

""" 4. Plotting """
# You can use the plotting methods from the pandas package or matplotlib.pyplot for plotting.
# Handy tip, use the following list compression to extract all scores from multiple players or teams: [x for sublist in dataframe for x in sublist]

#search1.result.sort_values(by="Balls Faced", ascending=False)[["Balls Faced", "Average", "Score MeanAD"]].plot(kind="bar", rot=15, fontsize=8, title="Tests since 2018/2019 (data: cricsheet.org)", secondary_y = "Balls Faced")
# plt.legend()
# plt.show()


""" 5. Bonus Data Analysis Example """
# Pythagorean Expected Win Percentage for a team: This is a formula for calculating expected win percentage given runs scored and conceded by team
# Formula: Expected Win % = (Runs scored)^exponent / ((Runs scored)^exponent + (Runs conceded)^exponent)
# Exponent Options: Vine2016: 7.41, SenevirathneaManage2021: maximum likelihood method, 4.71 for ODI matches and 6.06 for Twenty20. The least squares method, 5.01 and 6.56 respectively for ODI and Twenty20.
#search2.result["Exp Win %"] = ((pow(search2.result["Runs"], 7.41) / (pow(search2.result["Runs"], 7.41) + pow(search2.result["Runsgiven"], 7.41)))*100)
#print(search2.result[["Win %", "Exp Win %"]])