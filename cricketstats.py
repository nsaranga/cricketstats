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

from datetime import datetime
import json
import time
import pandas as pd
import os
import zipfile
import numpy as np
import math
import importlib

import statsprocessor
import index

# for reverse lookup, I need to look for stats. One way is to write a new type of search with new class and get stats func. Other way is to write function that lists every player for a particular stat and inputs subset of tha tlist into getstats(). Maybe another way is first create a list/index of all players in the database. delete duplicates. then input that list into getstatsfunc.
# I for this I need a new function that just opens each match in a given period and creates dictionary for players and gets innings.


class search:
    def __init__(self, players=None, teams=None, result=None, inningsresult=None) -> None:
        self.players = players
        self.teams = teams
        self.result = result
        self.inningsresult = inningsresult

    # Setup the statistics to be recorded.
    def resultsetup(self):
        if self.players:
            self.inningsresult = { 
            "Date":[], "Match Type":[], "Venue":[], "Players":[], "Team":[], "Opposition":[], "Innings":[], 
            "Scores": [],"Balls Faced": [], 
            "Batting S/R":[], "Runs/Ball":[], "First Boundary Ball":[], 
            "Runsgiven": [], "Wickets": [], "Overs Bowled": [], 
            'Economy Rate': [], 'Bowling Avg': [], 'Bowling S/R': [], "Runsgiven/Ball":[], "Avg Consecutive Dot Balls":[]}

            self.result = {}
            for eachplayer in self.players:
                self.result[eachplayer] = {"Players": eachplayer, "Games": 0, "Won": 0, "Drawn": 0, 'Win %': 0,

                                            "Innings Batted": 0, "batinningscount": False,
                                            "inningsruns": [], "inningsballsfaced": 0,
                                            "firstboundary": [],
                                            "Runs": 0, "Fours": 0, "Sixes": 0, "Dot Balls": 0, "Balls Faced": 0, "Outs": 0, 
                                            "Bowled Outs": 0, "LBW Outs": 0, "Caught Outs": 0, "Stumped Outs": 0, "Run Outs": 0, 
                                            "totalstos": 0, "totalstosopp": 0, 
                                            'Dot Ball %': 0, 'Strike Turnover %': 0, 'Batting S/R': 0, 'Batting S/R MeanAD': 0, 'Batting Avg': 0, "Mean Score":0, 'Score MeanAD': 0, 'Boundary %': 0, "Runs/Ball":0,
                                            'Avg First Boundary Ball': 0,
                                            
                                            "Innings Bowled":0, "bowlinningscount": False,
                                            "inningsrunsgiven": [], "inningsballsbowled": 0, "inningswickets": 0,
                                            "Runsgiven": 0, "Foursgiven": 0, "Sixesgiven": 0, 
                                            "Wickets": 0, "Balls Bowled": 0, "Extras": 0, "No Balls": 0, "Wides":0,
                                            "Dot Balls Bowled": 0, 
                                            "Bowleds": 0, "LBWs": 0, "Hitwickets": 0, "Caughts": 0, "Stumpeds": 0,
                                            "totalstosgiven": 0, "totalstosgivenopp": 0, 
                                            "Catches": 0, "Runouts": 0, "Stumpings": 0, 
                                            'Economy Rate': 0, 'Economy Rate MeanAD': 0, 'Dot Ball Bowled %': 0,'Boundary Given %': 0, 'Bowling Avg': 0, "Bowling Avg MeanAD": 0, 'Bowling S/R': 0, "Bowling S/R MeanAD": 0,  "Runsgiven/Ball":0, "dotballseries": [], "Avg Consecutive Dot Balls": 0}

        if self.teams:
            self.inningsresult = {
            "Date":[], "Match Type":[],"Venue":[],"Teams":[], "Opposition":[], "Innings":[], 
            "Defended Scores": [], "Chased Scores": [], "Margins":[], 
            "Scores": [],"Outs": [], "Overs Faced": [], 
            "Runs/Outs":[], "Runs/Ball":[], "Run Rate":[], "First Boundary Ball":[], 
            "Runsgiven": [], "Wickets": [], "Overs Bowled": [], 
            'Runsgiven/Wicket': [], "Runsgiven/Ball":[], 'Runsgiven Rate': [], "Avg Consecutive Dot Balls":[]}

            self.result = {}
            for eachteam in self.teams:
                self.result[eachteam] = {"Teams": eachteam, "Games": 0, "Innings Bowled":0, "bowlinningscount": False, "Innings Batted": 0,
                                        "batinningscount": False, "Won": 0, "Drawn": 0, 'Win %': 0, "Defended Wins": 0, "Chased Wins": 0, 
                                        "Net Boundary %":0, "Net Run Rate":0,
                                        
                                        "inningsruns": [], "inningsballsfaced": 0, "inningsouts": 0, "firstboundary": [],
                                        # "Runmargins": [], "Wicketmargins": [], "Overs Chased": [],
                                        "Runs": 0, "Fours": 0, "Sixes": 0, "Dot Balls": 0, "Outs": 0, "Balls Faced": 0, 
                                        "Bowled Outs": 0, "LBW Outs": 0, "Caught Outs": 0, "Stumped Outs": 0, "Run Outs": 0,
                                        "Runs/Outs":0, "Runs/Ball":0, "Run Rate":0, 'Avg First Boundary Ball': 0,
                                        'Dot Ball %': 0, 'Score MeanAD': 0, 'Boundary %': 0, 
                                        
                                        "inningsrunsgiven": [], "inningsballsbowled": 0, "inningswickets": 0, 
                                        "Runsgiven": 0, "Foursgiven": 0, "Sixesgiven": 0, 
                                        "Wickets": 0, "Balls Bowled": 0, "Extras": 0, "No Balls": 0, "Wides":0, "Byes": 0, "Leg Byes": 0, "Dot Balls Bowled": 0, 
                                        "Bowleds": 0, "LBWs": 0, "Hitwickets": 0,  "Caughts": 0, "Runouts": 0, "Stumpeds": 0, 
                                        'Dot Ball Bowled %': 0,'Boundary Given %': 0,'Runsgiven/Wicket': 0, "Runsgiven/Ball":0, "Runsgiven Rate": 0,
                                        "Avg Consecutive Dot Balls": 0, "dotballseries": []}
    
    # Indexes matches by match type for quick search.
    def fileindexing(self, database, matches):
        currentdir = os.path.dirname(os.path.abspath(__file__))
        databasemtime = os.path.getmtime(database)
        databasetime = time.gmtime(databasemtime)
        databaseyear = int(databasetime[0])
        if index.matchindex['indexedtime'] == 0:
            newmatchindex = {"file": "", 'indexedtime': 0, "matches":{"Test": {}, "MDM":{}, "ODI":{}, "ODM": {}, "T20":{}, "IT20":{}}}
            for eachmatchtype in newmatchindex["matches"]:
                for eachyear in range(2000, (databaseyear + 1)):
                    newmatchindex["matches"][eachmatchtype][f"{eachyear}"] = []
            file = open(f"{currentdir}/index.py", "w")
            file.write("matchindex = " + repr(newmatchindex))
            file.close()
            importlib.reload(index)

        if os.path.getmtime(database) > index.matchindex['indexedtime']:
            print("It looks like your database is newer than the index, please wait while the new matches in the database are indexed.")
            matchindex = index.matchindex
            matchindex['indexedtime'] = os.path.getmtime(database)
            matchindex['file'] = matches.filename
            filelist = matches.namelist()
            for eachfile in filelist:
                if ".json" not in eachfile:
                    continue
                matchdata = matches.open(eachfile)
                match = json.load(matchdata)
                if eachfile not in matchindex["matches"][match["info"]["match_type"]][match["info"]["dates"][0][:4]]:
                    matchindex["matches"][match["info"]["match_type"]][match["info"]["dates"][0][:4]].append(eachfile)
                matchdata.close
            
            file = open(f"{currentdir}/index.py", "w")
            file.write("matchindex = " + repr(matchindex))
            file.close()
        if os.path.getmtime(database) < index.matchindex['indexedtime']:
            raise Exception("Your cricsheet database is older than the index, please download the newest zip file from https://cricsheet.org/downloads/all_json.zip")
            
    # Record games played, wins, draws
    def gamesandwins(self, matchplayers, matchoutcome, matchteams):
        if self.players:
            for eachplayer in self.players:
                for eachteam in matchplayers:
                    if eachplayer in matchplayers[eachteam]:
                        self.result[eachplayer]["Games"] += 1
                        if "result" in matchoutcome and matchoutcome['result'] == "draw":
                            self.result[eachplayer]["Drawn"] += 1
                        if "winner" in matchoutcome and eachteam == matchoutcome["winner"]:
                            self.result[eachplayer]["Won"] += 1

        if self.teams:
            for eachteam in matchteams:
                if eachteam not in self.teams:
                    continue
                self.result[eachteam]["Games"] += 1
                if "result" in matchoutcome and matchoutcome['result'] == "draw":
                    self.result[eachteam]["Drawn"] += 1
                if "winner" in matchoutcome and eachteam in matchoutcome["winner"]:
                    self.result[matchoutcome
                                ["winner"]]["Won"] += 1
    
    # Setup innings lists 
    def setupinningscores(self):
        if self.players:
            for eachplayer in self.players:
                self.result[eachplayer]["batinningscount"] = False
                self.result[eachplayer]["inningsruns"] = []
                self.result[eachplayer]["inningsballsfaced"] = 0
                self.result[eachplayer]["bowlinningscount"] = False
                self.result[eachplayer]["inningsrunsgiven"] = []
                self.result[eachplayer]["inningsballsbowled"] = 0
                self.result[eachplayer]["inningswickets"] = 0
        if self.teams:
            for eachteam in self.teams:
                self.result[eachteam]["batinningscount"] = False
                self.result[eachteam]["inningsouts"] = 0
                self.result[eachteam]["inningsruns"] = []
                self.result[eachteam]["inningsballsfaced"] = 0
                self.result[eachteam]["bowlinningscount"] = False
                self.result[eachteam]["inningswickets"] = 0
                self.result[eachteam]["inningsrunsgiven"] = []
                self.result[eachteam]["inningsballsbowled"] = 0

    # Record striker's stats for each ball.
    def strikerstats(self, eachball):
        if eachball['batter'] in self.players:
            self.result[eachball['batter']]["batinningscount"] = True
        self.result[eachball['batter']
                    ]["Runs"] += eachball['runs']['batter']
        self.result[eachball['batter']]["inningsruns"].append(
            eachball['runs']['batter'])
        if eachball['runs']['batter'] == 4:
            self.result[eachball['batter']
                        ]["Fours"] += 1
        if eachball['runs']['batter'] == 6:
            self.result[eachball['batter']
                        ]["Sixes"] += 1
        if eachball['runs']['total'] == 0:
            self.result[eachball['batter']
                        ]["Dot Balls"] += 1
        if "extras" not in eachball:
            self.result[eachball['batter']
                        ]["Balls Faced"] += 1
            self.result[eachball['batter']
                        ]["inningsballsfaced"] += 1
        if "extras" in eachball:
            if not ("wides" in eachball['extras'] or "noballs" in eachball['extras']):
                self.result[eachball['batter']
                            ]["Balls Faced"] += 1
                self.result[eachball['batter']
                            ]["inningsballsfaced"] += 1
        if "wickets" in eachball:
            for eachwicket in eachball["wickets"]:
                self.result[eachball['batter']
                            ]["Outs"] += 1
                if eachwicket["kind"] == "bowled":
                    self.result[eachball['batter']
                                ]["Bowled Outs"] += 1
                if eachwicket["kind"] == "lbw":
                    self.result[eachball['batter']
                                ]["LBW Outs"] += 1
                if eachwicket["kind"] == "caught":
                    self.result[eachball['batter']
                                ]["Caught Outs"] += 1
                if eachwicket["kind"] == "stumped":
                    self.result[eachball['batter']
                                ]["Stumped Outs"] += 1
                if eachwicket["kind"] == "run out":
                    self.result[eachball['batter']
                                ]["Run Outs"] += 1

    # Record non-strikers's stats for each ball. 
    def nonstrikerstats(self, eachball, oppositionbowlers):
        self.result[eachball["non_striker"]]["batinningscount"] = True
        for eachwicket in eachball["wickets"]:
            if eachball['non_striker'] == eachwicket["player_out"] and not oppositionbowlers:
                self.result[eachball['non_striker']
                            ]["Outs"] += 1
                if eachwicket["kind"] == "run out":
                    self.result[eachball['non_striker']
                                ]["Run Outs"] += 1

    # Record strike turn over rstats for striker. 
    def striketurnoverstats(self, eachball, case1, case2):
        if eachball['batter'] in self.players:
            self.result[eachball['batter']
                        ]["totalstosopp"] += 1
            if eachball['runs']['batter'] == case1 or eachball['runs']['batter'] == case2:
                self.result[eachball['batter']]["totalstos"] += 1
            if "extras" in eachball:
                if not ("wides" in eachball['extras'] or "noballs" in eachball['extras']) and (eachball['runs']['extras'] == case1 or eachball['runs']['extras'] == case2):
                    self.result[eachball['batter']]["totalstos"] += 1
        if eachball['bowler'] in self.players:
            self.result[eachball['bowler']
                        ]["totalstosgivenopp"] += 1
            if eachball['runs']['batter'] == case1 or eachball['runs']['batter'] == case2:
                self.result[eachball['bowler']
                            ]["totalstosgiven"] += 1
            if "extras" in eachball:
                if not ("wides" in eachball['extras'] or "noballs" in eachball['extras']) and (eachball['runs']['extras'] == case1 or eachball['runs']['extras'] == case2):
                    self.result[eachball['bowler']
                            ]["totalstosgiven"] += 1
    
    # Record bowler's stats
    def bowlerstats(self, eachball, fielders):
        if eachball['bowler'] in self.players:
            self.result[eachball['bowler']]["bowlinningscount"] = True
        self.result[eachball['bowler']
                    ]["Runsgiven"] += eachball['runs']['batter']
        if eachball['runs']['batter'] == 4:
            self.result[eachball['bowler']
                        ]["Foursgiven"] += 1
        if eachball['runs']['batter'] == 6:
            self.result[eachball['bowler']
                        ]["Sixesgiven"] += 1
        if eachball['runs']['total'] == 0:
            self.result[eachball['bowler']
                        ]["Dot Balls Bowled"] += 1
        if "extras" not in eachball:
            self.result[eachball['bowler']
                        ]["Balls Bowled"] += 1
            self.result[eachball['bowler']
                        ]["inningsballsbowled"] += 1
            self.result[eachball['bowler']]["inningsrunsgiven"].append(
            eachball['runs']['batter'])
        if "extras" in eachball:
            if not ("wides" in eachball['extras'] or "noballs" in eachball['extras']):
                self.result[eachball['bowler']
                            ]["Balls Bowled"] += 1
                self.result[eachball['bowler']
                            ]["inningsballsbowled"] += 1
            if "wides" in eachball['extras']:
                self.result[eachball['bowler']
                            ]["Runsgiven"] += eachball['extras']['wides']
                self.result[eachball['bowler']
                            ]["Wides"] += eachball['extras']['wides']
                self.result[eachball['bowler']
                            ]["Extras"] += eachball['extras']['wides']
                self.result[eachball['bowler']]["inningsrunsgiven"].append((
            eachball['runs']['batter'] + eachball['extras']['wides']))
            if "noballs" in eachball['extras']:
                self.result[eachball['bowler']
                            ]["Runsgiven"] += eachball['extras']['noballs']
                self.result[eachball['bowler']
                            ]["No Balls"] += eachball['extras']['noballs']
                self.result[eachball['bowler']
                            ]["Extras"] += eachball['extras']['noballs']
                self.result[eachball['bowler']]["inningsrunsgiven"].append((
            eachball['runs']['batter'] + eachball['extras']['noballs']))
        if "wickets" in eachball:
            for eachwicket in eachball["wickets"]:
                if any([eachwicket["kind"] == "bowled", eachwicket["kind"] == "lbw",
                        eachwicket["kind"] == "hit wicket", eachwicket["kind"] == "caught",
                        eachwicket["kind"] == "stumped"]):
                    self.result[eachball['bowler']
                                ]["Wickets"] += 1
                    self.result[eachball['bowler']
                                ]["inningswickets"] += 1
                if eachwicket["kind"] == "bowled":
                    self.result[eachball['bowler']
                                ]["Bowleds"] += 1
                if eachwicket["kind"] == "lbw":
                    self.result[eachball['bowler']
                                ]["LBWs"] += 1
                if eachwicket["kind"] == "hit wicket":
                    self.result[eachball['bowler']
                                ]["Hitwickets"] += 1
                if eachwicket["kind"] == "caught" and (not fielders or (fielders and (eachwicket["fielders"]["name"] in fielders))):
                    self.result[eachball['bowler']
                                ]["Caughts"] += 1
                if eachwicket["kind"] == "stumped":
                    self.result[eachball['bowler']
                                ]["Stumpeds"] += 1
    
    # Record fieling stats for players.
    def fieldingstats(self, eachball):
        for eachwicket in eachball["wickets"]:
            if "fielders" in eachwicket:
                for eachfielder in eachwicket["fielders"]:
                    if "name" not in eachfielder:
                        continue
                    if eachfielder["name"] in self.players:
                        if eachwicket["kind"] == "caught":
                            self.result[eachfielder["name"]
                                        ]["Catches"] += 1
                        if eachwicket["kind"] == "stumped":
                            self.result[eachfielder["name"]
                                        ]["Stumpings"] += 1
                        if eachwicket["kind"] == "run out":
                            self.result[eachfielder["name"]
                                        ]["Runouts"] += 1

    # Record team's batting stats
    def teambattingstats(self, eachball, inningsteam):
        self.result[inningsteam]["batinningscount"] = True
        self.result[inningsteam]["inningsruns"].append(
            eachball['runs']['total'])
        self.result[inningsteam
                    ]["Runs"] += eachball['runs']['total']
        if eachball['runs']['batter'] == 4:
            self.result[inningsteam]["Fours"] += 1
        if eachball['runs']['batter'] == 6:
            self.result[inningsteam]["Sixes"] += 1
        if eachball['runs']['total'] == 0:
            self.result[inningsteam
                        ]["Dot Balls"] += 1
        if "extras" not in eachball:
            self.result[inningsteam
                        ]["Balls Faced"] += 1
            self.result[inningsteam
                        ]["inningsballsfaced"] += 1
        if "extras" in eachball:
            if not ("wides" in eachball['extras'] or "noballs" in eachball['extras']):
                self.result[inningsteam
                            ]["Balls Faced"] += 1
                self.result[inningsteam
                            ]["inningsballsfaced"] += 1
        if "wickets" in eachball:
            for eachwicket in eachball["wickets"]:
                self.result[inningsteam
                            ]["Outs"] += 1
                self.result[inningsteam
                            ]["inningsouts"] += 1
                if eachwicket["kind"] == "bowled":
                    self.result[inningsteam]["Bowled Outs"] += 1
                if eachwicket["kind"] == "lbw":
                    self.result[inningsteam]["LBW Outs"] += 1
                if eachwicket["kind"] == "caught":
                    self.result[inningsteam]["Caught Outs"] += 1
                if eachwicket["kind"] == "stumped":
                    self.result[inningsteam]["Stumped Outs"] += 1
                if eachwicket["kind"] == "run out":
                    self.result[inningsteam]["Run Outs"] += 1

    # Record team's bowling stats
    def teambowlingstats(self, eachball, inningsteam):
        self.result[inningsteam]["bowlinningscount"] = True
        self.result[inningsteam]["inningsrunsgiven"].append(
            eachball['runs']['total'])
        self.result[inningsteam]["Runsgiven"] += eachball['runs']['total']
        if eachball['runs']['batter'] == 4:
            self.result[inningsteam]["Foursgiven"] += 1
        if eachball['runs']['batter'] == 6:
            self.result[inningsteam]["Sixesgiven"] += 1
        if eachball['runs']['total'] == 0:
            self.result[inningsteam]["Dot Balls Bowled"] += 1
        if "extras" not in eachball:
            self.result[inningsteam]["Balls Bowled"] += 1
            self.result[inningsteam]["inningsballsbowled"] += 1
        if "extras" in eachball:
            if "wides" in eachball['extras']:
                self.result[inningsteam]["Wides"] += eachball['extras']['wides']
                self.result[inningsteam]["Extras"] += eachball['extras']['wides']
            if "noballs" in eachball['extras']:
                self.result[inningsteam]["No Balls"] += eachball['extras']['noballs']
                self.result[inningsteam]["Extras"] += eachball['extras']['noballs']
            if "byes" in eachball['extras']:
                self.result[inningsteam]["Balls Bowled"] += 1
                self.result[inningsteam]["inningsballsbowled"] += 1
                self.result[inningsteam]["Byes"] += eachball['extras']['byes']
                self.result[inningsteam]["Extras"] += eachball['extras']['byes']
            if "legbyes" in eachball['extras']:
                self.result[inningsteam]["Balls Bowled"] += 1
                self.result[inningsteam]["inningsballsbowled"] += 1
                self.result[inningsteam]["Leg Byes"] += eachball['extras']['legbyes']
                self.result[inningsteam]["Extras"] += eachball['extras']['legbyes']
        if "wickets" in eachball:
            for eachwicket in eachball["wickets"]:
                self.result[inningsteam]["inningswickets"] += 1
                self.result[inningsteam]["Wickets"] += 1
                if eachwicket["kind"] == "bowled":
                    self.result[inningsteam]["Bowleds"] += 1
                if eachwicket["kind"] == "lbw":
                    self.result[inningsteam]["LBWs"] += 1
                if eachwicket["kind"] == "hit wicket":
                    self.result[inningsteam]["Hitwickets"] += 1
                if eachwicket["kind"] == "caught":
                    self.result[inningsteam]["Caughts"] += 1
                if eachwicket["kind"] == "stumped":
                    self.result[inningsteam]["Stumpeds"] += 1
                if eachwicket["kind"] == "run out":
                    self.result[inningsteam]["Runouts"] += 1
    
    # Record player's innings stats
    def playerinnings(self, matchtimetuple, matchplayers, nthinnings, eachmatchtype,matchvenue):
        for eachplayer in self.result:
            for eachteam in matchplayers:
                if eachplayer in matchplayers[eachteam]:
                    playersteam = eachteam
                if eachplayer not in matchplayers[eachteam]:
                    oppositionteam = eachteam

            if self.result[eachplayer]["batinningscount"] == True:
                self.result[eachplayer]["Innings Batted"] += 1
                if 4 in self.result[eachplayer]["inningsruns"] or 6 in self.result[eachplayer]["inningsruns"]:
                    self.result[eachplayer]["firstboundary"].append(statsprocessor.firstboundary(self.result[eachplayer]["inningsruns"]))

                self.inningsresult["Players"].append(eachplayer)
                self.inningsresult["Venue"].append(matchvenue)
                self.inningsresult["Date"].append(datetime(matchtimetuple[0], matchtimetuple[1], matchtimetuple[2]))
                self.inningsresult["Match Type"].append(eachmatchtype)
                self.inningsresult["Team"].append(playersteam)
                self.inningsresult["Opposition"].append(oppositionteam)
                self.inningsresult["Innings"].append(nthinnings + 1)

                self.inningsresult["Scores"].append(
                    sum(self.result[eachplayer]["inningsruns"]))
                self.inningsresult["Balls Faced"].append(
                    self.result[eachplayer]["inningsballsfaced"])
                self.inningsresult["Batting S/R"].append(statsprocessor.ratio(sum(self.result[eachplayer]["inningsruns"]), self.result[eachplayer]["inningsballsfaced"], multiplier=100))
                self.inningsresult["Runs/Ball"].append(statsprocessor.ratio(sum(self.result[eachplayer]["inningsruns"]), self.result[eachplayer]["inningsballsfaced"]))
                self.inningsresult["First Boundary Ball"].append(statsprocessor.firstboundary(
                    self.result[eachplayer]["inningsruns"]))

                self.inningsresult["Runsgiven"].append(None)
                self.inningsresult["Wickets"].append(None)
                self.inningsresult["Overs Bowled"].append(None)
                self.inningsresult["Economy Rate"].append(None)
                self.inningsresult["Bowling Avg"].append(None)
                self.inningsresult["Bowling S/R"].append(None)
                self.inningsresult["Runsgiven/Ball"].append(None)
                self.inningsresult["Avg Consecutive Dot Balls"].append(None)

            if self.result[eachplayer]["bowlinningscount"] == True:
                self.result[eachplayer]["Innings Bowled"] += 1
                self.result[eachplayer]["dotballseries"].extend(statsprocessor.dotballseries(self.result[eachplayer]["inningsrunsgiven"]))
                self.inningsresult["Players"].append(eachplayer)
                self.inningsresult["Venue"].append(matchvenue)
                self.inningsresult["Date"].append(datetime(matchtimetuple[0], matchtimetuple[1], matchtimetuple[2]))
                self.inningsresult["Match Type"].append(eachmatchtype)
                self.inningsresult["Team"].append(playersteam)
                self.inningsresult["Opposition"].append(oppositionteam)
                self.inningsresult["Innings"].append(nthinnings + 1)

                self.inningsresult["Scores"].append(None)
                self.inningsresult["Balls Faced"].append(None)
                self.inningsresult["Batting S/R"].append(None)
                self.inningsresult["Runs/Ball"].append(None)
                self.inningsresult["First Boundary Ball"].append(None)

                self.inningsresult["Runsgiven"].append(
                    sum(self.result[eachplayer]["inningsrunsgiven"]))
                self.inningsresult["Wickets"].append(
                    self.result[eachplayer]["inningswickets"])
                self.inningsresult["Overs Bowled"].append(
                    math.ceil(self.result[eachplayer]["inningsballsbowled"] / 6))
                if self.result[eachplayer]["inningsrunsgiven"]:
                    self.inningsresult["Economy Rate"].append(round(sum(self.result[eachplayer]["inningsrunsgiven"]) / (math.ceil(self.result[eachplayer]["inningsballsbowled"] / 6)),2))
                    self.inningsresult["Runsgiven/Ball"].append(statsprocessor.ratio(sum(self.result[eachplayer]["inningsrunsgiven"]), self.result[eachplayer]["inningsballsbowled"]))
                if not self.result[eachplayer]["inningsrunsgiven"]:
                    self.inningsresult["Economy Rate"].append(None)
                    self.inningsresult["Runsgiven/Ball"].append(None)
                if self.result[eachplayer]["inningswickets"]:
                    self.inningsresult["Bowling Avg"].append(round(
                        sum(self.result[eachplayer]["inningsrunsgiven"]) / 
                        self.result[eachplayer]["inningswickets"],2))
                    self.inningsresult["Bowling S/R"].append(round(self.result[eachplayer]["inningsballsbowled"] / self.result[eachplayer]["inningswickets"],2))
                if not self.result[eachplayer]["inningswickets"]:
                    self.inningsresult["Bowling Avg"].append(None)
                    self.inningsresult["Bowling S/R"].append(None)
                if 0 in self.result[eachplayer]["inningsrunsgiven"]:
                    self.inningsresult["Avg Consecutive Dot Balls"].append(round(np.mean(statsprocessor.dotballseries(self.result[eachplayer]["inningsrunsgiven"]))))
                if 0 not in self.result[eachplayer]["inningsrunsgiven"]:
                    self.inningsresult["Avg Consecutive Dot Balls"].append(0)
                
    
    # Record team's batting innings
    def teambattinginnings(self, inningsteam, nthinnings, matchteams, matchtimetuple, matchoutcome, matchinnings, eachmatchtype, matchvenue):
        for eachteam in matchteams:
            if eachteam != inningsteam:
                bowlingteam = eachteam
        if 4 in self.result[inningsteam]["inningsruns"] or 6 in self.result[inningsteam]["inningsruns"]:
            self.result[inningsteam]["firstboundary"].append(statsprocessor.firstboundary(self.result[inningsteam]["inningsruns"]))
        if self.result[inningsteam]["batinningscount"] == True:
             self.result[inningsteam]["Innings Batted"] += 1

        self.inningsresult["Teams"].append(inningsteam)
        self.inningsresult["Venue"].append(matchvenue)
        self.inningsresult["Date"].append(datetime(matchtimetuple[0], matchtimetuple[1], matchtimetuple[2]))
        self.inningsresult["Match Type"].append(eachmatchtype)
        self.inningsresult["Opposition"].append(bowlingteam)
        self.inningsresult["Innings"].append(nthinnings + 1)

        self.inningsresult["Scores"].append(
            sum(self.result[inningsteam]["inningsruns"]))
        self.inningsresult["Outs"].append(self.result[inningsteam]["inningsouts"])
        self.inningsresult["Overs Faced"].append(
            math.ceil(self.result[inningsteam]["inningsballsfaced"]/6))
        if self.result[inningsteam]["inningsouts"] > 0:
            self.inningsresult["Runs/Outs"].append(statsprocessor.ratio(sum(self.result[inningsteam]["inningsruns"]), self.result[inningsteam]["inningsouts"]))
        if self.result[inningsteam]["inningsouts"]==0:
            self.inningsresult["Runs/Outs"].append(
            sum(self.result[inningsteam]["inningsruns"]))
        self.inningsresult["Runs/Ball"].append(statsprocessor.ratio(sum(self.result[inningsteam]["inningsruns"]), self.result[inningsteam]["inningsballsfaced"]))
        self.inningsresult["Run Rate"].append(statsprocessor.ratio(sum(self.result[inningsteam]["inningsruns"]), self.result[inningsteam]["inningsballsfaced"], multiplier=6))
        self.inningsresult["First Boundary Ball"].append(statsprocessor.firstboundary(
            self.result[inningsteam]["inningsruns"]))
            
        self.inningsresult["Runsgiven"].append(None)
        self.inningsresult["Wickets"].append(None)
        self.inningsresult["Overs Bowled"].append(None)
        self.inningsresult["Runsgiven/Wicket"].append(None)
        self.inningsresult["Runsgiven/Ball"].append(None)
        self.inningsresult["Runsgiven Rate"].append(None)
        self.inningsresult["Avg Consecutive Dot Balls"].append(None)

        # Recording Succesfully Chased Scores
        if nthinnings == (len(matchinnings) - 1):
            if "result" not in matchoutcome and matchoutcome["winner"] == inningsteam:
                if "by" in matchoutcome and "wickets" in matchoutcome["by"]:
                    self.result[inningsteam]["Chased Wins"] += 1
                    self.inningsresult["Chased Scores"].append(sum(self.result[matchoutcome["winner"]]["inningsruns"]))
                    self.inningsresult["Defended Scores"].append(None)
                    self.inningsresult["Margins"].append(matchoutcome['by']['wickets'])
                if "by" not in matchoutcome or "runs" in matchoutcome["by"]:
                    self.inningsresult["Defended Scores"].append(None)
                    self.inningsresult["Chased Scores"].append(None)
                    self.inningsresult["Margins"].append(None)
            if "result" in matchoutcome or matchoutcome["winner"] != inningsteam:
                self.inningsresult["Defended Scores"].append(None)
                self.inningsresult["Chased Scores"].append(None)
                self.inningsresult["Margins"].append(None)
        if nthinnings != (len(matchinnings) - 1):
            self.inningsresult["Defended Scores"].append(None)
            self.inningsresult["Chased Scores"].append(None)
            self.inningsresult["Margins"].append(None)

        # print("Inn", len(self.inningsresult["Innings"]))
        # print(nthinnings +1)
        # print("Def", len(self.inningsresult["Defended Scores"]))
        # print("Cha", len(self.inningsresult["Chased Scores"]))

        # self.inningsresult["Margins"].append(None)

    # Record team's bowling innings
    def teambowlinginnings(self, eachteam, battingteam, matchtimetuple, nthinnings, matchoutcome, matchinnings, eachmatchtype, matchvenue):

        self.result[eachteam]["dotballseries"].extend(statsprocessor.dotballseries(self.result[eachteam]["inningsrunsgiven"]))
        if self.result[eachteam]["bowlinningscount"] == True:
            self.result[eachteam]["Innings Bowled"] += 1

        self.inningsresult["Teams"].append(eachteam)
        self.inningsresult["Venue"].append(matchvenue)
        self.inningsresult["Date"].append(datetime(matchtimetuple[0], matchtimetuple[1], matchtimetuple[2]))
        self.inningsresult["Match Type"].append(eachmatchtype)
        self.inningsresult["Opposition"].append(battingteam)
        self.inningsresult["Innings"].append(nthinnings + 1)

        self.inningsresult["Scores"].append(None)
        self.inningsresult["Outs"].append(None)
        self.inningsresult["Overs Faced"].append(None)
        self.inningsresult["Runs/Outs"].append(None)
        self.inningsresult["Runs/Ball"].append(None)
        self.inningsresult["Run Rate"].append(None)
        self.inningsresult["First Boundary Ball"].append(None)
            
        self.inningsresult["Runsgiven"].append(
            sum(self.result[eachteam]["inningsrunsgiven"]))
        self.inningsresult["Wickets"].append(self.result[eachteam]["inningswickets"])
        self.inningsresult["Overs Bowled"].append(
            math.ceil(self.result[eachteam]["inningsballsbowled"]/6))
        if self.result[eachteam]["inningswickets"] > 0:
            self.inningsresult["Runsgiven/Wicket"].append(statsprocessor.ratio(sum(self.result[eachteam]["inningsrunsgiven"]), self.result[eachteam]["inningswickets"]))
        if self.result[eachteam]["inningswickets"]==0:
            self.inningsresult["Runsgiven/Wicket"].append(
            sum(self.result[eachteam]["inningsrunsgiven"]))
        self.inningsresult["Runsgiven/Ball"].append(statsprocessor.ratio(sum(self.result[eachteam]["inningsrunsgiven"]), self.result[eachteam]["inningsballsbowled"]))
        self.inningsresult["Runsgiven Rate"].append(statsprocessor.ratio(sum(self.result[eachteam]["inningsrunsgiven"]), self.result[eachteam]["inningsballsbowled"], multiplier=6))
        if 0 in self.result[eachteam]["inningsrunsgiven"]:
            self.inningsresult["Avg Consecutive Dot Balls"].append(round(np.mean(statsprocessor.dotballseries(self.result[eachteam]["inningsrunsgiven"]))))
        if 0 not in self.result[eachteam]["inningsrunsgiven"]:
             self.inningsresult["Avg Consecutive Dot Balls"].append(0)
        
        # Recording Succesfully Defended Scores
        if nthinnings == (len(matchinnings) - 1):
            if "result" not in matchoutcome and matchoutcome["winner"] == eachteam:
                if "by" in matchoutcome and "runs" in matchoutcome["by"]:
                    self.result[eachteam]["Defended Wins"] += 1
                    self.inningsresult["Defended Scores"].append(sum(self.result[matchoutcome["winner"]]["inningsrunsgiven"]) + matchoutcome['by']['runs'])
                    self.inningsresult["Chased Scores"].append(None)
                    self.inningsresult["Margins"].append(matchoutcome['by']['runs'])
                if "by" not in matchoutcome or "wickets" in matchoutcome["by"]:
                    self.inningsresult["Defended Scores"].append(None)
                    self.inningsresult["Chased Scores"].append(None)
                    self.inningsresult["Margins"].append(None)
            if "result" in matchoutcome or matchoutcome["winner"] != eachteam:
                self.inningsresult["Defended Scores"].append(None)
                self.inningsresult["Chased Scores"].append(None)
                self.inningsresult["Margins"].append(None)
        if nthinnings != (len(matchinnings) - 1):
            self.inningsresult["Defended Scores"].append(None)
            self.inningsresult["Chased Scores"].append(None)
            self.inningsresult["Margins"].append(None)
        
        # print(nthinnings +1)
        # print("Def", len(self.inningsresult["Defended Scores"]))
        # print("Cha", len(self.inningsresult["Chased Scores"]))
        # self.inningsresult["Margins"].append(None)

    # Record successful scores
    def successfulscores(self, matchoutcome, matchinnings, nthinnings, inningsteam):
        if "by" in matchoutcome and "runs" in matchoutcome["by"]:
            if "target" in matchinnings[1]:
                self.result[matchoutcome["winner"]]["Defended Scores"].append(
                    matchinnings[1]['target']['runs'] - 1)
            if "target" not in matchinnings[1] and nthinnings == (len(matchinnings) - 1) and matchoutcome["winner"] != inningsteam:
                self.result[matchoutcome["winner"]]["Defended Scores"].append(
                    (sum(
                        self.result[matchoutcome["winner"]]["inningsrunsgiven"]))
                    + matchoutcome['by']['runs'])
            self.result[matchoutcome["winner"]]["Runmargins"].append(matchoutcome['by']['runs'])
        if "by" in matchoutcome and 'wickets' in matchoutcome['by']:
            if "target" in matchinnings[1]:
                self.result[matchoutcome["winner"]]["Chased Scores"].append(
                    matchinnings[1]['target']['runs'])
                self.result[matchoutcome["winner"]]["Overs Chased"].append(
                    round(self.result[matchoutcome["winner"]]["inningsballsfaced"] / 6))
            if "target" not in matchinnings[1] and nthinnings == (len(matchinnings) - 1) and matchoutcome["winner"] == inningsteam:
                self.result[matchoutcome["winner"]]["Chased Scores"].append(
                    (sum(self.result[matchoutcome["winner"]]["inningsruns"])))
                self.result[matchoutcome["winner"]]["Overs Chased"].append(
                    round(self.result[matchoutcome["winner"]]["inningsballsfaced"] / 6))
            self.result[matchoutcome["winner"]]["Wicketmargins"].append(
                matchoutcome['by']['wickets'])

    # Calculate and record stats derived from basic stats
    def derivedstats(self):
        if self.players:
            for eachplayer in self.result:
                if self.result[eachplayer]["Games"] > 0:
                    self.result[eachplayer]["Win %"] = statsprocessor.ratio(self.result[eachplayer]["Won"],self.result[eachplayer]["Games"],multiplier=100)

                if self.result[eachplayer]["Balls Faced"] > 0:
                    self.result[eachplayer]["Runs/Ball"] = statsprocessor.ratio(self.result[eachplayer]["Runs"],self.result[eachplayer]["Balls Faced"])
                    self.result[eachplayer]["Batting S/R"] = statsprocessor.ratio(self.result[eachplayer]["Runs"], self.result[eachplayer]["Balls Faced"], multiplier=100)
                    self.result[eachplayer]["Boundary %"] = statsprocessor.ratio(
                        (self.result[eachplayer]["Fours"]
                        + self.result[eachplayer]["Sixes"]),
                        self.result[eachplayer]["Balls Faced"], multiplier=100)
                    self.result[eachplayer]["Dot Ball %"] = statsprocessor.ratio(self.result[eachplayer]["Dot Balls"],self.result[eachplayer]["Balls Faced"], multiplier=100)
                if self.result[eachplayer]["firstboundary"]:
                    self.result[eachplayer]["Avg First Boundary Ball"] = round(statsprocessor.ratio(sum(self.result[eachplayer]["firstboundary"]), len(self.result[eachplayer]["firstboundary"])))

                if self.result[eachplayer]["totalstosopp"] > 0:
                    self.result[eachplayer]["Strike Turnover %"] = statsprocessor.ratio(self.result[eachplayer]["totalstos"], self.result[eachplayer]["totalstosopp"], multiplier=100)

                if len(self.inningsresult.loc[self.inningsresult["Players"]==eachplayer, "Balls Faced"].dropna().index) > 0:
                    self.result[eachplayer]["Batting S/R MeanAD"] = round(self.inningsresult.loc[self.inningsresult["Players"]==eachplayer, "Batting S/R"].mad(), 2)

                if len(self.inningsresult.loc[self.inningsresult["Players"]==eachplayer, "Scores"].dropna().index) > 0:
                    self.result[eachplayer]["Mean Score"] = round(self.inningsresult.loc[self.inningsresult["Players"]==eachplayer, "Scores"].mean(),2)
                    self.result[eachplayer]["Score MeanAD"] = round(self.inningsresult.loc[self.inningsresult["Players"]==eachplayer, "Scores"].mad(),2)

                if self.result[eachplayer]["Outs"] > 0:
                    self.result[eachplayer]["Batting Avg"] = statsprocessor.ratio(self.result[eachplayer]["Runs"],self.result[eachplayer]["Outs"], multiplier=0)

                if self.result[eachplayer]["Balls Bowled"] > 0:
                    self.result[eachplayer]["Runsgiven/Ball"] = statsprocessor.ratio(self.result[eachplayer]["Runsgiven"], self.result[eachplayer]["Balls Bowled"])
                    self.result[eachplayer]["Economy Rate"] = statsprocessor.ratio(
                        self.result[eachplayer]["Runsgiven"], self.result[eachplayer]["Balls Bowled"],
                        multiplier=6)
                    self.result[eachplayer]["Dot Ball Bowled %"] = statsprocessor.ratio(
                        self.result[eachplayer]["Dot Balls Bowled"], self.result[eachplayer]["Balls Bowled"],
                        multiplier=100)
                    self.result[eachplayer]["Boundary Given %"] = statsprocessor.ratio(
                        (self.result[eachplayer]["Foursgiven"]
                        + self.result[eachplayer]["Sixesgiven"]),
                        self.result[eachplayer]["Balls Bowled"], multiplier=100)
                if self.result[eachplayer]["dotballseries"]:
                    self.result[eachplayer]["Avg Consecutive Dot Balls"] = round(np.mean(self.result[eachplayer]["dotballseries"]))

                if len(self.inningsresult.loc[self.inningsresult["Players"]==eachplayer, "Overs Bowled"].dropna().index) > 0:
                    self.result[eachplayer]["Economy Rate MeanAD"] = round(self.inningsresult.loc[self.inningsresult["Players"]==eachplayer, "Economy Rate"].mad(),2)

                if len(self.inningsresult.loc[self.inningsresult["Players"]==eachplayer, "Wickets"].dropna().index) > 0:
                    self.result[eachplayer]["Bowling Avg MeanAD"] = round(self.inningsresult.loc[self.inningsresult["Players"]==eachplayer, "Bowling Avg"].mad(),2)

                if len(self.inningsresult.loc[self.inningsresult["Players"]==eachplayer, "Wickets"].dropna().index) > 0:
                    self.result[eachplayer]["Bowling S/R MeanAD"] = round(self.inningsresult.loc[self.inningsresult["Players"]==eachplayer, "Bowling S/R"].mad(),2)

                if self.result[eachplayer]["Wickets"] > 0:
                    self.result[eachplayer]["Bowling Avg"] = statsprocessor.ratio(
                        self.result[eachplayer]["Runsgiven"], self.result[eachplayer]["Wickets"], multiplier=0)
                    self.result[eachplayer]["Bowling S/R"] = statsprocessor.ratio(
                        self.result[eachplayer]["Balls Bowled"], self.result[eachplayer]["Wickets"], multiplier=0)

            
        if self.teams:
            for eachteam in self.result:
                if self.result[eachteam]["Games"] > 0:
                    self.result[eachteam]["Win %"] = statsprocessor.ratio(self.result[eachteam]["Won"],self.result[eachteam]["Games"],multiplier=100)
                if self.result[eachteam]["Balls Faced"] > 0:
                    self.result[eachteam]["Runs/Ball"] = statsprocessor.ratio(self.result[eachteam]["Runs"],self.result[eachteam]["Balls Faced"])
                    self.result[eachteam]["Boundary %"] = statsprocessor.ratio((self.result[eachteam]["Fours"] + self.result[eachteam]["Sixes"]),
                        self.result[eachteam]["Balls Faced"], multiplier=100)
                    self.result[eachteam]["Dot Ball %"] = statsprocessor.ratio(self.result[eachteam]["Dot Balls"],self.result[eachteam]["Balls Faced"], multiplier=100)

                    self.result[eachteam]["Run Rate"] = statsprocessor.ratio(self.result[eachteam]["Runs"], self.result[eachteam]["Balls Faced"], multiplier=6)

                if self.result[eachteam]["firstboundary"]:
                    self.result[eachteam]["Avg First Boundary Ball"] = round(np.mean(self.result[eachteam]["firstboundary"]))

                if self.result[eachteam]["Outs"] > 0:
                    self.result[eachteam]["Runs/Ball"] = statsprocessor.ratio(self.result[eachteam]["Runs"],self.result[eachteam]["Outs"])

                if len(self.inningsresult.loc[self.inningsresult["Teams"]==eachteam, "Overs Faced"].dropna().index) > 0:
                    self.result[eachteam]["Run Rate MeanAD"]=round(self.inningsresult.loc[self.inningsresult["Teams"]==eachteam, "Run Rate"].mad(), 2)

                if len(self.inningsresult.loc[self.inningsresult["Teams"]==eachteam, "Scores"].dropna().index) > 0:
                    self.result[eachteam]["Score MeanAD"]=round(self.inningsresult.loc[self.inningsresult["Teams"]==eachteam, "Scores"].mad(), 2) 
                    self.result[eachteam]["Mean Score"]=round(self.inningsresult.loc[self.inningsresult["Teams"]==eachteam, "Scores"].mean(), 2)

                if self.result[eachteam]["Balls Bowled"] > 0:
                    self.result[eachteam]["Runsgiven/Ball"] = statsprocessor.ratio(
                        self.result[eachteam]["Runsgiven"], self.result[eachteam]["Balls Bowled"])
                    self.result[eachteam]["Dot Ball Bowled %"] = statsprocessor.ratio(
                        self.result[eachteam]["Dot Balls Bowled"], self.result[eachteam]["Balls Bowled"],
                        multiplier=100)
                    self.result[eachteam]["Boundary Given %"] = statsprocessor.ratio(
                        (self.result[eachteam]["Foursgiven"]
                        + self.result[eachteam]["Sixesgiven"]),
                        self.result[eachteam]["Balls Bowled"], multiplier=100)
                    self.result[eachteam]["Runsgiven Rate"] = statsprocessor.ratio(self.result[eachteam]["Runsgiven"], self.result[eachteam]["Balls Bowled"], multiplier=6)
                
                if len(self.inningsresult.loc[self.inningsresult["Teams"]==eachteam, "Overs Bowled"].dropna().index) > 0:
                    self.result[eachteam]["Runsgiven Rate MeanAD"] = round(self.inningsresult.loc[self.inningsresult["Teams"]==eachteam, "Runsgiven Rate"].mad(), 2)

                if self.result[eachteam]["Wickets"] > 0:
                    self.result[eachteam]['Runsgiven/Wicket'] = statsprocessor.ratio(
                        self.result[eachteam]["Runsgiven"], self.result[eachteam]["Wickets"])
                
                if self.result[eachteam]["dotballseries"]:
                    self.result[eachteam]["Avg Consecutive Dot Balls"] = round(np.mean(self.result[eachteam]["dotballseries"]))

                self.result[eachteam]["Net Run Rate"] = self.result[eachteam]["Run Rate"] - self.result[eachteam]["Runsgiven Rate"]
                self.result[eachteam]["Net Boundary %"] = self.result[eachteam]["Boundary %"] - self.result[eachteam]["Boundary Given %"]

    # Sum and record stats from all players and teams in a search
    def sumstats(self, allgamesplayed, allgameswinloss, allgamesdrawn):    
        if self.players:
            self.result["All Players"] = {}
            for eachstat in self.result[self.players[0]].keys():
                if eachstat == "Players":
                    self.result["All Players"][eachstat] = "All Players"
                if type(self.result[self.players[0]][eachstat]) == int:
                    self.result["All Players"][eachstat] = 0
                if type(self.result[self.players[0]][eachstat]) == list:
                    self.result["All Players"][eachstat] = []
            
            for eachstat in self.result["All Players"]:
                if type(self.result["All Players"][eachstat]) == int:
                    for eachplayer in self.players:
                        self.result["All Players"][eachstat] += self.result[eachplayer][eachstat]
                if type(self.result["All Players"][eachstat]) == list:
                    for eachplayer in self.players:
                        self.result["All Players"][eachstat].extend(self.result[eachplayer][eachstat])
        if self.teams:
            self.result["All Teams"] = {}
            for eachstat in self.result[self.teams[0]].keys():
                if eachstat == "Teams":
                    self.result["All Teams"][eachstat] = "All Teams"
                if type(self.result[self.teams[0]][eachstat]) == int:
                    self.result["All Teams"][eachstat] = 0
                if type(self.result[self.teams[0]][eachstat]) == list:
                    self.result["All Teams"][eachstat] = []
            
            for eachstat in self.result["All Teams"]:
                if type(self.result["All Teams"][eachstat]) == int:
                    for eachteam in self.teams:
                        self.result["All Teams"][eachstat] += self.result[eachteam][eachstat]
                if type(self.result["All Teams"][eachstat]) == list:
                    for eachteam in self.teams:
                        self.result["All Teams"][eachstat].extend(self.result[eachteam][eachstat])
                if eachstat == "Games":
                    self.result["All Teams"][eachstat] = allgamesplayed
                if eachstat == "Won":
                    self.result["All Teams"][eachstat] = allgameswinloss
                if eachstat == "Drawn":
                    self.result["All Teams"][eachstat] = allgamesdrawn
        
        if "All Players" in self.result:
            eachplayer = "All Players"
            if self.result[eachplayer]["Games"] > 0:
                self.result[eachplayer]["Win %"] = statsprocessor.ratio(self.result[eachplayer]["Won"],self.result[eachplayer]["Games"],multiplier=100)

            if self.result[eachplayer]["Balls Faced"] > 0:
                self.result[eachplayer]["Runs/Ball"] = statsprocessor.ratio(self.result[eachplayer]["Runs"],self.result[eachplayer]["Balls Faced"])
                self.result[eachplayer]["Batting S/R"] = statsprocessor.ratio(self.result[eachplayer]["Runs"], self.result[eachplayer]["Balls Faced"], multiplier=100)
                self.result[eachplayer]["Boundary %"] = statsprocessor.ratio(
                    (self.result[eachplayer]["Fours"]
                    + self.result[eachplayer]["Sixes"]),
                    self.result[eachplayer]["Balls Faced"], multiplier=100)
                self.result[eachplayer]["Dot Ball %"] = statsprocessor.ratio(self.result[eachplayer]["Dot Balls"],self.result[eachplayer]["Balls Faced"], multiplier=100)
            if self.result[eachplayer]["firstboundary"]:
                self.result[eachplayer]["Avg First Boundary Ball"] = round(np.mean(self.result[eachplayer]["firstboundary"]))

            if self.result[eachplayer]["totalstosopp"] > 0:
                self.result[eachplayer]["Strike Turnover %"] = statsprocessor.ratio(self.result[eachplayer]["totalstos"], self.result[eachplayer]["totalstosopp"], multiplier=100)

            if len(self.inningsresult["Batting S/R"].dropna().index) > 0:
                self.result[eachplayer]["Batting S/R MeanAD"] = round(self.inningsresult["Batting S/R"].mad(), 2)
            if len(self.inningsresult["Batting S/R"].dropna().index) == 0:
                self.result[eachplayer]["Batting S/R MeanAD"] = 0

            if len(self.inningsresult["Scores"].dropna().index) > 0:
                self.result[eachplayer]["Mean Score"] = round(self.inningsresult["Scores"].mean(),2)
                self.result[eachplayer]["Score MeanAD"] = round(self.inningsresult["Scores"].mad(),2)
            if len(self.inningsresult["Scores"].dropna().index) == 0:
                self.result[eachplayer]["Mean Score"] = 0
                self.result[eachplayer]["Score MeanAD"] = 0

            if self.result[eachplayer]["Outs"] > 0:
                self.result[eachplayer]["Batting Avg"] = statsprocessor.ratio(self.result[eachplayer]["Runs"],self.result[eachplayer]["Outs"], multiplier=0)

            if self.result[eachplayer]["Balls Bowled"] > 0:
                self.result[eachplayer]["Runsgiven/Ball"] = statsprocessor.ratio(self.result[eachplayer]["Runsgiven"], self.result[eachplayer]["Balls Bowled"])
                self.result[eachplayer]["Economy Rate"] = statsprocessor.ratio(
                    self.result[eachplayer]["Runsgiven"], self.result[eachplayer]["Balls Bowled"],
                    multiplier=6)
                self.result[eachplayer]["Dot Ball Bowled %"] = statsprocessor.ratio(
                    self.result[eachplayer]["Dot Balls Bowled"], self.result[eachplayer]["Balls Bowled"],
                    multiplier=100)
                self.result[eachplayer]["Boundary Given %"] = statsprocessor.ratio(
                    (self.result[eachplayer]["Foursgiven"]
                    + self.result[eachplayer]["Sixesgiven"]),
                    self.result[eachplayer]["Balls Bowled"], multiplier=100)
            if self.result[eachplayer]["dotballseries"]:
                self.result[eachplayer]["Avg Consecutive Dot Balls"] = round(
                    np.mean(self.result[eachplayer]["dotballseries"]))

            if len(self.inningsresult["Overs Bowled"].dropna().index) > 0:
                self.result[eachplayer]["Economy Rate MeanAD"] = round(self.inningsresult["Economy Rate"].mad(),2)
            if len(self.inningsresult["Overs Bowled"].dropna().index) == 0:
                self.result[eachplayer]["Economy Rate MeanAD"] = 0

            if len(self.inningsresult["Wickets"].dropna().index) > 0:
                self.result[eachplayer]["Bowling Avg MeanAD"] = round(self.inningsresult["Bowling Avg"].mad(),2)
            if len(self.inningsresult["Wickets"].dropna().index) == 0:
                self.result[eachplayer]["Bowling Avg MeanAD"] = 0

            if len(self.inningsresult["Bowling S/R"].dropna().index) > 0:
                self.result[eachplayer]["Bowling S/R MeanAD"] = round(self.inningsresult["Bowling S/R"].mad(),2)
            if len(self.inningsresult["Bowling S/R"].dropna().index) == 0:
                self.result[eachplayer]["Bowling S/R MeanAD"] = 0

            if self.result[eachplayer]["Wickets"] > 0:
                self.result[eachplayer]["Bowling Avg"] = statsprocessor.ratio(
                    self.result[eachplayer]["Runsgiven"], self.result[eachplayer]["Wickets"], multiplier=0)
                self.result[eachplayer]["Bowling S/R"] = statsprocessor.ratio(
                    self.result[eachplayer]["Balls Bowled"], self.result[eachplayer]["Wickets"], multiplier=0)
        
        if "All Teams" in self.result:
            eachteam = "All Teams"

            # For averaging stats
            if self.result[eachteam]["Games"] > 0:
                # self.result[eachteam]["Win %"] = statsprocessor.ratio(self.result[eachteam]["Won"],self.result[eachteam]["Games"],multiplier=100)
                winpavg = []
                for eachdict in self.result:
                    if eachdict!="All Teams":
                        winpavg.append(self.result[eachdict]["Win %"])
                self.result[eachteam]["Win %"] = round(np.mean(winpavg),2)
                # self.result[eachteam]["Win %"]=round(self.result.loc[self.result["Teams"]!=eachteam, "Win %"].mean(), 2)

            if self.result[eachteam]["Balls Faced"] > 0:
                self.result[eachteam]["Runs/Ball"] = statsprocessor.ratio(self.result[eachteam]["Runs"],self.result[eachteam]["Balls Faced"])
                self.result[eachteam]["Boundary %"] = statsprocessor.ratio((self.result[eachteam]["Fours"] + self.result[eachteam]["Sixes"]),
                    self.result[eachteam]["Balls Faced"], multiplier=100)
                self.result[eachteam]["Dot Ball %"] = statsprocessor.ratio(self.result[eachteam]["Dot Balls"],self.result[eachteam]["Balls Faced"], multiplier=100)

                self.result[eachteam]["Run Rate"] = statsprocessor.ratio(self.result[eachteam]["Runs"], self.result[eachteam]["Balls Faced"], multiplier=6)

            if self.result[eachteam]["firstboundary"]:
                self.result[eachteam]["Avg First Boundary Ball"] = round(np.mean(self.result[eachteam]["firstboundary"]))
                
            if self.result[eachteam]["Outs"] > 0:
                self.result[eachteam]["Runs/Ball"] = statsprocessor.ratio(self.result[eachteam]["Runs"],self.result[eachteam]["Outs"])

            if len(self.inningsresult["Run Rate"].dropna().index) > 0:
                self.result[eachteam]["Run Rate MeanAD"]=round(self.inningsresult["Run Rate"].mad(), 2)

            if len(self.inningsresult["Scores"].dropna().index) > 0:
                self.result[eachteam]["Score MeanAD"]=round(self.inningsresult["Scores"].mad(), 2) 
                self.result[eachteam]["Mean Score"]=round(self.inningsresult["Scores"].mean(), 2)

            if self.result[eachteam]["Balls Bowled"] > 0:
                self.result[eachteam]["Runsgiven/Ball"] = statsprocessor.ratio(
                    self.result[eachteam]["Runsgiven"], self.result[eachteam]["Balls Bowled"])
                self.result[eachteam]["Dot Ball Bowled %"] = statsprocessor.ratio(
                    self.result[eachteam]["Dot Balls Bowled"], self.result[eachteam]["Balls Bowled"],
                    multiplier=100)
                self.result[eachteam]["Boundary Given %"] = statsprocessor.ratio(
                    (self.result[eachteam]["Foursgiven"]
                    + self.result[eachteam]["Sixesgiven"]),
                    self.result[eachteam]["Balls Bowled"], multiplier=100)
                self.result[eachteam]["Runsgiven Rate"] = statsprocessor.ratio(self.result[eachteam]["Runsgiven"], self.result[eachteam]["Balls Bowled"], multiplier=6)

            if self.result[eachteam]["dotballseries"]:
                self.result[eachteam]["Avg Consecutive Dot Balls"] = round(np.mean(self.result[eachteam]["dotballseries"]))
            
            if len(self.inningsresult["Runsgiven Rate"].dropna().index) > 0:
                self.result[eachteam]["Runsgiven Rate MeanAD"] = round(self.inningsresult["Runsgiven Rate"].mad(), 2)

            if self.result[eachteam]["Wickets"] > 0:
                self.result[eachteam]['Runsgiven/Wicket'] = statsprocessor.ratio(
                    self.result[eachteam]["Runsgiven"], self.result[eachteam]["Wickets"], multiplier=0)\

            self.result[eachteam]["Net Run Rate"] = self.result[eachteam]["Run Rate"] - self.result[eachteam]["Runsgiven Rate"]
            self.result[eachteam]["Net Boundary %"] = self.result[eachteam]["Boundary %"] - self.result[eachteam]["Boundary Given %"]

    def cleanup(self):
        for eachdict in self.result:
            removestats = ["batinningscount", "inningsruns", "inningsballsfaced", "inningsouts", "firstboundary", "totalstos", "totalstosopp", "totalstosgiven", "totalstosgivenopp", "bowlinningscount", "inningsrunsgiven", "inningsballsbowled", "inningswickets","dotballseries"]
            for eachstat in removestats:
                if eachstat in self.result[eachdict]: 
                    self.result[eachdict].pop(eachstat)

    # This is the main function to be applied to search object.
    def stats(self, database, from_date, to_date, matchtype, betweenovers=None, innings=None, sex=None, playersteams=None, teammates=None, oppositionbatters=None, oppositionbowlers=None, oppositionteams=None, venue=None, event=None, matchresult=None, superover=None, battingposition=None, bowlingposition=None, fielders=None, sum=False):
        if betweenovers == None:
            betweenovers = []
        if innings == None:
            innings = []
        if sex == None:
            sex = []
        if playersteams ==None:
            playersteams = []
        if teammates ==None:
            teammates = []
        if fielders == None:
            fielders = []
        if oppositionbatters == None:
            oppositionbatters = []
        if oppositionbatters and type(oppositionbatters[0]) is list:
            oppositionbatters = [x for eachlist in oppositionbatters for x in eachlist]
        if oppositionbowlers == None:
            oppositionbowlers = []
        if oppositionbowlers and type(oppositionbowlers[0]) is list:
            oppositionbowlers = [x for eachlist in oppositionbowlers for x in eachlist]
        if oppositionteams == None:
            oppositionteams = []
        if venue == None:
            venue = []
        if event ==None:
            event =[]
        if matchresult == None:
            matchresult = None
        if superover == None:
            superover = False
        if battingposition == None:
            battingposition = []
        if bowlingposition == None:
            bowlingposition = []

        # Setup search results according to whether search involves teams or players.
        search.resultsetup(self)

        # Ingest zipfile of data
        matches = zipfile.ZipFile(database, 'r')

        # create an index file for eachfile
        search.fileindexing(self, database, matches)

        importlib.reload(index)
        # start = time.time()
        
        # Setup tally of games and results for "all teams" stats.
        allgamesplayed = 0
        allgameswinloss = 0
        allgamesdrawn = 0

        # Open each file by searched for matchtype in index
        for eachmatchtype in matchtype:
            for eachyear in index.matchindex["matches"][eachmatchtype]:
                if int(eachyear) < from_date[0] or int(eachyear) > to_date[0]:
                    continue
                for eachfile in index.matchindex["matches"][eachmatchtype][eachyear]:
                    # print(eachfile)
                    matchdata = matches.open(eachfile)
                    match = json.load(matchdata)

                    # Dates check
                    year = match["info"]["dates"][0][:4]
                    month = str(match["info"]["dates"][0][5:7])
                    day = str(match["info"]["dates"][0][8:])
                    matchtimetuple = (int(year), int(month),
                                    int(day))
                    if time.mktime(matchtimetuple + (0, 0, 0, 0, 0, 0)) < time.mktime(from_date + (0, 0, 0, 0, 0, 0)) or time.mktime(matchtimetuple + (0, 0, 0, 0, 0, 0)) > time.mktime(to_date + (0, 0, 0, 0, 0, 0)):
                        continue
                    # Event Check
                    if event and ("event" not in match["info"] or match["info"]["event"]["name"] not in event):
                        continue
                    # Mens/Womens Check
                    if sex and match["info"]["gender"] not in sex:
                        continue
                    # Players' Teams check
                    if playersteams and (
                            match["info"]["teams"][0] not in playersteams and match["info"]["teams"][1] not in playersteams):
                        continue
                    # Opposition check
                    if oppositionteams and (
                            match["info"]["teams"][0] not in oppositionteams and match["info"]["teams"][1] not in oppositionteams):
                        continue
                    # Venue Check
                    if venue and match["info"]["venue"] not in venue:
                        continue

                    # Team mate check
                    if teammates and not any(eachteammate in teammates for eachteammate in match["info"]["players"][playersteams]):
                        continue

                    # Teams Check
                    if self.teams and (match["info"]["teams"][0] not in self.teams and match["info"]["teams"][1] not in self.teams):
                        continue
                    
                    # Players Check
                    if self.players and not any(eachplayer in self.players for eachplayer in match['info']['registry']['people'].keys()):
                        continue

                    # Match Result check
                    if matchresult and self.teams and (
                        (("result" in match['info']['outcome'] and "no result" in match['info']['outcome']['result']) or (matchresult=="tie" and ("winner" in match['info']['outcome'] or "result" in match['info']['outcome'] and match['info']['outcome']['result']!=matchresult)) or
                        (matchresult=="draw" and ("winner" in match['info']['outcome'] or "result" in match['info']['outcome'] and match['info']['outcome']['result']!=matchresult)) or
                        (matchresult=="won" and ("result" in match['info']['outcome'] or "winner" in match['info']['outcome'] and match['info']['outcome']['winner'] not in self.teams)) or
                        (matchresult=="loss" and ("result" in match['info']['outcome'] or "winner" in match['info']['outcome'] and match['info']['outcome']['winner'] in self.teams))

                        )):
                        continue

                    if matchresult and self.players and playersteams and (
                        (("result" in match['info']['outcome'] and "no result" in match['info']['outcome']['result']) or (matchresult=="tie" and ("winner" in match['info']['outcome'] or "result" in match['info']['outcome'] and match['info']['outcome']['result']!=matchresult)) or
                        (matchresult=="draw" and ("winner" in match['info']['outcome'] or "result" in match['info']['outcome'] and match['info']['outcome']['result']!=matchresult)) or
                        (matchresult=="won" and ("result" in match['info']['outcome'] or "winner" in match['info']['outcome'] and match['info']['outcome']['winner'] not in playersteams)) or
                        (matchresult=="loss" and ("result" in match['info']['outcome'] or "winner" in match['info']['outcome'] and match['info']['outcome']['winner'] in playersteams))
                        )):
                        continue
                        
                        
                        #  or ("won"==matchresult and "winner" in match['info']['outcome'] and match['info']['outcome']['winner'] not in self.teams))
                        # ):
                        # continue
                        
                        # or 
                        # (self.players and ("result" in match['info']['outcome'] and match['info']['outcome']["result"] not in matchresult) and  
                        # (playersteams and "winner" in matchresult and "winner" in match['info']['outcome'] and match['info']['outcome']["winner"] not in playersteams))


                    # All Players and All Teams games/wins/draw/ties record
                    # rewrite for ties and add these to stats dict. Hard because T20s have superovers to decide ties.
                    if sum==True:
                        allgamesplayed += 1
                        if "result" in match["info"]["outcome"] and match["info"]["outcome"]['result'] == "draw":
                            allgamesdrawn += 1
                        if "winner" in match["info"]["outcome"]:
                            allgameswinloss += 1

                    # Individual team and players games/wins/draw/ties record
                    search.gamesandwins(self, match["info"]["players"], match["info"]["outcome"], match["info"]["teams"])

                    # Open each innings in match
                    for nthinnings, eachinnings in enumerate(match['innings']):
                        if innings and (nthinnings + 1) not in innings:
                            continue
                        if "overs" not in eachinnings:
                            continue
                        if not superover and "super_over" in eachinnings:
                            continue
                        if superover and "super_over" not in eachinnings:
                            continue
                        
                        # Setup running tally of innings scores
                        search.setupinningscores(self)

                        # Create list of batters in for this innings.
                        battingorder = []
                        bowlingorder = []

                        # Creat liste of mandatory and optional powerplays in this innings.
                        powerplays = []
                        if "powerplays" in eachinnings:
                            for eachpowerplay in eachinnings["powerplays"]:
                                thispowerplay = range(math.floor(eachpowerplay["from"]), (math.floor(eachpowerplay["to"]) + 1))
                                powerplays.extend(thispowerplay)

                        # Open each over in innings
                        for eachover in eachinnings['overs']:

                            # Powerplay (mandatory and optional) check.
                            if betweenovers and "powerplays" in betweenovers and "powerplays" in eachinnings and eachover['over'] not in powerplays:
                                continue

                            # Overs interval check  
                            if betweenovers and "powerplays" not in betweenovers and (eachover['over'] < (betweenovers[0] - 1) or eachover['over'] > (betweenovers[1] - 1)):
                                continue

                            # Open each ball
                            for nthball, eachball in enumerate(eachover['deliveries']):

                                # Player stats
                                if self.players:
                                    
                                    # Record batting lineup.
                                    if eachball['batter'] not in battingorder:
                                        battingorder.append(eachball['batter'])
                                    if eachball['non_striker'] not in battingorder:
                                        battingorder.append(eachball['non_striker'])

                                    # Record bowling order.
                                    if eachball['batter'] not in bowlingorder:
                                        bowlingorder.append(eachball['batter'])

                                    
                                    # Striker's stats
                                    if eachball['batter'] in self.players and (not oppositionbowlers or eachball['bowler'] in oppositionbowlers) and (not battingposition or (battingposition and ((battingorder.index(eachball['batter']) + 1) in battingposition))):
                                        search.strikerstats(self, eachball)
    
                                    # Non-striker's outs.
                                    if eachball["non_striker"] in self.players and "wickets" in eachball and (not battingposition or (battingposition and ((battingorder.index(eachball['non_striker']) + 1) in battingposition))):
                                        search.nonstrikerstats(self, eachball, oppositionbowlers)

                                    # Bowling stats
                                    if eachball['bowler'] in self.players and (not oppositionbatters or eachball['batter'] in oppositionbatters) and (not bowlingposition or (bowlingposition and ((bowlingorder.index(eachball['bowler']) + 1) in bowlingposition))):
                                        search.bowlerstats(self, eachball, fielders)

                                    # Fielding stats
                                    if "wickets" in eachball:
                                        search.fieldingstats(self, eachball)

                                    # Strike Turnover stats
                                    if nthball < (len(eachover['deliveries']) - 1):
                                        search.striketurnoverstats(self, eachball, 1, 3)
                                    if nthball == (len(eachover['deliveries']) - 1):
                                        search.striketurnoverstats(self, eachball, 0, 2)

                                # Team stats
                                if self.teams:

                                    # Team Batting stats
                                    if eachinnings["team"] in self.teams:
                                        search.teambattingstats(self, eachball, eachinnings["team"])

                                    # Team Bowling stats
                                    for eachteam in match["info"]["teams"]:
                                        if eachteam in self.teams and eachteam not in eachinnings["team"]:
                                            search.teambowlingstats(self, eachball, eachteam)

                        # Player innings scores.
                        if self.players:
                            search.playerinnings(self,matchtimetuple, match["info"]["players"], nthinnings, eachmatchtype,match["info"]["venue"])
                        
                        # Team innings scores
                        if self.teams:

                            # Batting innings score
                            if eachinnings["team"] in self.teams:
                                search.teambattinginnings(self, eachinnings["team"], nthinnings, match["info"]["teams"], matchtimetuple, match['info']['outcome'], match['innings'], eachmatchtype, match["info"]["venue"])
                                
                            # Bowling innings figures
                            for eachteam in match["info"]["teams"]:
                                if eachteam in self.teams and eachteam not in eachinnings["team"]:
                                    search.teambowlinginnings(self, eachteam, eachinnings["team"], matchtimetuple, nthinnings, match['info']['outcome'], match['innings'], eachmatchtype, match["info"]["venue"])
                                    
                            # Successfully defended and chased scores.
                            # if 'result' not in match['info']['outcome'] and match['info']['outcome']["winner"] in self.teams:
                                # search.successfulscores(self, match['info']['outcome'], match['innings'], nthinnings, eachinnings["team"])

                    matchdata.close()
        matches.close()
        # print(f'Time after stats(): {time.time() - start}')
        

        # for y in self.inningsresult.keys():
        #     print(y, len(self.inningsresult[y]))
        # print(self.inningsresult)

        self.inningsresult = pd.DataFrame(self.inningsresult)

        # print(f'Time after self.inningsresult creation: {time.time() - start}')
        # Derived Stats
        search.derivedstats(self)

        # print(f'Time after derivedstats(): {time.time() - start}')
        # All Player and All Teams Summing function
        if sum:
            search.sumstats(self,allgamesplayed, allgameswinloss, allgamesdrawn)

        search.cleanup(self)

        # print(f'Time after sumstats(): {time.time() - start}')
        df = pd.DataFrame(self.result)
        self.result = df.transpose()
        # print(f'Time after transpose(): {time.time() - start}')