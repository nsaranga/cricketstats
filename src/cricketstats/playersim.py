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
from timeit import timeit
import pandas as pd
import numpy as np
import multiprocessing as mp
import time
from cricketstats import cricketstats


# TODO record player's scores and balls faced
# TODO fix bowler's runs
# TODO add bowling order, or some mechanism to pick specific bowlers, yeah



class playersim:
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
        simplayers=[]
        for eachteam in self.simteams:
            for eachlist in self.simteams[eachteam]:
                simplayers.extend(self.simteams[eachteam][eachlist])

        searchmatchtypes={"T20": ["T20"], "ODI": ["ODI","ODM"],"ODM": ["ODI","ODM"],"Test": ["Test","MDM"],"MDM": ["Test","MDM"]} 

        self.simteamstats = cricketstats.search(players=simplayers)
        self.simteamstats.stats(database=statsdatabase, from_date=statsfrom_date, to_date=statsto_date, matchtype=searchmatchtypes[statsmatchtype], betweenovers=[], innings=[], sex=[statssex], playersteams=[], oppositionbatters=[], oppositionbowlers=[], oppositionteams=[], venue=[], event=[], matchresult=[], superover=None, battingposition=[], bowlingposition=[], fielders=[], sumstats=False)

    def playerP(self,nthinnings,thisinnings, bowlingteam,simteams,simteamstats,thisover,hometeam):

        if hometeam==thisinnings:
            batadv=0.55
            bowladv=1-batadv
        if hometeam==bowlingteam:
            bowladv=0.55
            batadv=1-bowladv
        if hometeam==None:
            batadv=0.5
            bowladv=0.5

        # wicket probabilites
        # wicketfallP = {self.batters[0]:
        # (simteamstats.ballresult['Out/NotOut'].loc[(simteamstats.ballresult["Batter"]==self.batters[0])&(simteamstats.ballresult["Innings Type"]=="Batting")&(simteamstats.ballresult["Balls Faced"]<(self.battersstats[self.batters[0]]+6))&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False)*batadv).add(
        #     simteamstats.ballresult['Out/NotOut'].loc[(simteamstats.ballresult["Bowler"].isin(simteams[bowlingteam]["bowlers"]))&(simteamstats.ballresult["Innings Type"]=="Bowling")&(simteamstats.ballresult["Innings Ball"]>(thisover))&(simteamstats.ballresult["Innings Ball"]<(thisover+1))&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False)*bowladv,fill_value=0)
        # ,
        # self.batters[1]: 
        # (simteamstats.ballresult['Out/NotOut'].loc[(simteamstats.ballresult["Batter"]==self.batters[1])&(simteamstats.ballresult["Innings Type"]=="Batting")&(simteamstats.ballresult["Balls Faced"]<(self.battersstats[self.batters[0]]+6))&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False)*batadv).add(
        #     simteamstats.ballresult['Out/NotOut'].loc[(simteamstats.ballresult["Bowler"].isin(simteams[bowlingteam]["bowlers"]))&(simteamstats.ballresult["Innings Type"]=="Bowling")&(simteamstats.ballresult["Innings Ball"]>(thisover))&(simteamstats.ballresult["Innings Ball"]<(thisover+1))&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False)*bowladv,fill_value=0)
        # }

        # # wicket probability all innings fallback
        # if len(wicketfallP[self.batters[0]])<2 or sum(wicketfallP[self.batters[0]])<0.99:
        wicketfallP = {self.batters[0]:
        (simteamstats.ballresult['Out/NotOut'].loc[(simteamstats.ballresult["Batter"]==self.batters[0])&(simteamstats.ballresult["Innings Type"]=="Batting")&(simteamstats.ballresult["Balls Faced"]<(self.battersstats[self.batters[0]]+6))].value_counts(normalize=True,sort=False)*batadv).add(
            simteamstats.ballresult['Out/NotOut'].loc[(simteamstats.ballresult["Bowler"].isin(simteams[bowlingteam]["bowlers"]))&(simteamstats.ballresult["Innings Type"]=="Bowling")&(simteamstats.ballresult["Innings Ball"]>(thisover))&(simteamstats.ballresult["Innings Ball"]<(thisover+1))].value_counts(normalize=True,sort=False)*bowladv,fill_value=0)
        ,
        self.batters[1]: 
        (simteamstats.ballresult['Out/NotOut'].loc[(simteamstats.ballresult["Batter"]==self.batters[1])&(simteamstats.ballresult["Innings Type"]=="Batting")&(simteamstats.ballresult["Balls Faced"]<(self.battersstats[self.batters[0]]+6))].value_counts(normalize=True,sort=False)*batadv).add(
            simteamstats.ballresult['Out/NotOut'].loc[(simteamstats.ballresult["Bowler"].isin(simteams[bowlingteam]["bowlers"]))&(simteamstats.ballresult["Innings Type"]=="Bowling")&(simteamstats.ballresult["Innings Ball"]>(thisover))&(simteamstats.ballresult["Innings Ball"]<(thisover+1))].value_counts(normalize=True,sort=False)*bowladv,fill_value=0)
        }

        # Score probabilites
        # scoreP= {self.batters[0]:
        # (simteamstats.ballresult["Batter Score"].loc[(simteamstats.ballresult["Batter"]==self.batters[0])&(simteamstats.ballresult["Balls Faced"]<(self.battersstats[self.batters[0]]+6))&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False)*batadv).add(
        #     simteamstats.ballresult['Batter Score'].loc[(simteamstats.ballresult["Bowler"].isin(simteams[bowlingteam]["bowlers"]))&(simteamstats.ballresult["Innings Type"]=="Bowling")&(simteamstats.ballresult["Innings Ball"]>(thisover))&(simteamstats.ballresult["Innings Ball"]<(thisover+1))&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False)*bowladv,fill_value=0)
        # ,
        # self.batters[1]:
        # (simteamstats.ballresult["Batter Score"].loc[(simteamstats.ballresult["Batter"]==self.batters[1])&(simteamstats.ballresult["Balls Faced"]<(self.battersstats[self.batters[0]]+6))&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False)*batadv).add(
        #     simteamstats.ballresult['Batter Score'].loc[(simteamstats.ballresult["Bowler"].isin(simteams[bowlingteam]["bowlers"]))&(simteamstats.ballresult["Innings Type"]=="Bowling")&(simteamstats.ballresult["Innings Ball"]>(thisover))&(simteamstats.ballresult["Innings Ball"]<(thisover+1))&(simteamstats.ballresult["Innings"]==(nthinnings+1))].value_counts(normalize=True,sort=False)*bowladv,fill_value=0)
        # }
        # if len(scoreP[self.batters[0]])==0 or sum(scoreP[self.batters[0]])<0.99:
            #print(f"Innings {nthinnings}, {self.batters[0]}")
        scoreP= {self.batters[0]:
        (simteamstats.ballresult["Batter Score"].loc[(simteamstats.ballresult["Batter"]==self.batters[0])&(simteamstats.ballresult["Balls Faced"]<(self.battersstats[self.batters[0]]+6))].value_counts(normalize=True,sort=False)*batadv).add(
            simteamstats.ballresult['Batter Score'].loc[(simteamstats.ballresult["Bowler"].isin(simteams[bowlingteam]["bowlers"]))&(simteamstats.ballresult["Innings Type"]=="Bowling")&(simteamstats.ballresult["Innings Ball"]>(thisover))&(simteamstats.ballresult["Innings Ball"]<(thisover+1))].value_counts(normalize=True,sort=False)*bowladv,fill_value=0)
        ,
        self.batters[1]:
        (simteamstats.ballresult["Batter Score"].loc[(simteamstats.ballresult["Batter"]==self.batters[1])&(simteamstats.ballresult["Balls Faced"]<(self.battersstats[self.batters[0]]+6))].value_counts(normalize=True,sort=False)*batadv).add(
            simteamstats.ballresult['Batter Score'].loc[(simteamstats.ballresult["Bowler"].isin(simteams[bowlingteam]["bowlers"]))&(simteamstats.ballresult["Innings Type"]=="Bowling")&(simteamstats.ballresult["Innings Ball"]>(thisover))&(simteamstats.ballresult["Innings Ball"]<(thisover+1))].value_counts(normalize=True,sort=False)*bowladv,fill_value=0)
        }

        

        return wicketfallP,scoreP

    def extras(self,nthinnings,thisinnings, bowlingteam,simteams,simteamstats,thisover):

        extrasP= simteamstats.ballresult["Bowler Extras"].loc[(simteamstats.ballresult["Bowler"].isin(simteams[bowlingteam]["bowlers"]))&(simteamstats.ballresult["Innings Ball"]>(thisover))&(simteamstats.ballresult["Innings Ball"]<(thisover+1))].value_counts(normalize=True,sort=False)
        
        fieldingextrasP= simteamstats.ballresult["Fielding Extras"].loc[(simteamstats.ballresult["Bowler"].isin(simteams[bowlingteam]["bowlers"]))].value_counts(normalize=True,sort=False)

        return extrasP,fieldingextrasP

    def wicketfallbackplayersP(self,nthinnings,thisinnings, bowlingteam,simteams,simteamstats,thisover,hometeam):

        if hometeam==thisinnings:
            batadv=0.55
            bowladv=1-batadv
        if hometeam==bowlingteam:
            bowladv=0.55
            batadv=1-bowladv
        if hometeam==None:
            batadv=0.5
            bowladv=0.5

        inningswicketfallP = {
            self.batters[0]: (simteamstats.ballresult['Out/NotOut'].loc[(simteamstats.ballresult["Batter"]==self.batters[0])&(simteamstats.ballresult["Innings Type"]=="Batting")].value_counts(normalize=True,sort=False)*batadv).add(simteamstats.ballresult['Out/NotOut'].loc[(simteamstats.ballresult["Bowler"].isin(simteams[bowlingteam]["bowlers"]))&(simteamstats.ballresult["Innings Type"]=="Bowling")].value_counts(normalize=True,sort=False)*bowladv,fill_value=0)
            ,
            self.batters[1]: (simteamstats.ballresult['Out/NotOut'].loc[(simteamstats.ballresult["Batter"]==self.batters[1])&(simteamstats.ballresult["Innings Type"]=="Batting")].value_counts(normalize=True,sort=False)*batadv).add(simteamstats.ballresult['Out/NotOut'].loc[(simteamstats.ballresult["Bowler"].isin(simteams[bowlingteam]["bowlers"]))&(simteamstats.ballresult["Innings Type"]=="Bowling")].value_counts(normalize=True,sort=False)*bowladv,fill_value=0)
            }

        if len(inningswicketfallP[self.batters[0]])<2 or sum(inningswicketfallP[self.batters[0]])<0.99:
            inningswicketfallP={
                self.batters[0]: (simteamstats.ballresult['Out/NotOut'].loc[(simteamstats.ballresult["Batter"].isin(simteams[thisinnings]["battingorder"]))&(simteamstats.ballresult["Innings Type"]=="Batting")].value_counts(normalize=True,sort=False)*batadv).add(simteamstats.ballresult['Out/NotOut'].loc[(simteamstats.ballresult["Bowler"].isin(simteams[bowlingteam]["bowlers"]))&(simteamstats.ballresult["Innings Type"]=="Bowling")].value_counts(normalize=True,sort=False)*bowladv,fill_value=0)
                ,
                self.batters[1]: (simteamstats.ballresult['Out/NotOut'].loc[(simteamstats.ballresult["Batter"].isin(simteams[thisinnings]["battingorder"]))&(simteamstats.ballresult["Innings Type"]=="Batting")].value_counts(normalize=True,sort=False)*batadv).add(simteamstats.ballresult['Out/NotOut'].loc[(simteamstats.ballresult["Bowler"].isin(simteams[bowlingteam]["bowlers"]))&(simteamstats.ballresult["Innings Type"]=="Bowling")].value_counts(normalize=True,sort=False)*bowladv,fill_value=0)
                }

        return inningswicketfallP


    def scorefallbackplayersP(self,nthinnings,thisinnings, bowlingteam,simteams,simteamstats,thisover,hometeam):

        if hometeam==thisinnings:
            batadv=0.55
            bowladv=1-batadv
        if hometeam==bowlingteam:
            bowladv=0.55
            batadv=1-bowladv
        if hometeam==None:
            batadv=0.5
            bowladv=0.5

        inningsscorefallP = {
            self.batters[0]: (simteamstats.ballresult["Batter Score"].loc[(simteamstats.ballresult["Batter"]==self.batters[0])&(simteamstats.ballresult["Innings Type"]=="Batting")].value_counts(normalize=True,sort=False)*batadv).add(simteamstats.ballresult["Batter Score"].loc[(simteamstats.ballresult["Bowler"].isin(simteams[bowlingteam]["bowlers"]))&(simteamstats.ballresult["Innings Type"]=="Bowling")].value_counts(normalize=True,sort=False)*bowladv,fill_value=0)
            ,
            self.batters[1]: (simteamstats.ballresult["Batter Score"].loc[(simteamstats.ballresult["Batter"]==self.batters[1])&(simteamstats.ballresult["Innings Type"]=="Batting")].value_counts(normalize=True,sort=False)*batadv).add(simteamstats.ballresult["Batter Score"].loc[(simteamstats.ballresult["Bowler"].isin(simteams[bowlingteam]["bowlers"]))&(simteamstats.ballresult["Innings Type"]=="Bowling")].value_counts(normalize=True,sort=False)*bowladv,fill_value=0)
            }

        if len(inningsscorefallP[self.batters[0]])==0 or sum(inningsscorefallP[self.batters[0]])!=1:
            inningsscorefallP = {
                self.batters[0]: (simteamstats.ballresult["Batter Score"].loc[(simteamstats.ballresult["Batter"].isin(simteams[thisinnings]["battingorder"]))&(simteamstats.ballresult["Innings Type"]=="Batting")].value_counts(normalize=True,sort=False)*batadv).add(simteamstats.ballresult["Batter Score"].loc[(simteamstats.ballresult["Bowler"].isin(simteams[bowlingteam]["bowlers"]))&(simteamstats.ballresult["Innings Type"]=="Bowling")].value_counts(normalize=True,sort=False)*bowladv,fill_value=0)
                ,
                self.batters[1]: (simteamstats.ballresult["Batter Score"].loc[(simteamstats.ballresult["Batter"].isin(simteams[thisinnings]["battingorder"]))&(simteamstats.ballresult["Innings Type"]=="Batting")].value_counts(normalize=True,sort=False)*batadv).add(simteamstats.ballresult["Batter Score"].loc[(simteamstats.ballresult["Bowler"].isin(simteams[bowlingteam]["bowlers"]))&(simteamstats.ballresult["Innings Type"]=="Bowling")].value_counts(normalize=True,sort=False)*bowladv,fill_value=0)
                }
        
        return inningsscorefallP

    def extrasfallbackplayersP(self,nthinnings,thisinnings, bowlingteam,simteams,simteamstats,thisover,hometeam):

        extrasP= simteamstats.ballresult["Extras"].loc[(simteamstats.ballresult["Bowler"].isin(simteams[bowlingteam]["bowlers"]))].value_counts(normalize=True,sort=False)

        return extrasP

    def over(self,rng,nthinnings,thisinnings, bowlingteam,statsmatchtype,thisover,simteams,simteamstats,hometeam, wicketfallP,scoreP,extrasP, fieldingextrasP):


        
        # ball outcome generator
        legaldeliveries = 0
        while legaldeliveries < 6:
            
            if len(wicketfallP[self.batters[0]])<2 or sum(wicketfallP[self.batters[0]])<0.99:
                    wicketfallP=playersim.wicketfallbackplayersP(self,nthinnings,thisinnings,bowlingteam,simteams,simteamstats,thisover,hometeam)
            # Over based wicket rng
            wicket = rng.choice(wicketfallP[self.batters[0]].index, p=wicketfallP[self.batters[0]].tolist(), shuffle=False)
            

            if wicket=="Out":
                legaldeliveries += 1
                self.battersstats[self.batters[0]] += 1
                self.inningswickets += 1
                self.playersout.append(self.batters[0])

            if self.inningswickets == 10:
                self.inningsovers=float(f"{thisover}.{legaldeliveries}")
                break

            if wicket=="Out":
                self.batters[0]= simteams[thisinnings]["battingorder"][(self.inningswickets + 1)]
                self.battersstats[simteams[thisinnings]["battingorder"][(self.inningswickets + 1)]] = 0

                wicketfallP,scoreP = playersim.playerP(self,nthinnings,thisinnings,bowlingteam,simteams,simteamstats,thisover,hometeam)

                if len(wicketfallP[self.batters[0]])<2 or sum(wicketfallP[self.batters[0]])<0.99:
                    wicketfallP=playersim.wicketfallbackplayersP(self,nthinnings,thisinnings,bowlingteam,simteams,simteamstats,thisover,hometeam)

                if len(scoreP[self.batters[0]])==0 or sum(scoreP[self.batters[0]])<0.99:
                    scoreP=playersim.scorefallbackplayersP(self,nthinnings,thisinnings,bowlingteam,simteams,simteamstats,thisover,hometeam)

                # Fix if p-values don't have all possibilites
                if len(scoreP[self.batters[0]])>0 and len(scoreP[self.batters[0]])<7:
                    scoreP = playersim.redistributepvalues(self,scoreP)

            # Over based scoring rng
            if wicket=="Not Out":

                if len(scoreP[self.batters[0]])==0 or sum(scoreP[self.batters[0]])<0.99:
                    scoreP=playersim.scorefallbackplayersP(self,nthinnings,thisinnings,bowlingteam,simteams,simteamstats,thisover,hometeam)

                # Fix if p-values don't have all possibilites
                if len(scoreP[self.batters[0]])>0 and len(scoreP[self.batters[0]])<7:
                    scoreP = playersim.redistributepvalues(self,scoreP)

                #try:
                batterscore = rng.choice(scoreP[self.batters[0]].index, p=scoreP[self.batters[0]].tolist(), shuffle=False)
                # except:
                #     print(self.batters[0])

                if batterscore!=0:
                    extras = rng.choice(extrasP.index, p=extrasP.tolist(), shuffle=False)
                    self.inningsscore+=(batterscore+extras)
                    if extras==0:
                        legaldeliveries += 1
                        self.battersstats[self.batters[0]] += 1
                    if (batterscore)%2!=0:
                        self.batters.reverse()
                    if extras!=0:
                        self.battersstats[self.batters[0]] += 1
                if batterscore==0:
                    legaldeliveries += 1
                    self.battersstats[self.batters[0]] += 1
                    fieldingextras = rng.choice(fieldingextrasP.index, p=fieldingextrasP.tolist(), shuffle=False)
                    self.inningsscore += (fieldingextras)
                    if (fieldingextras)%2!=0:
                        self.batters.reverse()


            # Check if score has been chased
            if ((statsmatchtype == "T20" or statsmatchtype == "ODI" or statsmatchtype == "ODM") and (nthinnings == 1 and self.inningsscore > self.matchresults["Innings 1 Score"][-1])) or (statsmatchtype == "Test" and (self.inningswickets==10 or (nthinnings == 3 and self.inningsscore > (self.matchresults["Innings 1 Score"][-1]+self.matchresults["Innings 3 Score"][-1]-self.matchresults["Innings 2 Score"][-1])))):
                self.inningsovers=float(f"{thisover}.{legaldeliveries}")
                break
        

    def redistributepvalues(self,scoreP):
        # print(f"Before Modification: {scoreP}")
        lowestP = min(scoreP[self.batters[0]])
        scoreP[self.batters[0]]=scoreP[self.batters[0]] /(1+lowestP)
        newPs= (1-sum(scoreP[self.batters[0]]))/(7-len(scoreP[self.batters[0]]))
        # print(scoreP)
        scoreP[self.batters[0]]=scoreP[self.batters[0]].reindex([0,1,2,3,4,5,6],fill_value=newPs)
        # print(scoreP)
        # for eachvalue in scoreP[self.batters[0]].index:
        #     if pd.isna(scoreP[self.batters[0]][eachvalue]):
        #         scoreP[self.batters[0]][eachvalue]=newPs
        # print(scoreP)
        # print(f"ScoreP Sum: {sum(scoreP)}")
        return scoreP

    def resetinningstally(self):
        self.inningsscore = 0
        self.inningswickets = 0
        self.inningsovers = 0
        self.playersout=[]
        self.batters=[]
        self.battersstats={}

    def mcsimulations(self,statsmatchtype,simulations,inningsorder,rain,matchscore,hometeam):
        # print("Sims started")
        start = time.time()
        # setup random generator object
        rng = np.random.default_rng()
        # Set function dictionary
        # matchtypes={"T20": ld.limitedovers, "ODI": ld.limitedovers,"ODM": ld.limitedovers,"Test": tm.testmatch}
        classtypes={"T20": ld, "ODI": ld,"ODM": ld,"Test": tm}

        sim=classtypes[statsmatchtype]()

        sim.resultssetup()
        for thismatch in range(simulations):
            
            sim.matchresultssetup()
            # Function to simulate a match
            if statsmatchtype=="T20" or statsmatchtype=="ODI" or statsmatchtype=="ODM":
                sim.limitedovers(rng,statsmatchtype,inningsorder,rain,self.simteams,self.simteamstats,matchscore,hometeam,start)

            if statsmatchtype=="Test":
                sim.testmatch(rng,statsmatchtype,inningsorder,rain,self.simteams,self.simteamstats,matchscore,hometeam,start)

        return sim.results
            
    def sim(self, statsdatabase, statsfrom_date, statsto_date, statssex, statsmatchtype,simulations,inningsorder=None,rain=False,matchscore=None,hometeam=None, multicore=True):
        # Setup match results
        playersim.simresultssetup(self,statsmatchtype)

        # Search for pvalues
        playersim.pvaluesearch(self, statsdatabase, statsfrom_date, statsto_date, statssex, statsmatchtype)

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
            simprocs = procpool.starmap(playersim.mcsimulations,inputs)
            
            procpool.close()
            #print(f'Time after mcsimulations(): {time.time() - start}')

            for eachdict in simprocs:
                for eachlist in eachdict:
                    self.simresults[eachlist].extend(eachdict[eachlist])
            print("Sims finished")

            self.simresults=pd.DataFrame(self.simresults)

        if multicore==False:
            start = time.time()
            rng = np.random.default_rng()
            # print(f'Time after rng: {time.time() - start}')

            # Set function dictionary
            classtypes={"T20": ld, "ODI": ld,"ODM": ld,"Test": tm}

            sim=classtypes[statsmatchtype]()
            # simulation generator
            sim.resultssetup()
            for thismatch in range(simulations):
                sim.matchresultssetup()
                # Function to simulate a match
                if statsmatchtype=="T20" or statsmatchtype=="ODI" or statsmatchtype=="ODM":
                    sim.limitedovers(rng,statsmatchtype,inningsorder,rain,self.simteams,self.simteamstats,matchscore,hometeam,start)

                if statsmatchtype=="Test":
                    sim.testmatch(rng,statsmatchtype,inningsorder,rain,self.simteams,self.simteamstats,matchscore,hometeam,start)

            self.simresults=pd.DataFrame(sim.results)



