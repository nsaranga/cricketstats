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
import multiprocessing as mp
import time


module_path = os.path.abspath(os.path.join("./cricketstats/"))
if module_path not in sys.path:
    sys.path.append(module_path)
import cricketstats


# Monte Carlo simulation of each ball in match

# TODO simulate particular phases, over intervals. this would help determine score after particular overs.
# TODO Add superover tiebreaker for limited overs matches.

# reorganise into PyPi and submit online



# TODO add share data manager for simsteamstats
# TODO work out how to combine probabilities for OUt/not out, when one team has empty probs.
# TODO add option to simulate toss 60/40 in favour of batting first.
# TODO Innings simulator, that can simulate innings from any given point.
# TODO Indexing to venue/country?
# TODO Add player statistics into teams?

# TODO add wide/noball and byes/legbyes p-values for extras with while loop. This requires rewriting crickets stats to include extras type

# TODO Make this simulation of innings record that then have winning losing. YES
# In mean time i can include overs bowled, runs/wicket and run rate for each innings
        # self.inningsresult = {
        # "Date":[], "Match Type":[],"Venue":[], "Event":[], "Batting Team":[], "Bowling Team":[], "Innings":[], 
        # "Defended Score": [], "Chased Score": [], "Margin":[], "Declared":[],
        # "Score": [], "Outs": [], "Overs": [], "Extras": [],
        # "Runs/Wicket":[], "Runs/Ball":[], "Run Rate":[], "First Boundary Ball":[],
        # "Avg Consecutive Dot Balls":[]
        # }

