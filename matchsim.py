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

import os
import sys
import pandas as pd
import numpy as np

module_path = os.path.abspath(os.path.join("./cricketstats/"))
if module_path not in sys.path:
    sys.path.append(module_path)
from cricketstats import cricketstats


# Monte Carlo simulation of each ball in team's innings.
# input parameters: score, wicket, extras? but maybe make these each spearate random choices for a ball. yes
# simulations should run until 10 wickets are taken. or declare?
# Indexing to venue/country?
# for first attempt include batting team propabilities only, leave out bowling.

# TODO Get p-values for first or second innings separately.
# TODO Get p-values for toss choice.
# TODO Add player statistics into teams?

class matchsim:
    def __init__(self,simteams=None) -> None:
        self.simteams = simteams
        self.results = None

    def sim(self, statsdatabase, statsfrom_date, statsto_date, statssex, statsmatchtype, simulations):

        # search stats for p-values
        simteamsstats = cricketstats.search(teams=self.simteams)
        simteamsstats.stats(database=statsdatabase, from_date=statsfrom_date, to_date=statsto_date, matchtype=[statsmatchtype], betweenovers=[], innings=[], sex=[statssex], playersteams=[], oppositionbatters=[], oppositionbowlers=[], oppositionteams=[], venue=[], event=[], matchresult=[], superover=None, battingposition=[], bowlingposition=[], fielders=[], sumstats=False)

        # setup p-values for simulations
        simstats = {}
        for eachteam in self.simteams:
            simstats[eachteam]={}
            simstats[eachteam]["Batpvalues"] = simteamsstats.ballresult[["Runs Scored"]].loc[simteamsstats.ballresult["Batting Team"]==eachteam].value_counts(normalize=True,sort=False)
            simstats[eachteam]["Outspvalues"] = simteamsstats.ballresult[['Out/NotOut']].loc[simteamsstats.ballresult["Batting Team"]==eachteam].value_counts(normalize=True,sort=False)


        # match generator
        
        rng = np.random.default_rng()

        matchresults={"Innings 1 Team":[], "Innings 1 Score":[],"Innings 1 Wickets":[],"Innings 2 Team":[], "Innings 2 Score":[],"Innings 2 Wickets":[],"Winner":[]}
        
        for thismatch in range(simulations):

            # toss rng to decide inningsorder
            inningsorder = rng.choice(self.simteams, p=[0.5,0.5],size=2, replace=False, shuffle=False).tolist()

            # innings generator
            for thisinnings in inningsorder:  
                inningsscore = 0
                inningswickets = 0
                inningsballs = 0

                inningslenth = 0
                if statsmatchtype=="T20":
                    inningslenth=120
                if statsmatchtype=="ODI" or statsmatchtype=="ODM":
                    inningslenth=300
                    
                # ball outcome generator
                for thisball in range(inningslenth):
                    if inningswickets == 10:
                        break
                    wicket = rng.choice(simstats[thisinnings]["Outspvalues"].index, p=simstats[thisinnings]["Outspvalues"].values, shuffle=False)
                    if wicket[0]=="Out":
                        inningswickets += 1
                    if inningswickets == 10:
                        break
                    if inningsorder.index(thisinnings) == 1 and inningsscore > matchresults["Innings 1 Score"][-1]:
                        break
                    # add superover tie thing.

                    score = rng.choice(simstats[thisinnings]["Batpvalues"].index, p=simstats[thisinnings]["Batpvalues"].values, shuffle=False)
                    inningsscore += score[0]

                matchresults[f"Innings {inningsorder.index(thisinnings)+1} Team"].append(thisinnings)
                matchresults[f"Innings {inningsorder.index(thisinnings)+1} Score"].append(inningsscore)
                matchresults[f"Innings {inningsorder.index(thisinnings)+1} Wickets"].append(inningswickets)

            if matchresults["Innings 1 Score"][-1]>matchresults["Innings 2 Score"][-1]:
                matchresults["Winner"].append(matchresults["Innings 1 Team"][-1])
            if matchresults["Innings 1 Score"][-1]<matchresults["Innings 2 Score"][-1]:
                matchresults["Winner"].append(matchresults["Innings 2 Team"][-1])
            if matchresults["Innings 1 Score"][-1]==matchresults["Innings 2 Score"][-1]:
                matchresults["Winner"].append("Tie")

        self.results=pd.DataFrame(matchresults)