class ld(playersim):
    def __init__(self) -> None:
        self.inningswickets = 0
        self.inningsscore = 0
        self.inningsovers = 0
        self.matchresults = None
        self.results = None
        self.batters=[]
        self.battersstats={}
        self.playersout = []

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

    def limitedovers(self,rng,statsmatchtype,inningsorder,rain,simteams,simteamstats,matchscore,hometeam,start):

        if matchscore:
            ld.midinningssetup(self,matchscore)

        # Randomly set innings order if not given
        if not inningsorder:
            # toss rng to decide inningsorder
            inningsorder = rng.choice(list(simteams.keys()), p=[0.5,0.5],size=2, replace=False, shuffle=False).tolist()

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

            # over generator
            for thisover in range(overs):
                # skip to last matchscore overs
                if matchscore and ((len(matchscore)==1 and thisover<(matchscore["Innings 1"][3])) or (len(matchscore)==2 and thisover<(matchscore["Innings 2"][3]))):
                    continue

                if self.inningswickets == 10 or (nthinnings == 1 and self.inningsscore > self.matchresults["Innings 1 Score"][-1]):
                    break
                
                self.batters.reverse()
                if not self.batters:
                    self.batters = simteams[thisinnings]["battingorder"][0:2]
                    for eachbatter in self.batters:
                        self.battersstats[eachbatter] = 0

                wicketfallP,scoreP = playersim.playerP(self,nthinnings,thisinnings,bowlingteam,simteams,simteamstats,thisover,hometeam)
                
                # Fix if p-values don't have all possibilites
                if len(scoreP[self.batters[0]])>0 and len(scoreP[self.batters[0]])<7:
                    scoreP = playersim.redistributepvalues(self,scoreP)

                if len(wicketfallP[self.batters[0]])<2 or sum(wicketfallP[self.batters[0]])<0.99:
                    wicketfallP=playersim.wicketfallbackplayersP(self,nthinnings,thisinnings,bowlingteam,simteams,simteamstats,thisover,hometeam)

                if len(scoreP[self.batters[0]])==0 or sum(scoreP[self.batters[0]])<0.99:
                    scoreP=playersim.scorefallbackplayersP(self,nthinnings,thisinnings,bowlingteam,simteams,simteamstats,thisover,hometeam)

                extrasP, fieldingextrasP = ld.extras(self,nthinnings,thisinnings, bowlingteam,simteams,simteamstats,thisover)
                if len(extrasP)==0 or sum(extrasP)<0.99:
                    extrasP=playersim.extrasfallbackplayersP(self,nthinnings,thisinnings,bowlingteam,simteams,simteamstats,thisover,hometeam)
                
                ld.over(self,rng,nthinnings,thisinnings, bowlingteam,statsmatchtype,thisover,simteams,simteamstats,hometeam,wicketfallP,scoreP,extrasP, fieldingextrasP)

                if self.inningswickets == 10 or (nthinnings == 1 and self.inningsscore > self.matchresults["Innings 1 Score"][-1]) or (self.inningswickets+1) == len(simteams[thisinnings]["battingorder"]):
                    break
                self.inningsovers+=1

            if self.inningsovers==0:
                self.inningsovers=overs
            self.matchresults[f"Innings {nthinnings+1} Team"].append(thisinnings)
            self.matchresults[f"Innings {nthinnings+1} Wickets"].append(self.inningswickets)
            self.matchresults[f"Innings {nthinnings+1} Score"].append(self.inningsscore)
            self.matchresults[f"Innings {nthinnings+1} Overs"].append(self.inningsovers)
            # print(self.battersstats)
            ld.resetinningstally(self)

        
        if self.matchresults["Innings 1 Score"][-1]>self.matchresults["Innings 2 Score"][-1]:
            self.matchresults["Winner"].append(self.matchresults["Innings 1 Team"][-1])
        if self.matchresults["Innings 1 Score"][-1]<self.matchresults["Innings 2 Score"][-1]:
            self.matchresults["Winner"].append(self.matchresults["Innings 2 Team"][-1])
        if self.matchresults["Innings 1 Score"][-1]==self.matchresults["Innings 2 Score"][-1]:
            self.matchresults["Winner"].append("Tie")
        for eachresult in self.results:
            self.results[eachresult].extend(self.matchresults[eachresult])

