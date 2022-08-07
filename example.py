""" 
cricketstats is a script for getting team and player statistics from the cricsheet.org database for data analysis.
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
# If you want to import cricketstats into your own python file or jupyter notebook that sits outside, use the lines below instead of "import cricketstats". Replace "./cricketstats/" with the path of repo in your system.
"""
import os
import sys
module_path = os.path.abspath(os.path.join("./cricketstats/src/cricketstats"))
if module_path not in sys.path:
    sys.path.append(module_path)
import cricketstats
"""


""" 1. Create a search object """
# For ease of use first declare a list of players or teams to search stats for and then call that variable
Ozbatters = ["DA Warner", "SPD Smith",  "M Labuschagne",  "TM Head", "MS Harris", "C Green", "AT Carey", "UT Khawaja", "MR Marsh", "GJ Maxwell", "MP Stoinis", "MS Wade", "JP Inglis"]

bblteams = ["Sydney Thunder", "Melbourne Renegades", "Brisbane Heat", "Sydney Sixers", "Melbourne Stars", "Perth Scorchers", "Adelaide Strikers", "Hobart Hurricanes"]

# create a search object with "cricketstats.search" based on the inputs above. Input arguments: players=[] or teams=[] You can create multiple objects at the same time.
search1 = cricketstats.search(players=Ozbatters)

# If you want to find stats for all players ot teams use the "allplayers=True" or "allteams=True" option in the class.
# search2 = cricketstats.search(allplayers=True)

# You can see below another search object setup for BBL teams. Just uncomment the line to use it.
# search3 = cricketstats.search(teams=bblteams)

""" 2. Apply the "stats()" method to the search object with the necessary arguments. """
# Arguments are mostly lists, with items separated by commas.

# First we can setup our arguments.
# Required input arguments:
database = "/home/saranga/Downloads/all_json.zip" # Path of cricsheet.org's all matches json zip file on your system. You can download the file at https://cricsheet.org/downloads/
from_date = (2018, 10, 1) # The (Year, Month, Day) from which to start search
to_date = (2021, 12, 31) # The (Year, Month, Day) from which to end search
matchtype = ["Test"] # Options: ["Test", "MDM", "ODI", "ODM", "T20", "IT20"] Explanation of what these mean is found at https://cricsheet.org/downloads/

# Optional Arguments:
# First we can set overs and innings related arguments:
betweenovers=[] # Search only these overs. eg. betweenovers = [1, 20]. Or if you only want to search for powerplays that are mandatory and option input "powerplays" eg. betweenovers =["powerplays"]
innings=[] # Search these innings. Options: 1, 2, 3, 4 eg. innings = [1,3]
fielders=[] # Search bowling stats involves these fielders.
oppositionbatters=[] # Search overs where players have bowled against certain batters. Options: batter names. You can also put in a list of batters by handedness. eg. oppositionbatters=["Left hand", "Right Hand"]
oppositionbowlers=[] # Search overs where players have batted against certain bowlers Options: bowler names You can also put in list of bowlers by type, eg. oppositionbowlers=["Right arm pace","Left arm pace","Right arm Off break","Right arm Leg break","Left arm orthodox","Left arm wrist spin"]
superover=None # Search normal innings or superover innings. Options: True, False eg. superover=True
battingposition=[] # Search stats at certain position in batting order. eg. battingposition=[1,2,3]
bowlingposition=[] # Search stats at certain position in bowling order. eg. bowlingposition=[1,2]

# Second we have match related arguments
sex=[] # Search only matches of certain sex. Options: "male", "female" eg. sex = ["female"] 
playerteams=[] # Search matches where players have played in certain teams. Options: team names eg. playerteams=["Australia", "England"]
teammates=[] # Search matches where certain teammates play. For this to work playerteams must be populated.
oppositionteams=[] # Search matches where opposition is only certain teams. Options: team names eg. oppositionteams=["India", "England"]
venue=[] # Search matches played only at these venues Options: Cricket Grounds eg. venue=["Sydney Cricket Ground", "Melbourne Cricket Ground", ""Brisbane Cricket Ground, Woolloongabba""]
teamtype=[] # Search only for particualr type of teams. eg. "international", "club".
event=[] # Search matches played as part of these Leagues or Tournaments Options: Name of League or Tournament eg. event=["Sheffield Shield", "ICC World Cup", "Big Bash League"] 
matchresult=None # Search matches where players or teams have these results. When looking at players, this option **must** be used with at one team in playersteams variable. Options either "won" or "loss" or "draw" or "tie" eg. matchresult="won"
sumstats=False # When switched to True, it adds an "all players" or "all teams" row at end of result that sums all players or teams stats that are searched for.

# Apply stats() method applied on search object. You have to apply the method to every search object if you want the script to actually do teh search.
search1.stats(database, from_date, to_date, matchtype, betweenovers=betweenovers, innings=innings, sex=sex, playersteams=playerteams, oppositionbatters=oppositionbatters, oppositionbowlers=oppositionbowlers, oppositionteams=oppositionteams, venue=venue, event=event, matchresult=matchresult, superover=superover, battingposition=battingposition, bowlingposition=bowlingposition, fielders=fielders, sumstats=sumstats)

# You can use the above template if you want or put all the values inside the brackets of the "stats()" method like I've done below for the search2 object.
# search2.stats(database="/home/saranga/Downloads/all_json.zip", from_date=(2018, 10, 1), to_date=(2021, 12, 31), matchtype=["T20"], betweenovers=[], innings=[], sex=[], playersteams=[], oppositionbatters=[], oppositionbowlers=[], oppositionteams=[], venue=[], event=["Big Bash League"], matchresult=[], superover=None, battingposition=[], bowlingposition=[], fielders=[], sumstats=False)


""" 3. Print result. Output is a pandas dataframe. """
# The output of the search is a pandas dataframe.
# print(search1.result.columns) # Use this line to print all the stats that are recorded and can be displayed.

# The line below prints the columns of the stats. There are way more stats than just the four used in the line below.
print(search1.result[["Games", "Batting Avg", "Score MeanAD", "Balls Faced"]]) 

# To get the long form data of each innings the players/team have played use the line below. This is best displayed as dataframe in jupyter notebook.
print(search1.inningsresult)

# If you want to save the search result as a csv file that you can open in excel you can use the line below.
# search1.result.to_csv(./YOUR FILE LOCATION)

""" 4. Plotting """
# You can use the plotting methods from the pandas package or matplotlib.pyplot for plotting.
# Handy tip, use the following list compression to extract all scores from multiple players or teams: [x for sublist in dataframe for x in sublist]

#search1.result.sort_values(by="Balls Faced", ascending=False)[["Balls Faced", "Batting Avg", "Score MeanAD"]].plot(kind="bar", rot=15, fontsize=8, title="Tests since 2018/2019 (data: cricsheet.org)", secondary_y = "Balls Faced")
# plt.legend()
# plt.show()


""" 5. Bonus Data Analysis Example """
# Pythagorean Expected Win Percentage for a team: This is a formula for calculating expected win percentage given runs scored and conceded by team
# Formula: Expected Win % = (Runs scored)^exponent / ((Runs scored)^exponent + (Runs conceded)^exponent)
# Exponent Options: Vine2016: 7.41, SenevirathneaManage2021: maximum likelihood method, 4.71 for ODI matches and 6.06 for Twenty20. The least squares method, 5.01 and 6.56 respectively for ODI and Twenty20.
#search2.result["Exp Win %"] = ((pow(search2.result["Runs"], 7.41) / (pow(search2.result["Runs"], 7.41) + pow(search2.result["Runsgiven"], 7.41)))*100)
#print(search2.result[["Win %", "Exp Win %"]])