class matchsim:
    def __init__(self,simteams=None) -> None:
        self.simteams = simteams
        self.simresults = None
        self.simteamstats = None

    def simresultssetup(self, statsmatchtype):
        limitedovers = {"Innings 1 Team":[], "Innings 1 Wickets":[],"Innings 1 Score":[], "Innings 1 Overs":[], "Innings 2 Team":[],"Innings 2 Wickets":[], "Innings 2 Score":[], "Innings 2 Overs":[],"Winner":[]}
        testmatch={"Innings 1 Team":[],"Innings 1 Wickets":[], "Innings 1 Score":[], "Innings 1 Overs":[],"Innings 2 Team":[],"Innings 2 Wickets":[], "Innings 2 Score":[],"Innings 2 Overs":[],"Innings 3 Team":[],"Innings 3 Wickets":[], "Innings 3 Score":[],"Innings 3 Overs":[],"Innings 4 Team":[], "Innings 4 Wickets":[],"Innings 4 Score":[],"Innings 4 Overs":[],"Winner":[]}
        matchtypes={"T20": limitedovers, "ODI": limitedovers,"ODM": limitedovers,"Test": testmatch}
        self.simresults = matchtypes[statsmatchtype]

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

    def inningsfallbacks(self,nthinnings,thisinnings, bowlingteam,simteamstats):
        inningswicketfallP = simteamstats.ballresult[['Out/NotOut']].loc[(simteamstats.ballresult["Batting Team"]==thisinnings)&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False).add(simteamstats.ballresult[["Out/NotOut"]].loc[(simteamstats.ballresult["Bowling Team"]==bowlingteam)&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False),fill_value=0).divide(2)

        inningsscorefallP= simteamstats.ballresult[["Batter Score"]].loc[(simteamstats.ballresult["Batting Team"]==thisinnings)&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False).add(simteamstats.ballresult[["Batter Score"]].loc[(simteamstats.ballresult["Bowling Team"]==bowlingteam)&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False),fill_value=0).divide(2)

        inningsextrasfallP=simteamstats.ballresult[["Extras"]].loc[(simteamstats.ballresult["Bowling Team"]==bowlingteam)&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False)

        return inningswicketfallP,inningsscorefallP,inningsextrasfallP

    def oversrunsPs(self,nthinnings,thisinnings, bowlingteam,simteamstats,thisover,hometeam):
        # scoreP = simteamstats.ballresult[["Batter Score"]].loc[(simteamstats.ballresult["Batting Team"]==thisinnings)&(simteamstats.ballresult["Ball"]>(thisover))&(simteamstats.ballresult["Ball"]<(thisover+1))&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False).add(simteamstats.ballresult[["Batter Score"]].loc[(simteamstats.ballresult["Bowling Team"]==bowlingteam)&(simteamstats.ballresult["Ball"]>(thisover))&(simteamstats.ballresult["Ball"]<(thisover+1))&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False),fill_value=0).divide(2)

        if hometeam==thisinnings:
            batadv=0.55
            bowladv=1-batadv
        if hometeam==bowlingteam:
            bowladv=0.55
            batadv=1-bowladv
        if hometeam==None:
            batadv=0.5
            bowladv=0.5

        scoreOversP = (simteamstats.ballresult[["Batter Score"]].loc[(simteamstats.ballresult["Batting Team"]==thisinnings)&(simteamstats.ballresult["Ball"]>(thisover))&(simteamstats.ballresult["Ball"]<(thisover+1))&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False)*batadv).add((simteamstats.ballresult[["Batter Score"]].loc[(simteamstats.ballresult["Bowling Team"]==bowlingteam)&(simteamstats.ballresult["Ball"]>(thisover))&(simteamstats.ballresult["Ball"]<(thisover+1))&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False)*bowladv),fill_value=0)    

        #scoreOversP = simteamstats.ballresult[["Batter Score"]].loc[(simteamstats.ballresult["Batting Team"]==thisinnings)&(simteamstats.ballresult["Ball"]>(thisover))&(simteamstats.ballresult["Ball"]<(thisover+1))&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False).add(simteamstats.ballresult[["Batter Score"]].loc[(simteamstats.ballresult["Bowling Team"]==bowlingteam)&(simteamstats.ballresult["Ball"]>(thisover))&(simteamstats.ballresult["Ball"]<(thisover+1))&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False),fill_value=0).divide(2)

        scoreCOutsP = simteamstats.ballresult[["Batter Score"]].loc[(simteamstats.ballresult["Batting Team"]==thisinnings)&(simteamstats.ballresult["Current Outs"]==self.inningswickets)].value_counts(normalize=True,sort=False).add(simteamstats.ballresult[["Batter Score"]].loc[(simteamstats.ballresult["Bowling Team"]==bowlingteam)&(simteamstats.ballresult["Current Outs"]==self.inningswickets)].value_counts(normalize=True,sort=False),fill_value=0).divide(2)

        #scoreP = scoreCOutsP
        scoreP = scoreOversP
        #scoreP = scoreOversP.add(scoreCOutsP, fill_value=0).divide(2)

        # Extras Score p-values
        extrasP = simteamstats.ballresult[["Extras"]].loc[(simteamstats.ballresult["Bowling Team"]==bowlingteam)&(simteamstats.ballresult["Ball"]>(thisover))&(simteamstats.ballresult["Ball"]<(thisover+1))].value_counts(normalize=True,sort=False)

        return scoreP, extrasP

    def overswicketsPs(self,nthinnings,thisinnings, bowlingteam,simteamstats,thisover,hometeam):
        if hometeam==thisinnings:
            batadv=0.55
            bowladv=1-batadv
        if hometeam==bowlingteam:
            bowladv=0.55
            batadv=1-bowladv
        if hometeam==None:
            batadv=0.5
            bowladv=0.5

        wicketfallOversP= (simteamstats.ballresult[['Out/NotOut']].loc[(simteamstats.ballresult["Batting Team"]==thisinnings)&(simteamstats.ballresult["Ball"]>(thisover))&(simteamstats.ballresult["Ball"]<(thisover+1))&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False)*batadv).add((simteamstats.ballresult[["Out/NotOut"]].loc[(simteamstats.ballresult["Bowling Team"]==bowlingteam)&(simteamstats.ballresult["Ball"]>(thisover))&(simteamstats.ballresult["Ball"]<(thisover+1))&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False)*bowladv),fill_value=0)
        
        #wicketfallOversP= simteamstats.ballresult[['Out/NotOut']].loc[(simteamstats.ballresult["Batting Team"]==thisinnings)&(simteamstats.ballresult["Ball"]>(thisover))&(simteamstats.ballresult["Ball"]<(thisover+1))&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False).add(simteamstats.ballresult[["Out/NotOut"]].loc[(simteamstats.ballresult["Bowling Team"]==bowlingteam)&(simteamstats.ballresult["Ball"]>(thisover))&(simteamstats.ballresult["Ball"]<(thisover+1))&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False),fill_value=0).divide(2)

        wicketfallCOutsP = simteamstats.ballresult[['Out/NotOut']].loc[(simteamstats.ballresult["Batting Team"]==thisinnings)&(simteamstats.ballresult["Current Outs"]==self.inningswickets)].value_counts(normalize=True,sort=False).add(simteamstats.ballresult[['Out/NotOut']].loc[(simteamstats.ballresult["Bowling Team"]==bowlingteam)&(simteamstats.ballresult["Current Outs"]==self.inningswickets)].value_counts(normalize=True,sort=False),fill_value=0).divide(2)

        wicketfallP = wicketfallOversP.add(wicketfallCOutsP, fill_value=0).divide(2)
        # wicketfallP =wicketfallOversP
        #wicketfallP =wicketfallCOutsP
        return wicketfallP

    def over(self,rng,wicketfallP,scoreP, extrasP,nthinnings,statsmatchtype,thisover):
        # ball outcome generator
        legaldeliveries = 0
        while legaldeliveries < 6:

            # Over based wicket rng
            wicket = rng.choice(wicketfallP.index, p=wicketfallP.tolist(), shuffle=False)

            if wicket[0]=="Out":
                legaldeliveries += 1
                self.inningswickets += 1
            if self.inningswickets == 10:
                self.inningsovers=float(f"{thisover}.{legaldeliveries}")
                break
            
            # Over based scoring rng
            if wicket[0]!="Out":
                legaldeliveries += 1
                batterscore = rng.choice(scoreP.index, p=scoreP.tolist(), shuffle=False)
                extras = rng.choice(extrasP.index, p=extrasP.tolist(), shuffle=False)
                self.inningsscore += (batterscore[0]+extras[0])

            # Check if score has been chased
            if ((statsmatchtype == "T20" or statsmatchtype == "ODI" or statsmatchtype == "ODM") and (nthinnings == 1 and self.inningsscore > self.matchresults["Innings 1 Score"][-1])) or (statsmatchtype == "Test" and (self.inningswickets==10 or (nthinnings == 3 and self.inningsscore > (self.matchresults["Innings 1 Score"][-1]+self.matchresults["Innings 3 Score"][-1]-self.matchresults["Innings 2 Score"][-1])))):
                self.inningsovers=float(f"{thisover}.{legaldeliveries}")
                break
        

    def redistributepvalues(self,scoreP):
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
        return scoreP

    def resetinningstally(self):
        self.inningsscore = 0
        self.inningswickets = 0
        self.inningsovers = 0

    def mcsimulations(self, statsmatchtype,simulations,inningsorder,rain,matchscore,hometeam):
        # print("Sims started")
        # setup random generator object
        rng = np.random.default_rng()
        # Set function dictionary
        matchtypes={"T20": ld.limitedovers, "ODI": ld.limitedovers,"ODM": ld.limitedovers,"Test": tm.testmatch}
        classtypes={"T20": ld, "ODI": ld,"ODM": ld,"Test": tm}

        sim=classtypes[statsmatchtype]()

        sim.resultssetup()
        for thismatch in range(simulations):
            sim.matchresultssetup()
            # Function to simulate a match
            if statsmatchtype=="T20" or statsmatchtype=="ODI" or statsmatchtype=="ODM":
                sim.limitedovers(rng,statsmatchtype,inningsorder,rain,self.simteams,self.simteamstats,matchscore,hometeam)

            if statsmatchtype=="Test":
                sim.testmatch(rng,statsmatchtype,inningsorder,rain,self.simteams,self.simteamstats,matchscore,hometeam)

        return sim.results
            
    def sim(self, statsdatabase, statsfrom_date, statsto_date, statssex, statsmatchtype,simulations,inningsorder=None,rain=False,matchscore=None,hometeam=None, multicore=True):
        # Setup match results
        matchsim.simresultssetup(self,statsmatchtype)

        # Search for pvalues
        matchsim.pvaluesearch(self, statsdatabase, statsfrom_date, statsto_date, statssex, statsmatchtype)



        # multiprocessing
        if multicore==True:
            cores = os.cpu_count()
            procpool=mp.Pool(cores)

            simulations=int(simulations/cores)
            inputs=None
            inputs=[]
            print(f"Sims/cpu: {simulations}")
            for x in range(cores):
                inputs.append((self,statsmatchtype,simulations,inningsorder,rain,matchscore,hometeam))

            #start = time.time()
            simprocs = procpool.starmap(matchsim.mcsimulations,inputs)
            
            procpool.close()

            for eachdict in simprocs:
                for eachlist in eachdict:
                    self.simresults[eachlist].extend(eachdict[eachlist])

            self.simresults=pd.DataFrame(self.simresults)
        
        if multicore==False:
            rng = np.random.default_rng()

            # Set function dictionary
            classtypes={"T20": ld, "ODI": ld,"ODM": ld,"Test": tm}

            sim=classtypes[statsmatchtype]()
            # simulation generator
            sim.resultssetup()
            for thismatch in range(simulations):
                sim.matchresultssetup()
                # Function to simulate a match
                if statsmatchtype=="T20" or statsmatchtype=="ODI" or statsmatchtype=="ODM":
                    sim.limitedovers(rng,statsmatchtype,inningsorder,rain,self.simteams,self.simteamstats,matchscore,hometeam)

                if statsmatchtype=="Test":
                    sim.testmatch(rng,statsmatchtype,inningsorder,rain,self.simteams,self.simteamstats,matchscore,hometeam)

            self.simresults=pd.DataFrame(sim.results)