class tm(playersim):
    def __init__(self) -> None:
        self.inningswickets = 0
        self.inningsscore = 0
        self.inningsovers = 0
        self.matchresults = None
        self.results = None
        self.batters=[]
        self.battersstats={}
        self.playersout = []

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

    def testmatch(self,rng,statsmatchtype,inningsorder,rain,simteams,simteamstats,matchscore,hometeam,start):

        if matchscore:
            tm.midinningssetup(self,matchscore)
        
        # Randomly set innings if not given
        if not inningsorder:
            # toss rng to decide inningsorder
            toss = rng.choice(list(simteams.keys()), p=[0.5,0.5],size=2, replace=False, shuffle=False).tolist()
            inningsorder = toss+toss
        if len(inningsorder)==2:
            inningsorder = [inningsorder[0],inningsorder[1],inningsorder[0],inningsorder[1]]

        
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

            # set bowling team
            bowlingteam = None
            for eachteam in inningsorder:
                if eachteam!=thisinnings:
                    bowlingteam = eachteam

            thisover=0
            # Innings overs generator
            
            while matchover<450:

                if (nthinnings == 3 and self.inningsscore > (self.matchresults["Innings 1 Score"][-1]+self.matchresults["Innings 3 Score"][-1]-self.matchresults["Innings 2 Score"][-1])) or (nthinnings==0 and (((self.inningsscore)/(450-matchover))>2)) or (nthinnings==1 and (((self.inningsscore-self.matchresults["Innings 1 Score"][-1])/(450-matchover))>2)) or (nthinnings==2 and (((self.inningsscore+self.matchresults["Innings 1 Score"][-1]-self.matchresults["Innings 2 Score"][-1])/(450-matchover))>4)):
                    break

                self.batters.reverse()
                if not self.batters:
                    self.batters = simteams[thisinnings]["battingorder"][0:2]
                    for eachbatter in self.batters:
                        self.battersstats[eachbatter] = 0

                wicketfallP,scoreP = playersim.playerP(self,nthinnings,thisinnings,bowlingteam,simteams,simteamstats,thisover,hometeam)
                # Fix if p-values don't have all possibilites
                if len(scoreP[self.batters[0]])>0 and len(scoreP[self.batters[0]])<7:
                    scoreP = playersim.redistributepvalues(self,scoreP)

                if len(wicketfallP[self.batters[0]])<2 or sum(wicketfallP[self.batters[0]])<0.99:
                    wicketfallP=playersim.wicketfallbackplayersP(self,nthinnings,thisinnings,bowlingteam,simteams,simteamstats,thisover,hometeam)

                if len(scoreP[self.batters[0]])==0 or sum(scoreP[self.batters[0]])<0.99:
                    scoreP=playersim.scorefallbackplayersP(self,nthinnings,thisinnings,bowlingteam,simteams,simteamstats,thisover,hometeam)

                extrasP, fieldingextrasP = ld.extras(self,nthinnings,thisinnings, bowlingteam,simteams,simteamstats,thisover)
                if len(extrasP)==0 or sum(extrasP)<0.99:
                    extrasP=playersim.extrasfallbackplayersP(self,nthinnings,thisinnings,bowlingteam,simteams,simteamstats,thisover,hometeam,)
                #print(f'Time after beforeover: {time.time() - start}')
                # Over generator
                tm.over(self,rng,nthinnings,thisinnings, bowlingteam,statsmatchtype,thisover,simteams,simteamstats,hometeam,wicketfallP,scoreP,extrasP, fieldingextrasP)

                # print(f'Time after afterover: {time.time() - start}')

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
        #print(self.matchresults)
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
