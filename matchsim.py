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


# Monte Carlo simulation of each ball in match


# input parameters: score, wicket, extras? but maybe make these each spearate random choices for a ball. yes
# TODO Indexing to venue/country?
# TODO Get p-values for first or second innings separately.
# TODO Get p-values for toss choice.
# TODO Add player statistics into teams?
# TODO Add superover tiebreaker
# TODO Test simulation: 

class matchsim:
    def __init__(self,simteams=None) -> None:
        self.simteams = simteams
        self.results = None

    def sim(self, statsdatabase, statsfrom_date, statsto_date, statssex, statsmatchtype, simulations):

        # search stats for p-values
        simteamsstats = cricketstats.search(teams=self.simteams)
        simteamsstats.stats(database=statsdatabase, from_date=statsfrom_date, to_date=statsto_date, matchtype=[statsmatchtype], betweenovers=[], innings=[], sex=[statssex], playersteams=[], oppositionbatters=[], oppositionbowlers=[], oppositionteams=[], venue=[], event=[], matchresult=[], superover=None, battingposition=[], bowlingposition=[], fielders=[], sumstats=False)

        # All balls in game based p-values
        # simstats = {}
        # for eachteam in self.simteams:
        #     simstats[eachteam]={"BattingPs":{}, "BowlingPs":{}}

        #     simstats[eachteam]["BattingPs"]["RunsP"] = simteamsstats.ballresult[["Runs Scored"]].loc[simteamsstats.ballresult["Batting Team"]==eachteam].value_counts(normalize=True,sort=False)
        #     simstats[eachteam]["BowlingPs"]["RunsgivenP"] = simteamsstats.ballresult[["Runs Scored"]].loc[simteamsstats.ballresult["Bowling Team"]==eachteam].value_counts(normalize=True,sort=False)

        #     simstats[eachteam]["BattingPs"]["WicketgivenP"] = simteamsstats.ballresult[['Out/NotOut']].loc[simteamsstats.ballresult["Batting Team"]==eachteam].value_counts(normalize=True,sort=False)
        #     simstats[eachteam]["BowlingPs"]["WicketP"] = simteamsstats.ballresult[["Out/NotOut"]].loc[simteamsstats.ballresult["Bowling Team"]==eachteam].value_counts(normalize=True,sort=False)

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
                bowlingteam = None

                for eachteam in inningsorder:
                    if eachteam!=thisinnings:
                        bowlingteam = eachteam

                overs = 0
                if statsmatchtype=="T20":
                    overs=20
                if statsmatchtype=="ODI" or statsmatchtype=="ODM":
                    overs=50

                # over generator
                for thisover in range(overs):
                    if inningswickets == 10:
                        break
                    if inningsorder.index(thisinnings) == 1 and inningsscore > matchresults["Innings 1 Score"][-1]:
                        break



                    # to use current outs, I can check if probs sum to 1, if higher substract diff, if less add diff?
                    # or here add the probabilites of innings currents outs p-values This would provide skew
                    # wicketPcurrentouts = simteamsstats.ballresult[['Out/NotOut']].loc[(simteamsstats.ballresult["Batting Team"]==thisinnings)&(simteamsstats.ballresult["Current Outs"]==inningswickets)].value_counts(normalize=True,sort=False)

                    # Over based p-values
                    # Batter Score p-values 
                    scoreP = simteamsstats.ballresult[["Batter Score"]].loc[(simteamsstats.ballresult["Batting Team"]==thisinnings)&(simteamsstats.ballresult["Ball"]>(thisover))&(simteamsstats.ballresult["Ball"]<(thisover+1))].value_counts(normalize=True,sort=False).add(simteamsstats.ballresult[["Batter Score"]].loc[(simteamsstats.ballresult["Bowling Team"]==bowlingteam)&(simteamsstats.ballresult["Ball"]>(thisover))&(simteamsstats.ballresult["Ball"]<(thisover+1))].value_counts(normalize=True,sort=False),fill_value=0).divide(2)

                    # Extras Score p-values
                    extrasP = simteamsstats.ballresult[["Extras"]].loc[(simteamsstats.ballresult["Bowling Team"]==bowlingteam)&(simteamsstats.ballresult["Ball"]>(thisover))&(simteamsstats.ballresult["Ball"]<(thisover+1))].value_counts(normalize=True,sort=False)

                    # Over based wicket p-values
                    wicketfallP = simteamsstats.ballresult[['Out/NotOut']].loc[(simteamsstats.ballresult["Batting Team"]==thisinnings)&(simteamsstats.ballresult["Ball"]>(thisover))&(simteamsstats.ballresult["Ball"]<(thisover+1))].value_counts(normalize=True,sort=False).add(simteamsstats.ballresult[["Out/NotOut"]].loc[(simteamsstats.ballresult["Bowling Team"]==bowlingteam)&(simteamsstats.ballresult["Ball"]>(thisover))&(simteamsstats.ballresult["Ball"]<(thisover+1))].value_counts(normalize=True,sort=False),fill_value=0).divide(2)



                    #wicketfallP= wicketfallP.add(wicketPcurrentouts).divide(2)

                    # print(scoreP)
                    # print(wicketfallP)

                    # Fix if p-values don't sum to 1
                    #if sum(scoreP.tolist())!=1:


                    # Fix if p-values don't have all possibilites
                    # if len(scoreP)<7:
                    #     scoreP=scoreP.apply(lambda x: x/(1+x))
                    #     newPs= (1-sum(scoreP))/(7-len(scoreP))
                    #     scoreP=scoreP.reindex([0,1,2,3,4,5,6])
                    #     print(scoreP)
                    #     for eachvalue in scoreP.index:
                    #         if pd.isna(scoreP[eachvalue]):
                    #             scoreP[eachvalue]=newPs
                    #     print(f"ScoreP Sum: {sum(scoreP)}")
                            # else:
                                # rs[eachvalue]=rs[eachvalue]/(1+(rs[eachvalue]))
                        

                    # ball outcome generator
                    for thisball in range(1,7):

                        # innings based wicket p-values
                        # wicketfallP = simstats[thisinnings]['BattingPs']["WicketgivenP"].add(simstats[bowlingteam]['BowlingPs']["WicketP"]).divide(2)
                        # innings based wicket rng
                        # wicket = rng.choice(simstats[thisinnings]['BattingPs']["WicketgivenP"].index, p=wicketfallP.tolist(), shuffle=False) 

                        #wicketgiven = rng.choice(simstats[thisinnings]['BattingPs']["WicketgivenP"].index, p=simstats[thisinnings]['BattingPs']["WicketgivenP"].values, shuffle=False) 
                        #wicketaken = rng.choice(simstats[bowlingteam]['BowlingPs']["WicketP"].index, p=simstats[bowlingteam]['BowlingPs']["WicketP"].values, shuffle=False)

                        # Innings based p-values scoring
                        # scoreP = simstats[thisinnings]['BattingPs']["RunsP"].add(simstats[bowlingteam]['BowlingPs']["RunsgivenP"],fill_value=0).divide(2)

                        # innings based scoring rng
                        # score = rng.choice(simstats[thisinnings]['BattingPs']["RunsP"].index, p=scoreP.tolist(), shuffle=False)
                        
                        # Over based wicket rng
                        wicket = rng.choice(wicketfallP.index, p=wicketfallP.tolist(), shuffle=False)

                        if wicket[0]=="Out":
                            inningswickets += 1
                        if inningswickets == 10:
                            break
                        
                        # Over based scoring rng
                        if wicket[0]!="Out":
                            batterscore = rng.choice(scoreP.index, p=scoreP.tolist(), shuffle=False)
                            extras = rng.choice(extrasP.index, p=extrasP.tolist(), shuffle=False)
                            inningsscore += (batterscore[0]+extras[0])

                        
                        
                        if inningsorder.index(thisinnings) == 1 and inningsscore > matchresults["Innings 1 Score"][-1]:
                            break

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