class ld(matchsim):
    def __init__(self) -> None:
        self.inningswickets = 0
        self.inningsscore = 0
        self.inningsovers = 0
        self.matchresults = None
        self.results = None

    def resultssetup(self):
        self.results = {"Innings 1 Team":[], "Innings 1 Wickets":[],"Innings 1 Score":[], "Innings 1 Overs":[], "Innings 2 Team":[],"Innings 2 Wickets":[], "Innings 2 Score":[], "Innings 2 Overs":[],"Winner":[]}
    def matchresultssetup(self):
        self.matchresults = {"Innings 1 Team":[], "Innings 1 Wickets":[],"Innings 1 Score":[], "Innings 1 Overs":[], "Innings 2 Team":[],"Innings 2 Wickets":[], "Innings 2 Score":[], "Innings 2 Overs":[],"Winner":[]}

    def midinningssetup(self, matchscore):
        if len(matchscore) == 1:
            self.inningswickets = matchscore["Innings 1"][1]
            self.inningsscore = matchscore["Innings 1"][2]
            self.inningsovers = matchscore["Innings 1"][3]
        if len(matchscore) == 2:
            self.matchresults["Innings 1 Team"].append(matchscore["Innings 1"][0])
            self.matchresults["Innings 1 Wickets"].append(matchscore["Innings 1"][1])
            self.matchresults["Innings 1 Score"].append(matchscore["Innings 1"][2])
            self.matchresults["Innings 1 Overs"].append(matchscore["Innings 1"][3])
            self.inningswickets = matchscore["Innings 2"][1]
            self.inningsscore = matchscore["Innings 2"][2]
            self.inningsovers = matchscore["Innings 2"][3]


    def limitedovers(self,rng,statsmatchtype,inningsorder,rain,simteams,simteamstats,matchscore,hometeam):

        if matchscore:
            ld.midinningssetup(self,matchscore)

        # Randomly set innings order if not given
        if not inningsorder:
            # toss rng to decide inningsorder
            inningsorder = rng.choice(simteams, p=[0.5,0.5],size=2, replace=False, shuffle=False).tolist()

        # innings generator
        for nthinnings, thisinnings in enumerate(inningsorder):

            if matchscore and (len(matchscore)==2 and thisinnings == matchscore["Innings 1"][0]):
                continue
            # set bowling team
            bowlingteam = None
            for eachteam in inningsorder:
                if eachteam!=thisinnings:
                    bowlingteam = eachteam

            if statsmatchtype=="T20":
                overs=20
            if statsmatchtype=="ODI" or statsmatchtype=="ODM":
                overs=50

            # Innings based fallback probabilites
            inningswicketfallP,inningsscorefallP,inningsextrasfallP = ld.inningsfallbacks(self,nthinnings,thisinnings,bowlingteam,simteamstats)

            # over generator
            for thisover in range(overs):
                # skip to last matchscore overs
                if matchscore and ((len(matchscore)==1 and thisover<(matchscore["Innings 1"][3])) or (len(matchscore)==2 and thisover<(matchscore["Innings 2"][3]))):
                    continue

                if self.inningswickets == 10 or (nthinnings == 1 and self.inningsscore > self.matchresults["Innings 1 Score"][-1]):
                    break

                # Over based p-values
                # Batter Score p-values
                scoreP, extrasP = ld.oversrunsPs(self,nthinnings,thisinnings, bowlingteam,simteamstats,thisover,hometeam)

                # Over based wicket p-values
                wicketfallP = ld.overswicketsPs(self,nthinnings,thisinnings, bowlingteam,simteamstats,thisover,hometeam)

                if len(wicketfallP)<2 or sum(wicketfallP)!=1:
                    wicketfallP=inningswicketfallP
                if len(scoreP)==0 or sum(scoreP)!=1:
                    scoreP=inningsscorefallP
                if len(extrasP)==0 or sum(extrasP)!=1:
                    extrasP=inningsextrasfallP

                # Fix if p-values don't have all possibilites
                if len(scoreP)<7:
                    scoreP = ld.redistributepvalues(self, scoreP)

                # print(thisinnings)
                # print(wicketfallP)
                # print(inningswicketfallP)
                ld.over(self,rng,wicketfallP,scoreP, extrasP,nthinnings,statsmatchtype,thisover)

                if self.inningswickets == 10 or (nthinnings == 1 and self.inningsscore > self.matchresults["Innings 1 Score"][-1]):
                    break
                self.inningsovers+=1

            if self.inningsovers==0:
                self.inningsovers=overs
            self.matchresults[f"Innings {nthinnings+1} Team"].append(thisinnings)
            self.matchresults[f"Innings {nthinnings+1} Wickets"].append(self.inningswickets)
            self.matchresults[f"Innings {nthinnings+1} Score"].append(self.inningsscore)
            self.matchresults[f"Innings {nthinnings+1} Overs"].append(self.inningsovers)
            ld.resetinningstally(self)

        
        if self.matchresults["Innings 1 Score"][-1]>self.matchresults["Innings 2 Score"][-1]:
            self.matchresults["Winner"].append(self.matchresults["Innings 1 Team"][-1])
        if self.matchresults["Innings 1 Score"][-1]<self.matchresults["Innings 2 Score"][-1]:
            self.matchresults["Winner"].append(self.matchresults["Innings 2 Team"][-1])
        if self.matchresults["Innings 1 Score"][-1]==self.matchresults["Innings 2 Score"][-1]:
            self.matchresults["Winner"].append("Tie")
        for eachresult in self.results:
            self.results[eachresult].extend(self.matchresults[eachresult])

