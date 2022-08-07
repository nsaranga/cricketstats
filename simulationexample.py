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
import mpmatchsim

# This is an example script of how you can use the match simulator in cricketstats
# If you want to import cricketstats into your own python file or jupyter notebook that sits outside, use the lines below instead of "import cricketstats". Replace "./cricketstats/" with the path of repo in your system.
"""
import os
import sys
module_path = os.path.abspath(os.path.join("./cricketstats/src/cricketstats"))
if module_path not in sys.path:
    sys.path.append(module_path)
import cricketstats 
import mpmatchsim
"""


""" 1. Create a simulation object """
sim = mpmatchsim.matchsim(simteams=["Sri Lanka", "Australia"])

""" 2. Apply the "sim()" method to the simulation object with the necessary arguments. """
# Arguments are mostly lists, with items separated by commas.

# First we can setup our arguments.
# Required input arguments:

statsdatabase="/home/saranga/Downloads/all_json.zip" # Path of cricsheet.org's all matches json zip file on your system. You can download the file at https://cricsheet.org/downloads/
statsfrom_date=(2021,7,1) # The (Year, Month, Day) from which to start search for probability values
statsto_date=(2022,12,31) # The (Year, Month, Day) from which to end search for probability values
statssex="male" # The male or female team stats to search for
statsmatchtype = "T20" # match type to simulated and search stats for Options: ["Test","ODI", "ODM", "T20",] Explanation of what these mean is found at https://cricsheet.org/downloads/
simulations=10 # Number of matches to simulate. Make sure this is divisble by the number of cores you have in your computer otherwise the module will fail.

# Optional Arguments:
inningsorder = None # This sets the order in which teams bat. Eg. ["Sri Lanka", "Australia","Sri Lanka", "Australia"] for a test match # This overrides the toss rng and sets a specific innings order.
rain=False # This sets whether there might be rain affected matches in the simulated games. This is set at constant 90/10% in favour of no rain.

matchscore = None # This sets a score or match situation from which a matches will simulated eg. matchscore = {"Innings 1":["Sri Lanka",10, 300, 90],"Innings 2":["Australia"",10, 300, 90],"Innings 3":["Sri Lanka",10, 300, 90],"Innings 4":["Australia"",0, 1, 1]}. when using this argument, inningsorder must be given to ensure the correct inningsorder is preserved

# Apply sim() method on the simulation object.
sim.sim(statsdatabase=statsdatabase, statsfrom_date=statsfrom_date,statsto_date=statsto_date, statssex=statssex,statsmatchtype=statsmatchtype,simulations=simulations, inningsorder=inningsorder, rain=rain)


# You can use the above template if you want or put all the values inside the brackets of the "sim()" method like I've done below for the object.
# sim1.sim(statsdatabase="/home/saranga/Downloads/all_json.zip", statsfrom_date=(2021,7,1),statsto_date=(2022,12,31), statssex="male",statsmatchtype="Test",simulations=10)


""" 3. Print result. Output is a pandas dataframe. """
# The output of the search is a pandas dataframe.

print(sim.results)

# You can then use all the familiar pandas methods for statistical analysis and plotting.
# Eg. sim.simresults["Winner"].value_counts(normalize=True) # This command will given you winnings percentage for each team.

# If you want to save the sim result as a csv file that you can open in excel you can use the line below.
# sim1.results.to_csv(./YOUR FILE LOCATION)
