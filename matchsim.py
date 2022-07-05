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

# TODO simulate toss and chossing based on previous toss win decisions
# TODO Innings simulator, that can simulate innings from any given point.
# TODO Indexing to venue/country?
# TODO Get p-values for toss choice.
# TODO Add player statistics into teams?
# TODO Add superover tiebreaker
# TODO Test simulation: just do a while loop. get declared innings by eachinnings["declared"]. rewrite cricketstats to include this in teaminnings stats. then get p-value of declaration based on number of overs and innings score.
# TODO add wide/noball and byes/legbyes p-values for extras with while loop. This requires rewriting crickets stats to include extras type

class matchsim:
    def __init__(self,simteams=None) -> None:
        self.simteams = simteams
        self.results = None
        self.simteamstats = None
        self.inningsscore = 0
        self.inningswickets = 0

    def matchresultssetup(self, statsmatchtype):
        limitedovers = {"Innings 1 Team":[], "Innings 1 Wickets":[],"Innings 1 Score":[], "Innings 2 Team":[],"Innings 2 Wickets":[], "Innings 2 Score":[],"Winner":[]}
        testmatch={"Innings 1 Team":[],"Innings 1 Wickets":[], "Innings 1 Score":[],"Innings 2 Team":[],"Innings 2 Wickets":[], "Innings 2 Score":[],"Innings 3 Team":[],"Innings 3 Wickets":[], "Innings 3 Score":[],"Innings 4 Team":[], "Innings 4 Wickets":[],"Innings 4 Score":[],"Winner":[]}
        matchtypes={"T20": limitedovers, "ODI": limitedovers,"ODM": limitedovers,"Test": testmatch}
        self.results = matchtypes[statsmatchtype] 

    def pvaluesearch(self, statsdatabase, statsfrom_date, statsto_date, statssex, statsmatchtype):
        # search stats for p-values
        self.simteamstats = cricketstats.search(teams=self.simteams)
        self.simteamstats.stats(database=statsdatabase, from_date=statsfrom_date, to_date=statsto_date, matchtype=[statsmatchtype], betweenovers=[], innings=[], sex=[statssex], playersteams=[], oppositionbatters=[], oppositionbowlers=[], oppositionteams=[], venue=[], event=[], matchresult=[], superover=None, battingposition=[], bowlingposition=[], fielders=[], sumstats=False)

        # Pre search p-values have to add one search as dictionary this will speed up simulations.
        # simstats = {}
        # for eachteam in self.simteams:
        #     simstats[eachteam]={"BattingPs":{}, "BowlingPs":{}}

        #     simstats[eachteam]["BattingPs"]["RunsP"] = self.simteamstats.ballresult[["Runs Scored"]].loc[self.simteamstats.ballresult["Batting Team"]==eachteam].value_counts(normalize=True,sort=False)
        #     simstats[eachteam]["BowlingPs"]["RunsgivenP"] = self.simteamstats.ballresult[["Runs Scored"]].loc[self.simteamstats.ballresult["Bowling Team"]==eachteam].value_counts(normalize=True,sort=False)

        #     simstats[eachteam]["BattingPs"]["WicketgivenP"] = self.simteamstats.ballresult[['Out/NotOut']].loc[self.simteamstats.ballresult["Batting Team"]==eachteam].value_counts(normalize=True,sort=False)
        #     simstats[eachteam]["BowlingPs"]["WicketP"] = self.simteamstats.ballresult[["Out/NotOut"]].loc[self.simteamstats.ballresult["Bowling Team"]==eachteam].value_counts(normalize=True,sort=False)

    def limitedovers(self,rng,statsmatchtype,inningsorder):
        # toss rng to decide inningsorder
        inningsorder = rng.choice(self.simteams, p=[0.5,0.5],size=2, replace=False, shuffle=False).tolist()


        # innings generator
        for thisinnings in inningsorder:  
            self.inningsscore = 0
            self.inningswickets = 0
            bowlingteam = None
            nthinnings = inningsorder.index(thisinnings)

            for eachteam in inningsorder:
                if eachteam!=thisinnings:
                    bowlingteam = eachteam

            if statsmatchtype=="T20":
                overs=20
            if statsmatchtype=="ODI" or statsmatchtype=="ODM":
                overs=50

            # Innings based fallback probabilites
            inningswicketfallP = self.simteamstats.ballresult[['Out/NotOut']].loc[(self.simteamstats.ballresult["Batting Team"]==thisinnings)&(self.simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False).add(self.simteamstats.ballresult[["Out/NotOut"]].loc[(self.simteamstats.ballresult["Bowling Team"]==bowlingteam)&(self.simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False),fill_value=0).divide(2)

            # over generator
            for thisover in range(overs):
                if self.inningswickets == 10:
                    break
                if nthinnings == 1 and self.inningsscore > self.results["Innings 1 Score"][-1]:
                    break

                # To use current outs, add following condition: &(self.simteamstats.ballresult["Current Outs"]==inningswickets)
                # It is removed now because it lowers sample size

                # Over based p-values
                # Batter Score p-values 
                scoreP = self.simteamstats.ballresult[["Batter Score"]].loc[(self.simteamstats.ballresult["Batting Team"]==thisinnings)&(self.simteamstats.ballresult["Ball"]>(thisover))&(self.simteamstats.ballresult["Ball"]<(thisover+1))&(self.simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False).add(self.simteamstats.ballresult[["Batter Score"]].loc[(self.simteamstats.ballresult["Bowling Team"]==bowlingteam)&(self.simteamstats.ballresult["Ball"]>(thisover))&(self.simteamstats.ballresult["Ball"]<(thisover+1))&(self.simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False),fill_value=0).divide(2)

                # Extras Score p-values
                extrasP = self.simteamstats.ballresult[["Extras"]].loc[(self.simteamstats.ballresult["Bowling Team"]==bowlingteam)&(self.simteamstats.ballresult["Ball"]>(thisover))&(self.simteamstats.ballresult["Ball"]<(thisover+1))].value_counts(normalize=True,sort=False)

                # Over based wicket p-values
                wicketfallP = self.simteamstats.ballresult[['Out/NotOut']].loc[(self.simteamstats.ballresult["Batting Team"]==thisinnings)&(self.simteamstats.ballresult["Ball"]>(thisover))&(self.simteamstats.ballresult["Ball"]<(thisover+1))&(self.simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False).add(self.simteamstats.ballresult[["Out/NotOut"]].loc[(self.simteamstats.ballresult["Bowling Team"]==bowlingteam)&(self.simteamstats.ballresult["Ball"]>(thisover))&(self.simteamstats.ballresult["Ball"]<(thisover+1))&(self.simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False),fill_value=0).divide(2)


                # Fix if p-values don't have all possibilites
                if len(scoreP)<7:
                    # print(f"Before Modification: {scoreP}")
                    lowestP = min(scoreP)
                    scoreP=scoreP.apply(lambda x: x/(1+lowestP))
                    newPs= (1-sum(scoreP))/(7-len(scoreP))
                    # print(scoreP)
                    scoreP=scoreP.reindex([(0,),(1,),(2,),(3,),(4,),(5,),(6,)])
                    # print(scoreP)
                    for eachvalue in scoreP.index:
                        if pd.isna(scoreP[eachvalue]):
                            scoreP[eachvalue]=newPs
                    # print(scoreP)
                    # print(f"ScoreP Sum: {sum(scoreP)}")

                # print(wicketfallP)
                if len(wicketfallP)<2 or sum(wicketfallP)!=1:
                    wicketfallP=inningswicketfallP

                matchsim.over(self,rng,wicketfallP,scoreP, extrasP,nthinnings)
                
            self.results[f"Innings {nthinnings+1} Team"].append(thisinnings)
            self.results[f"Innings {nthinnings+1} Score"].append(self.inningsscore)
            self.results[f"Innings {nthinnings+1} Wickets"].append(self.inningswickets)

    def testmatch(self,rng,statsmatchtype,inningsorder, rain):
        # toss rng to decide inningsorder
        if not inningsorder:
            toss = rng.choice(self.simteams, p=[0.5,0.5],size=2, replace=False, shuffle=False).tolist()
            inningsorder = toss+toss
        
        if rain:
            rainaffected = rng.choice(["rain","no_rain"], p=[0.1,0.9],size=1, replace=False, shuffle=False)
        
        matchover = 0
        inningsnumber=0
        # innings generator
        for thisinnings in inningsorder:
            if matchover >= 450:
                break
            inningsnumber+=1
            self.inningsscore = 0
            self.inningswickets = 0
            bowlingteam = None
            nthinnings = inningsnumber-1

            for eachteam in inningsorder:
                if eachteam!=thisinnings:
                    bowlingteam = eachteam

            # Innings based fallback probabilites
            inningswicketfallP = self.simteamstats.ballresult[['Out/NotOut']].loc[(self.simteamstats.ballresult["Batting Team"]==thisinnings)&(self.simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False).add(self.simteamstats.ballresult[["Out/NotOut"]].loc[(self.simteamstats.ballresult["Bowling Team"]==bowlingteam)&(self.simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False),fill_value=0).divide(2)

            inningsscorefallP= self.simteamstats.ballresult[["Batter Score"]].loc[(self.simteamstats.ballresult["Batting Team"]==thisinnings)&(self.simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False).add(self.simteamstats.ballresult[["Batter Score"]].loc[(self.simteamstats.ballresult["Bowling Team"]==bowlingteam)&(self.simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False),fill_value=0).divide(2)

            inningsextrasfallP=self.simteamstats.ballresult[["Extras"]].loc[(self.simteamstats.ballresult["Bowling Team"]==bowlingteam)&(self.simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False)

            thisover=0
            # over generator
            while self.inningswickets<10 and matchover<450:
                if nthinnings == 3 and self.inningsscore > (self.results["Innings 1 Score"][-1]+self.results["Innings 3 Score"][-1]-self.results["Innings 2 Score"][-1]):
                    break
                if nthinnings==2 and (((self.inningsscore+self.results["Innings 1 Score"][-1]-self.results["Innings 2 Score"][-1])/(450-matchover))>4):
                    break

                # Over based p-values
                # Batter Score p-values 
                scoreP = self.simteamstats.ballresult[["Batter Score"]].loc[(self.simteamstats.ballresult["Batting Team"]==thisinnings)&(self.simteamstats.ballresult["Ball"]>(thisover))&(self.simteamstats.ballresult["Ball"]<(thisover+1))&(self.simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False).add(self.simteamstats.ballresult[["Batter Score"]].loc[(self.simteamstats.ballresult["Bowling Team"]==bowlingteam)&(self.simteamstats.ballresult["Ball"]>(thisover))&(self.simteamstats.ballresult["Ball"]<(thisover+1))&(self.simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False),fill_value=0).divide(2)

                # Extras Score p-values
                extrasP = self.simteamstats.ballresult[["Extras"]].loc[(self.simteamstats.ballresult["Bowling Team"]==bowlingteam)&(self.simteamstats.ballresult["Ball"]>(thisover))&(self.simteamstats.ballresult["Ball"]<(thisover+1))].value_counts(normalize=True,sort=False)

                # Over based wicket p-values
                wicketfallP = self.simteamstats.ballresult[['Out/NotOut']].loc[(self.simteamstats.ballresult["Batting Team"]==thisinnings)&(self.simteamstats.ballresult["Ball"]>(thisover))&(self.simteamstats.ballresult["Ball"]<(thisover+1))&(self.simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False).add(self.simteamstats.ballresult[["Out/NotOut"]].loc[(self.simteamstats.ballresult["Bowling Team"]==bowlingteam)&(self.simteamstats.ballresult["Ball"]>(thisover))&(self.simteamstats.ballresult["Ball"]<(thisover+1))&(self.simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False),fill_value=0).divide(2)

                # print(wicketfallP)
                if len(wicketfallP)<2 or sum(wicketfallP)!=1:
                    wicketfallP=inningswicketfallP
                if len(scoreP)==0 or sum(scoreP)!=1:
                    scoreP=inningsscorefallP
                if len(extrasP)==0 or sum(extrasP)!=1:
                    extrasP=inningsextrasfallP

                # Fix if p-values don't have all possibilites
                if len(scoreP)<7:
                    # print(f"Before Modification: {scoreP}")
                    lowestP = min(scoreP)
                    scoreP=scoreP.apply(lambda x: x/(1+lowestP))
                    newPs= (1-sum(scoreP))/(7-len(scoreP))
                    # print(scoreP)
                    scoreP=scoreP.reindex([(0,),(1,),(2,),(3,),(4,),(5,),(6,)])
                    # print(scoreP)
                    for eachvalue in scoreP.index:
                        if pd.isna(scoreP[eachvalue]):
                            scoreP[eachvalue]=newPs
                    # print(scoreP)
                    # print(f"ScoreP Sum: {sum(scoreP)}")

                matchsim.over(self,rng,wicketfallP,scoreP, extrasP,nthinnings,statsmatchtype)
                thisover +=1
                matchover +=1

                # rain rng
                if rain:
                    if rainaffected=="rain":
                        rainaffected="no_rain"
                        overslost = rng.integers(low=15, high=60)
                        matchover+=overslost
            
            #print(thisover)
            self.results[f"Innings {nthinnings+1} Team"].append(thisinnings)
            self.results[f"Innings {nthinnings+1} Score"].append(self.inningsscore)
            self.results[f"Innings {nthinnings+1} Wickets"].append(self.inningswickets)
        print(f"Overs left: {450-matchover}")

    def over(self,rng,wicketfallP,scoreP, extrasP,nthinnings,statsmatchtype):
        # ball outcome generator
        legaldeliveries = 0
        while legaldeliveries < 6:
            # Over based wicket rng
            wicket = rng.choice(wicketfallP.index, p=wicketfallP.tolist(), shuffle=False)

            if wicket[0]=="Out":
                legaldeliveries += 1
                self.inningswickets += 1
            if self.inningswickets == 10:
                break
            
            # Over based scoring rng
            if wicket[0]!="Out":
                legaldeliveries += 1
                batterscore = rng.choice(scoreP.index, p=scoreP.tolist(), shuffle=False)
                extras = rng.choice(extrasP.index, p=extrasP.tolist(), shuffle=False)
                self.inningsscore += (batterscore[0]+extras[0])

            if (statsmatchtype == "T20" or statsmatchtype == "ODI" or statsmatchtype == "ODM") and (nthinnings == 1 and self.inningsscore > self.results["Innings 1 Score"][-1]):
                break
            if statsmatchtype == "Test" and (self.inningswickets==10 or (nthinnings == 3 and self.inningsscore > (self.results["Innings 1 Score"][-1]+self.results["Innings 3 Score"][-1]-self.results["Innings 2 Score"][-1]))):
                break


    def sim(self, statsdatabase, statsfrom_date, statsto_date, statssex, statsmatchtype,simulations, inningsorder=None,rain=False):

        # Setup match results
        matchsim.matchresultssetup(self,statsmatchtype)

        # Search for pvalues
        matchsim.pvaluesearch(self, statsdatabase, statsfrom_date, statsto_date, statssex, statsmatchtype)

        # match generator
        
        rng = np.random.default_rng()

        matchtypes={"T20": matchsim.limitedovers, "ODI": matchsim.limitedovers,"ODM": matchsim.limitedovers,"Test": matchsim.testmatch}
        for thismatch in range(simulations):

            matchtypes[statsmatchtype](self,rng,statsmatchtype,inningsorder,rain)


            if statsmatchtype == "T20" or statsmatchtype == "ODI" or statsmatchtype == "ODM":
                if self.results["Innings 1 Score"][-1]>self.results["Innings 2 Score"][-1]:
                    self.results["Winner"].append(self.results["Innings 1 Team"][-1])
                if self.results["Innings 1 Score"][-1]<self.results["Innings 2 Score"][-1]:
                    self.results["Winner"].append(self.results["Innings 2 Team"][-1])
                if self.results["Innings 1 Score"][-1]==self.results["Innings 2 Score"][-1]:
                    self.results["Winner"].append("Tie")

            if statsmatchtype == "Test":
                if (self.results["Innings 1 Score"][-1]+self.results["Innings 3 Score"][-1])>(self.results["Innings 2 Score"][-1]+self.results["Innings 4 Score"][-1]) and (self.results["Innings 4 Wickets"][-1]==10):
                    self.results["Winner"].append(self.results["Innings 1 Team"][-1])
                if (self.results["Innings 1 Score"][-1]+self.results["Innings 3 Score"][-1])<(self.results["Innings 2 Score"][-1]+self.results["Innings 4 Score"][-1]):
                    self.results["Winner"].append(self.results["Innings 2 Team"][-1])
                if (self.results["Innings 1 Score"][-1]+self.results["Innings 3 Score"][-1])==(self.results["Innings 2 Score"][-1]+self.results["Innings 4 Score"][-1]):
                    self.results["Winner"].append("Tie")
                if (self.results["Innings 1 Score"][-1]+self.results["Innings 3 Score"][-1])>(self.results["Innings 2 Score"][-1]+self.results["Innings 4 Score"][-1]) and (self.results["Innings 4 Wickets"][-1]<10):
                    self.results["Winner"].append("Draw")

        # print(self.results)

        self.results=pd.DataFrame(self.results)