class tm(matchsim):
    def __init__(self) -> None:
        self.inningsscore = 0
        self.inningswickets = 0
        self.inningsovers = 0
        self.results = None
        self.matchresults = None

    def resultssetup(self):
        self.results={"Innings 1 Team":[],"Innings 1 Wickets":[], "Innings 1 Score":[], "Innings 1 Overs":[],"Innings 2 Team":[],"Innings 2 Wickets":[], "Innings 2 Score":[],"Innings 2 Overs":[],"Innings 3 Team":[],"Innings 3 Wickets":[], "Innings 3 Score":[],"Innings 3 Overs":[],"Innings 4 Team":[], "Innings 4 Wickets":[],"Innings 4 Score":[],"Innings 4 Overs":[],"Winner":[]}

    def matchresultssetup(self):
        self.matchresults={"Innings 1 Team":[],"Innings 1 Wickets":[], "Innings 1 Score":[], "Innings 1 Overs":[],"Innings 2 Team":[],"Innings 2 Wickets":[], "Innings 2 Score":[],"Innings 2 Overs":[],"Innings 3 Team":[],"Innings 3 Wickets":[], "Innings 3 Score":[],"Innings 3 Overs":[],"Innings 4 Team":[], "Innings 4 Wickets":[],"Innings 4 Score":[],"Innings 4 Overs":[],"Winner":[]}

    def midinningssetup(self, matchscore):
        if len(matchscore) == 1:
            self.inningswickets = matchscore["Innings 1"][1]
            self.inningsscore = matchscore["Innings 1"][2]
            self.inningsovers = matchscore["Innings 1"][3]

        if len(matchscore) == 2:
            self.matchresults["Innings 1 Team"].append(matchscore["Innings 1"][0])
            self.matchresults["Innings 1 Wickets"].append(matchscore["Innings 1"][1])
            self.matchresults["Innings 1 Score"].append(matchscore["Innings 1"][2])
            self.matchresults["Innings 1 Overs"].append(matchscore["Innings 1"][3])
            self.inningswickets = matchscore["Innings 2"][1]
            self.inningsscore = matchscore["Innings 2"][2]
            self.inningsovers = matchscore["Innings 2"][3]

        if len(matchscore) == 3:
            self.matchresults["Innings 1 Team"].append(matchscore["Innings 1"][0])
            self.matchresults["Innings 1 Wickets"].append(matchscore["Innings 1"][1])
            self.matchresults["Innings 1 Score"].append(matchscore["Innings 1"][2])
            self.matchresults["Innings 1 Overs"].append(matchscore["Innings 1"][3])
            self.matchresults["Innings 2 Team"].append(matchscore["Innings 2"][0])
            self.matchresults["Innings 2 Wickets"].append(matchscore["Innings 2"][1])
            self.matchresults["Innings 2 Score"].append(matchscore["Innings 2"][2])
            self.matchresults["Innings 2 Overs"].append(matchscore["Innings 2"][3])
            self.inningswickets = matchscore["Innings 3"][1]
            self.inningsscore = matchscore["Innings 3"][2]
            self.inningsovers = matchscore["Innings 3"][3]

        if len(matchscore) == 4:
            self.matchresults["Innings 1 Team"].append(matchscore["Innings 1"][0])
            self.matchresults["Innings 1 Wickets"].append(matchscore["Innings 1"][1])
            self.matchresults["Innings 1 Score"].append(matchscore["Innings 1"][2])
            self.matchresults["Innings 1 Overs"].append(matchscore["Innings 1"][3])
            self.matchresults["Innings 2 Team"].append(matchscore["Innings 2"][0])
            self.matchresults["Innings 2 Wickets"].append(matchscore["Innings 2"][1])
            self.matchresults["Innings 2 Score"].append(matchscore["Innings 2"][2])
            self.matchresults["Innings 2 Overs"].append(matchscore["Innings 2"][3])
            self.matchresults["Innings 3 Team"].append(matchscore["Innings 3"][0])
            self.matchresults["Innings 3 Wickets"].append(matchscore["Innings 3"][1])
            self.matchresults["Innings 3 Score"].append(matchscore["Innings 3"][2])
            self.matchresults["Innings 3 Overs"].append(matchscore["Innings 3"][3])
            self.inningswickets = matchscore["Innings 4"][1]
            self.inningsscore = matchscore["Innings 4"][2]
            self.inningsovers = matchscore["Innings 4"][3]

    def testmatch(self,rng,statsmatchtype,inningsorder, rain,simteams,simteamstats,matchscore,hometeam):

        if matchscore:
            tm.midinningssetup(self,matchscore)
        
        # Randomly set innings if not given
        if not inningsorder:
            # toss rng to decide inningsorder
            toss = rng.choice(simteams, p=[0.5,0.5],size=2, replace=False, shuffle=False).tolist()
            inningsorder = toss+toss
        
        if rain:
            rainaffected = rng.choice(["rain","no_rain"], p=[0.1,0.9],size=1, replace=False, shuffle=False)
        
        matchover = 0
        # skip to last matchscore overs
        if matchscore:
            thisover = self.inningsovers
            for eachscore in matchscore:
                matchover += matchscore[eachscore][3]
        # inningsnumber=0
        # innings generator
        for nthinnings, thisinnings in enumerate(inningsorder):
            if matchscore and nthinnings<(len(matchscore)-1):
                continue

            # inningsnumber+=1
            
            bowlingteam = None
            # nthinnings = inningsnumber-1

            # set bowling team
            for eachteam in inningsorder:
                if eachteam!=thisinnings:
                    bowlingteam = eachteam

            if matchover<450:
                # Innings based fallback probabilites
                inningswicketfallP,inningsscorefallP,inningsextrasfallP = tm.inningsfallbacks(self,nthinnings,thisinnings,bowlingteam,simteamstats)

            thisover=0
            # Innings overs generator
            while matchover<450:

                if (nthinnings == 3 and self.inningsscore > (self.matchresults["Innings 1 Score"][-1]+self.matchresults["Innings 3 Score"][-1]-self.matchresults["Innings 2 Score"][-1])) or (nthinnings==2 and (((self.inningsscore+self.matchresults["Innings 1 Score"][-1]-self.matchresults["Innings 2 Score"][-1])/(450-matchover))>4)):
                    break

                # Over based p-values
                # Batter Score p-values 
                scoreP, extrasP = tm.oversrunsPs(self,nthinnings,thisinnings, bowlingteam,simteamstats,thisover,hometeam)

                # Over based wicket p-values
                wicketfallP = tm.overswicketsPs(self,nthinnings,thisinnings, bowlingteam,simteamstats,thisover,hometeam)

                # print(wicketfallP)
                if len(wicketfallP)<2 or sum(wicketfallP)!=1:
                    wicketfallP=inningswicketfallP
                if len(scoreP)==0 or sum(scoreP)!=1:
                    scoreP=inningsscorefallP
                if len(extrasP)==0 or sum(extrasP)!=1:
                    extrasP=inningsextrasfallP

                # Fix if p-values don't have all possibilites
                if len(scoreP)<7:
                    scoreP = tm.redistributepvalues(self,scoreP)

                # Over generator
                tm.over(self,rng,wicketfallP,scoreP, extrasP,nthinnings,statsmatchtype,thisover)

                if self.inningswickets==10 or (nthinnings == 3 and self.inningsscore > (self.matchresults["Innings 1 Score"][-1]+self.matchresults["Innings 3 Score"][-1]-self.matchresults["Innings 2 Score"][-1])) or (nthinnings==2 and (((self.inningsscore+self.matchresults["Innings 1 Score"][-1]-self.matchresults["Innings 2 Score"][-1])/(450-matchover))>4)):
                    break

                thisover +=1
                matchover +=1

                # rain rng
                if rain:
                    if rainaffected=="rain":
                        rain=False
                        rainaffected="no_rain"
                        overslost = rng.integers(low=15, high=60)
                        matchover+=overslost
            
            #print(thisover)

            # Record innings results
            if self.inningsovers==0:
                self.inningsovers= thisover
            self.matchresults[f"Innings {nthinnings+1} Team"].append(thisinnings)
            self.matchresults[f"Innings {nthinnings+1} Wickets"].append(self.inningswickets)
            self.matchresults[f"Innings {nthinnings+1} Score"].append(self.inningsscore)
            self.matchresults[f"Innings {nthinnings+1} Overs"].append(self.inningsovers)
            tm.resetinningstally(self)
        
        # print(f"Overs left: {450-matchover}")

        # Record match winners
        if (self.matchresults["Innings 1 Score"][-1]+self.matchresults["Innings 3 Score"][-1])>(self.matchresults["Innings 2 Score"][-1]+self.matchresults["Innings 4 Score"][-1]) and (self.matchresults["Innings 4 Wickets"][-1]<10):
                    self.matchresults["Winner"].append("Draw")
        if (self.matchresults["Innings 1 Score"][-1]+self.matchresults["Innings 3 Score"][-1])>(self.matchresults["Innings 2 Score"][-1]+self.matchresults["Innings 4 Score"][-1]) and (self.matchresults["Innings 4 Wickets"][-1]==10):
            self.matchresults["Winner"].append(self.matchresults["Innings 1 Team"][-1])
        if (self.matchresults["Innings 1 Score"][-1]+self.matchresults["Innings 3 Score"][-1])<(self.matchresults["Innings 2 Score"][-1]+self.matchresults["Innings 4 Score"][-1]):
            self.matchresults["Winner"].append(self.matchresults["Innings 2 Team"][-1])
        if (self.matchresults["Innings 1 Score"][-1]+self.matchresults["Innings 3 Score"][-1])==(self.matchresults["Innings 2 Score"][-1]+self.matchresults["Innings 4 Score"][-1]):
            self.matchresults["Winner"].append("Tie")

        # Record match results in return value
        for eachresult in self.results:
            self.results[eachresult].extend(self.matchresults[eachresult])






        