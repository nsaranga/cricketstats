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


# Do this first Stats by batting position is just a check. to add. Basically go through the innings and get batting order, then check against the number I give in input.

# CLI program plan:
# a: Need create indexes of teams, venues, events, so people cna know what it is possible to search for.
# 1 Wrapper CLI interface -> user inputs players or teams they -> create search object
# 2 Search Object uses getstats method -> stats collected
# 3 User is shown what stats they can see, and asks which? -> Pandas display of stats.
# 4 ask if you want plot of dataframe and how?

class search:
    def __init__(self, players=None, teams=None, result=None) -> None:
        self.players = players
        self.teams = teams
        self.result = result

    def resultsetup(self):
        if self.players:
            self.result = {}
            for eachplayer in self.players:
                self.result[eachplayer] = {"Games": 0, "Won": 0, "Drawn": 0, 'Win %': 0, "Innings Batted":0, "batinningscount": False,
                                            "All Scores": [],"All Balls Faced": [],
                                            "inningsruns": [], "inningsballsfaced": 0, "1stboundary": [], 'Avg First Boundary Ball': 0, 
                                            "Runs": 0, "Fours": 0, "Sixes": 0, "Dot Balls": 0, "Balls Faced": 0, "Outs": 0, "Bowled Outs": 0, "LBW Outs": 0, "Caught Outs": 0, "Stumped Outs": 0, "Run Outs": 0, "totalstos": 0, "totalstosopp": 0, 'Dot Ball %': 0, 'Strike Turnover %': 0, 'Batting S/R': 0, 'Batting S/R MeanAD': 0,  'Batting Avg': 0, 'Score MeanAD': 0, 'Boundary %': 0,
                                            "Innings Bowled":0, "bowlinningscount": False, "All Runsgiven": [], "All Wickets": [], "All Overs Bowled": [], "inningsrunsgiven": [], "inningsballsbowled": 0, "inningswickets": 0,
                                            "Runsgiven": 0, "totalfoursgiven": 0,
                                            "totalsixesgiven": 0, "Wickets": 0, "Balls Bowled": 0, "totalextras": 0, "No Balls": 0, "Wides":0,
                                            "totaldotballsbowled": 0, "totalbowleds": 0, "totallbws": 0,
                                            "totalhitwickets": 0, "totalcaughts": 0, "totalstumpeds": 0,
                                            "totalstosgiven": 0, "totalstosgivenopp": 0, "totalcatches": 0,
                                            "totalrunouts": 0, "totalstumpings": 0,  'Economy Rate': 0, 'Economy Rate MeanAD': 0, 'Dot Ball Bowled %': 0,'Boundary Given %': 0, 'Bowling Avg': 0, 'Bowling S/R': 0, "dotballseries": [], "Avg Consecutive Dot Balls": 0}
        if self.teams:
            self.result = {}
            for eachteam in self.teams:
                self.result[eachteam] = {"Games": 0, "Innings":0, "Won": 0, "Drawn": 0, 'Win %': 0, "All Scores": [], "All Outs": [], 
                                        "All Overs Faced": [], 
                                        "1st Innings Scores": [], "2nd Innings Scores": [], "3rd Innings Scores": [], "4th Innings Scores": [], "inningsruns": [], "inningsballsfaced": 0, "inningsouts": 0, "1stboundary": [], 'Avg First Boundary Ball': 0, "Defended Scores": [], "Chased Scores": [], "runmargins": [], "wicketmargins": [], "overschased": [],
                                        "Runs": 0, "Fours": 0, "Sixes": 0, "Dot Balls": 0, "Outs": 0, "Balls Faced": 0, 'Dot Ball %': 0, 'Strike Turnover %': 0, 'Batting S/R': 0, 'Batting S/R MeanAD': 0,  'Batting Avg': 0, 'Score MeanAD': 0, 'Boundary %': 0, "Run Rate":0,
                                        "All Runsgiven": [], "All Wickets": [], "All Overs Bowled": [],
                                        "1st Innings Wickets": [], "2nd Innings Wickets": [], "3rd Innings Wickets": [],
                                        "4th Innings Wickets": [], "inningsrunsgiven": [], "inningsballsbowled": 0,
                                        "inningswickets": 0, "Runsgiven": 0, "totalfoursgiven": 0,
                                        "totalsixesgiven": 0, "Wickets": 0, "Balls Bowled": 0, "totalextras": 0, "No Balls": 0, "Wides":0, "Byes": 0, "Leg Byes": 0,
                                        "totaldotsbowled": 0, "totalcaughts": 0, "totalrunouts": 0, "totalstumpeds": 0,  'Economy Rate': 0, 'Economy Rate MeanAD': 0, 'Dot Ball Bowled %': 0,'Boundary Given %': 0, 'Bowling Avg': 0, 'Bowling S/R': 0, "dotballseries": [], "Avg Consecutive Dot Balls": 0,
                                        "Runsgiven Rate":0, "Net Boundary %":0, "Net Run Rate":0}
    
    def fileindexing(self, database, matches):
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
                if eachfile not in matchindex[match["info"]["match_type"]]:
                    matchindex[match["info"]["match_type"]].append(eachfile)
                matchdata.close
            currentdir = os.path.dirname(os.path.abspath(__file__))
            file = open(f"{currentdir}/index.py", "w")
            file.write("matchindex = " + repr(matchindex))
            file.close
        if os.path.getmtime(database) < index.matchindex['indexedtime']:
            raise Exception("Your cricsheet database is older than the index, please download the newest zip file from https://cricsheet.org/downloads/all_json.zip")
            
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
                self.result[eachteam]["inningsouts"] = 0
                self.result[eachteam]["inningsruns"] = []
                self.result[eachteam]["inningsballsfaced"] = 0
                self.result[eachteam]["inningswickets"] = 0
                self.result[eachteam]["inningsrunsgiven"] = []
                self.result[eachteam]["inningsballsbowled"] = 0

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

    def nonstrikerstats(self, eachball, oppositionbowlers):
        self.result[eachball["non_striker"]]["batinningscount"] = True
        for eachwicket in eachball["wickets"]:
            if eachball['non_striker'] == eachwicket["player_out"] and not oppositionbowlers:
                self.result[eachball['non_striker']
                            ]["Outs"] += 1
                if eachwicket["kind"] == "run out":
                    self.result[eachball['non_striker']
                                ]["Run Outs"] += 1

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

    def bowlerstats(self, eachball, fielders):
        if eachball['bowler'] in self.players:
            self.result[eachball['bowler']]["bowlinningscount"] = True
        self.result[eachball['bowler']
                    ]["Runsgiven"] += eachball['runs']['batter']
        if eachball['runs']['batter'] == 4:
            self.result[eachball['bowler']
                        ]["totalfoursgiven"] += 1
        if eachball['runs']['batter'] == 6:
            self.result[eachball['bowler']
                        ]["totalsixesgiven"] += 1
        if eachball['runs']['total'] == 0:
            self.result[eachball['bowler']
                        ]["totaldotballsbowled"] += 1
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
                            ]["totalextras"] += eachball['extras']['wides']
                self.result[eachball['bowler']]["inningsrunsgiven"].append((
            eachball['runs']['batter'] + eachball['extras']['wides']))
            if "noballs" in eachball['extras']:
                self.result[eachball['bowler']
                            ]["Runsgiven"] += eachball['extras']['noballs']
                self.result[eachball['bowler']
                            ]["No Balls"] += eachball['extras']['noballs']
                self.result[eachball['bowler']
                            ]["totalextras"] += eachball['extras']['noballs']
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
                                ]["totalbowleds"] += 1
                if eachwicket["kind"] == "lbw":
                    self.result[eachball['bowler']
                                ]["totallbws"] += 1
                if eachwicket["kind"] == "hit wicket":
                    self.result[eachball['bowler']
                                ]["totalhitwickets"] += 1
                if eachwicket["kind"] == "caught" and (not fielders or (fielders and (eachwicket["fielders"]["name"] in fielders))):
                    self.result[eachball['bowler']
                                ]["totalcaughts"] += 1
                if eachwicket["kind"] == "stumped":
                    self.result[eachball['bowler']
                                ]["totalstumpeds"] += 1

    def fieldingstats(self, eachball):
        for eachwicket in eachball["wickets"]:
            if "fielders" in eachwicket:
                for eachfielder in eachwicket["fielders"]:
                    if "name" not in eachfielder:
                        continue
                    if eachfielder["name"] in self.players:
                        if eachwicket["kind"] == "caught":
                            self.result[eachfielder["name"]
                                        ]["totalcatches"] += 1
                        if eachwicket["kind"] == "stumped":
                            self.result[eachfielder["name"]
                                        ]["totalstumpings"] += 1
                        if eachwicket["kind"] == "run out":
                            self.result[eachfielder["name"]
                                        ]["totalrunouts"] += 1

    def teambattingstats(self, eachball, inningsteam):
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

    def teambowlingstats(self, eachball, inningsteam):
        self.result[inningsteam]["inningsrunsgiven"].append(
            eachball['runs']['total'])
        self.result[inningsteam]["Runsgiven"] += eachball['runs']['total']
        if eachball['runs']['batter'] == 4:
            self.result[inningsteam]["totalfoursgiven"] += 1
        if eachball['runs']['batter'] == 6:
            self.result[inningsteam]["totalsixesgiven"] += 1
        if eachball['runs']['total'] == 0:
            self.result[inningsteam]["totaldotsbowled"] += 1
        if "extras" not in eachball:
            self.result[inningsteam]["Balls Bowled"] += 1
            self.result[inningsteam]["inningsballsbowled"] += 1
        if "extras" in eachball:
            if "wides" in eachball['extras']:
                self.result[inningsteam]["Wides"] += eachball['extras']['wides']
                self.result[inningsteam]["totalextras"] += eachball['extras']['wides']
            if "noballs" in eachball['extras']:
                self.result[inningsteam]["No Balls"] += eachball['extras']['noballs']
                self.result[inningsteam]["totalextras"] += eachball['extras']['noballs']
            if "byes" in eachball['extras']:
                self.result[inningsteam]["Balls Bowled"] += 1
                self.result[inningsteam]["inningsballsbowled"] += 1
                self.result[inningsteam]["Byes"] += eachball['extras']['byes']
                self.result[inningsteam]["totalextras"] += eachball['extras']['byes']
            if "legbyes" in eachball['extras']:
                self.result[inningsteam]["Balls Bowled"] += 1
                self.result[inningsteam]["inningsballsbowled"] += 1
                self.result[inningsteam]["Leg Byes"] += eachball['extras']['legbyes']
                self.result[inningsteam]["totalextras"] += eachball['extras']['legbyes']
        if "wickets" in eachball:
            for eachwicket in eachball["wickets"]:
                self.result[inningsteam]["inningswickets"] += 1
                self.result[inningsteam]["Wickets"] += 1
                if eachwicket["kind"] == "caught":
                    self.result[inningsteam]["totalcaughts"] += 1
                if eachwicket["kind"] == "stumped":
                    self.result[inningsteam]["totalstumpeds"] += 1
                if eachwicket["kind"] == "run out":
                    self.result[inningsteam]["totalrunouts"] += 1

    def playerinnings(self):
        for eachplayer in self.result:
            if self.result[eachplayer]["batinningscount"] == True:
                self.result[eachplayer]["Innings Batted"] += 1
            if self.result[eachplayer]["inningsballsfaced"] > 0:
                self.result[eachplayer]["All Scores"].append(
                    sum(self.result[eachplayer]["inningsruns"]))
                self.result[eachplayer]["All Balls Faced"].append(
                    self.result[eachplayer]["inningsballsfaced"])
            if 4 in self.result[eachplayer]["inningsruns"] or 6 in self.result[eachplayer]["inningsruns"]:
                self.result[eachplayer]["1stboundary"].append(statsprocessor.firstboundary(
                    self.result[eachplayer]["inningsruns"]))

            if self.result[eachplayer]["bowlinningscount"] == True:
                self.result[eachplayer]["Innings Bowled"] += 1
            if self.result[eachplayer]["inningsballsbowled"] > 0:
                self.result[eachplayer]["All Runsgiven"].append(
                    sum(self.result[eachplayer]["inningsrunsgiven"]))
                self.result[eachplayer]["All Wickets"].append(
                    self.result[eachplayer]["inningswickets"])
                self.result[eachplayer]["All Overs Bowled"].append(
                    math.ceil(self.result[eachplayer]["inningsballsbowled"] / 6))
                self.result[eachplayer]["dotballseries"].extend(statsprocessor.dotballseries(self.result[eachplayer]["inningsrunsgiven"]))
    
    def teambattinginnings(self, inningsteam, nthinnings):
        self.result[inningsteam]["All Scores"].append(
                                sum(self.result[inningsteam]["inningsruns"]))
        self.result[inningsteam]["All Outs"].append(
            self.result[inningsteam]["inningsouts"])
        self.result[inningsteam]["All Overs Faced"].append(
            round(self.result[inningsteam]["inningsballsfaced"] / 6))
        if nthinnings == 0:
            self.result[inningsteam]["1st Innings Scores"].append(
                sum(self.result[inningsteam]["inningsruns"]))
        if nthinnings == 1:
            self.result[inningsteam]["2nd Innings Scores"].append(
                sum(self.result[inningsteam]["inningsruns"]))
        if nthinnings == 2:
            self.result[inningsteam]["3rd Innings Scores"].append(
                sum(self.result[inningsteam]["inningsruns"]))
        if nthinnings == 3:
            self.result[inningsteam]["4th Innings Scores"].append(
                sum(self.result[inningsteam]["inningsruns"]))

    def teambowlinginnings(self, eachteam, nthinnings):
        self.result[eachteam]["All Runsgiven"].append(
                                    sum(self.result[eachteam]["inningsrunsgiven"]))
        self.result[eachteam]["All Wickets"].append(
            self.result[eachteam]["inningswickets"])
        self.result[eachteam]["All Overs Bowled"].append(
            round(self.result[eachteam]["inningsballsbowled"] / 6))
        if nthinnings == 0:
            self.result[eachteam]["1st Innings Wickets"].append(
                self.result[eachteam]["inningswickets"])
        if nthinnings == 1:
            self.result[eachteam]["2nd Innings Wickets"].append(
                self.result[eachteam]["inningswickets"])
        if nthinnings == 2:
            self.result[eachteam]["3rd Innings Wickets"].append(
                self.result[eachteam]["inningswickets"])
        if nthinnings == 3:
            self.result[eachteam]["4th Innings Wickets"].append(
                self.result[eachteam]["inningswickets"])

    def succesfulscores(self, matchoutcome, matchinnings, nthinnings, inningsteam):
        if 'runs' in matchoutcome['by']:
            if "target" in matchinnings[1]:
                self.result[matchoutcome["winner"]]["Defended Scores"].append(
                    matchinnings[1]['target']['runs'] - 1)
            if "target" not in matchinnings[1] and nthinnings == (len(matchinnings) - 1) and matchoutcome["winner"] != inningsteam:
                self.result[matchoutcome["winner"]]["Defended Scores"].append(
                    (sum(
                        self.result[matchoutcome["winner"]]["inningsrunsgiven"]))
                    + matchoutcome['by']['runs'])
            self.result[matchoutcome["winner"]]["runmargins"].append(
                matchoutcome['by']['runs'])
        if 'wickets' in matchoutcome['by']:
            if "target" in matchinnings[1]:
                self.result[matchoutcome["winner"]]["Chased Scores"].append(
                    matchinnings[1]['target']['runs'])
                self.result[matchoutcome["winner"]]["overschased"].append(
                    round(self.result[matchoutcome["winner"]]["inningsballsfaced"] / 6))
            if "target" not in matchinnings[1] and nthinnings == (len(matchinnings) - 1) and matchoutcome["winner"] == inningsteam:
                self.result[matchoutcome["winner"]]["Chased Scores"].append(
                    (sum(self.result[matchoutcome["winner"]]["inningsruns"])))
                self.result[matchoutcome["winner"]]["overschased"].append(
                    round(self.result[matchoutcome["winner"]]["inningsballsfaced"] / 6))
            self.result[matchoutcome["winner"]]["wicketmargins"].append(
                matchoutcome['by']['wickets'])

    def derivedstats(self):
        if self.players:
            for eachplayer in self.result:
                if self.result[eachplayer]["Games"] > 0:
                    self.result[eachplayer]["Win %"] = statsprocessor.ratio(self.result[eachplayer]["Won"],
                                                                            self.result[eachplayer]["Games"],
                                                                            multiplier=100)

                if self.result[eachplayer]["Balls Faced"] > 0:
                    self.result[eachplayer]["Batting S/R"] = statsprocessor.ratio(self.result[eachplayer]["Runs"],
                                                                                    self.result[eachplayer][
                                                                                        "Balls Faced"], multiplier=100)
                    self.result[eachplayer]["Boundary %"] = statsprocessor.ratio(
                        (self.result[eachplayer]["Fours"]
                        + self.result[eachplayer]["Sixes"]),
                        self.result[eachplayer]["Balls Faced"], multiplier=100)
                    self.result[eachplayer]["Dot Ball %"] = statsprocessor.ratio(self.result[eachplayer]["Dot Balls"],
                                                                                    self.result[eachplayer][
                                                                                        "Balls Faced"], multiplier=100)
                if self.result[eachplayer]["1stboundary"]:
                    self.result[eachplayer]["Avg First Boundary Ball"] = round(statsprocessor.ratio(sum(self.result[eachplayer]["1stboundary"]), len(self.result[eachplayer]["1stboundary"])))

                if self.result[eachplayer]["totalstosopp"] > 0:
                    self.result[eachplayer]["Strike Turnover %"] = statsprocessor.ratio(self.result[eachplayer]["totalstos"], self.result[eachplayer]["totalstosopp"], multiplier=100)

                if self.result[eachplayer]["All Balls Faced"]:
                    self.result[eachplayer]["Batting S/R MeanAD"] = statsprocessor.madfromratio(
                        self.result[eachplayer]["All Scores"], self.result[eachplayer]["All Balls Faced"], multiplier=100)

                if self.result[eachplayer]["All Scores"]:
                    self.result[eachplayer]["Mean Score"] = statsprocessor.ratio(sum(self.result[eachplayer]["All Scores"]), len(self.result[eachplayer]["All Scores"]))
                    self.result[eachplayer]["Score MeanAD"] = statsprocessor.mad(
                        self.result[eachplayer]["All Scores"])

                if self.result[eachplayer]["Outs"] > 0:
                    self.result[eachplayer]["Batting Avg"] = statsprocessor.ratio(self.result[eachplayer]["Runs"],
                                                                                self.result[eachplayer]["Outs"],
                                                                                multiplier=0)

                if self.result[eachplayer]["Balls Bowled"] > 0:
                    self.result[eachplayer]["Economy Rate"] = statsprocessor.ratio(
                        self.result[eachplayer]["Runsgiven"], self.result[eachplayer]["Balls Bowled"],
                        multiplier=6)
                    self.result[eachplayer]["Dot Ball Bowled %"] = statsprocessor.ratio(
                        self.result[eachplayer]["totaldotballsbowled"], self.result[eachplayer]["Balls Bowled"],
                        multiplier=100)
                    self.result[eachplayer]["Boundary Given %"] = statsprocessor.ratio(
                        (self.result[eachplayer]["totalfoursgiven"]
                        + self.result[eachplayer]["totalsixesgiven"]),
                        self.result[eachplayer]["Balls Bowled"], multiplier=100)
                    self.result[eachplayer]["Avg Consecutive Dot Balls"] = round(
                        statsprocessor.ratio(
                            sum(self.result[eachplayer]["dotballseries"]), len(self.result[eachplayer]["dotballseries"])))

                if self.result[eachplayer]["All Overs Bowled"]:
                    self.result[eachplayer]["Economy Rate MeanAD"] = statsprocessor.madfromratio(
                        self.result[eachplayer]["All Runsgiven"], self.result[eachplayer]["All Overs Bowled"])

                if self.result[eachplayer]["Wickets"] > 0:
                    self.result[eachplayer]["Bowling Avg"] = statsprocessor.ratio(
                        self.result[eachplayer]["Runsgiven"], self.result[eachplayer]["Wickets"], multiplier=0)
                    self.result[eachplayer]["Bowling S/R"] = statsprocessor.ratio(
                        self.result[eachplayer]["Balls Bowled"], self.result[eachplayer]["Wickets"], multiplier=0)
            
        if self.teams:
            for eachteam in self.result:
                if self.result[eachteam]["Games"] > 0:
                    self.result[eachteam]["Win %"] = statsprocessor.ratio(self.result[eachteam]["Won"],
                                                                            self.result[eachteam]["Games"],
                                                                            multiplier=100)
                if self.result[eachteam]["Balls Faced"] > 0:
                    self.result[eachteam]["Batting S/R"] = statsprocessor.ratio(self.result[eachteam]["Runs"],
                                                                                    self.result[eachteam]["Balls Faced"], multiplier=100)
                    self.result[eachteam]["Boundary %"] = statsprocessor.ratio((self.result[eachteam]["Fours"] + self.result[eachteam]["Sixes"]),
                        self.result[eachteam]["Balls Faced"], multiplier=100)
                    self.result[eachteam]["Dot Ball %"] = statsprocessor.ratio(self.result[eachteam]["Dot Balls"],
                                                                                    self.result[eachteam][
                                                                                        "Balls Faced"], multiplier=100)

                    self.result[eachteam]["Run Rate"] = statsprocessor.ratio(self.result[eachteam]["Runs"], self.result[eachteam]["Balls Faced"], multiplier=6)

                if self.result[eachteam]["All Overs Faced"]:
                    self.result[eachteam]["Run Rate MeanAD"] = statsprocessor.madfromratio(
                        self.result[eachteam]["All Scores"], self.result[eachteam]["All Overs Faced"])

                if self.result[eachteam]["All Scores"]:
                    self.result[eachteam]["Score MeanAD"] = statsprocessor.mad(self.result[eachteam]["All Scores"])
                    self.result[eachteam]["Mean Score"] = statsprocessor.ratio(sum(self.result[eachteam]["All Scores"]), len(self.result[eachteam]["All Scores"]))

                if self.result[eachteam]["Balls Bowled"] > 0:
                    self.result[eachteam]["Economy Rate"] = statsprocessor.ratio(
                        self.result[eachteam]["Runsgiven"], self.result[eachteam]["Balls Bowled"],
                        multiplier=6)
                    self.result[eachteam]["Dot Ball Bowled %"] = statsprocessor.ratio(
                        self.result[eachteam]["totaldotsbowled"], self.result[eachteam]["Balls Bowled"],
                        multiplier=100)
                    self.result[eachteam]["Boundary Given %"] = statsprocessor.ratio(
                        (self.result[eachteam]["totalfoursgiven"]
                        + self.result[eachteam]["totalsixesgiven"]),
                        self.result[eachteam]["Balls Bowled"], multiplier=100)
                    self.result[eachteam]["Runsgiven Rate"] = statsprocessor.ratio(self.result[eachteam]["Runsgiven"], self.result[eachteam]["Balls Bowled"], multiplier=6)
                
                if self.result[eachteam]["All Overs Bowled"]:
                    self.result[eachteam]["Economy Rate MeanAD"] = statsprocessor.madfromratio(
                        self.result[eachteam]["All Runsgiven"], self.result[eachteam]["All Overs Bowled"])

                if self.result[eachteam]["Wickets"] > 0:
                    self.result[eachteam]["Bowling Avg"] = statsprocessor.ratio(
                        self.result[eachteam]["Runsgiven"], self.result[eachteam]["Wickets"], multiplier=0)
                    self.result[eachteam]["Bowling S/R"] = statsprocessor.ratio(
                        self.result[eachteam]["Balls Bowled"], self.result[eachteam]["Wickets"], multiplier=0)

                self.result[eachteam]["Net Run Rate"] = self.result[eachteam]["Run Rate"] - self.result[eachteam]["Runsgiven Rate"]
                self.result[eachteam]["Net Boundary %"] = self.result[eachteam]["Boundary %"] - self.result[eachteam]["Boundary Given %"]

    def stats(self, database, from_date, to_date, matchtype, betweenovers=None, innings=None, sex=None, playerteams=None, oppositionbatters=None, oppositionbowlers=None, oppositionteams=None, venue=None, event=None, matchresult=None, superover=None, battingposition=None, bowlingposition=None, fielders=None):
        if betweenovers == None:
            betweenovers = []
        if innings == None:
            innings = []
        if sex == None:
            sex = []
        if playerteams ==None:
            playerteams = []
        if fielders == None:
            fielders = []
        if oppositionbatters == None:
            oppositionbatters = []
        if oppositionbowlers == None:
            oppositionbowlers = []
        if oppositionteams == None:
            oppositionteams = []
        if venue == None:
            venue = []
        if event ==None:
            event =[]
        if matchresult == None:
            matchresult = []
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
        # if os.path.getmtime(database) > index.matchindex['indexedtime']:
        search.fileindexing(self, database, matches)

        importlib.reload(index)
        # for most of these checks if i pass the required string I can setup functions with basic structure.
        # what if I don't give any matchtype? I have to make this a required arg.
        for eachmatchtype in matchtype:
            for eachfile in index.matchindex[eachmatchtype]:
                # print(eachfile)
                matchdata = matches.open(eachfile)
                match = json.load(matchdata)

                # General Checks: Dates, event, mens/womens, matchtype, venue, oppositionteams
                # For player stats, players, playerteams
                # For team stats, teams

                # General Checks
                # Dates check
                year = match["info"]["dates"][0][:4]
                month = str(match["info"]["dates"][0][5:7])
                day = str(match["info"]["dates"][0][8:])
                matchtimetuple = (int(year), int(month),
                                int(day), 0, 0, 0, 0, 0, 0)
                if time.mktime(matchtimetuple) < time.mktime(from_date + (0, 0, 0, 0, 0, 0)) or time.mktime(matchtimetuple) > time.mktime(to_date + (0, 0, 0, 0, 0, 0)):
                    continue
                # Event Check
                if event and ("event" not in match["info"] or match["info"]["event"]["name"] not in event):
                    continue
                # Mens/Womens Check
                if sex and match["info"]["gender"] not in sex:
                    continue
                # Players' Teams check
                if playerteams and (
                        match["info"]["teams"][0] not in playerteams and match["info"]["teams"][1] not in playerteams):
                    continue
                # Opposition check
                if oppositionteams and (
                        match["info"]["teams"][0] not in oppositionteams and match["info"]["teams"][1] not in oppositionteams):
                    continue
                # Venue Check
                if venue and match["info"]["venue"] not in venue:
                    continue
                # Match Result check
                if matchresult and ((match['info']['outcome'] not in matchresult) or (self.teams and match['info']['outcome']["winner"] not in self.teams) or (playerteams and match['info']['outcome']["winner"] not in playerteams)):
                    continue

                # Players and Teams Check
                if (self.teams and (match["info"]["teams"][0] not in self.teams and match["info"]["teams"][1] not in self.teams)) and (
                        self.players and not any(
                        eachplayer in self.players for eachplayer in match['info']['registry']['people'].keys())):
                    continue

                # Games and Wins record
                # rewrite for ties and superovers, and add these to stats dict.
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
                        for nth, eachball in enumerate(eachover['deliveries']):

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

                                # Strike Turnover stats
                                if nth < (len(eachover['deliveries']) - 1):
                                    search.striketurnoverstats(self, eachball, 1, 3)
                                if nth == (len(eachover['deliveries']) - 1):
                                    search.striketurnoverstats(self, eachball, 0, 2)

                                # Bowling stats
                                if eachball['bowler'] in self.players and (not oppositionbatters or eachball['batter'] in oppositionbatters) and (not bowlingposition or (bowlingposition and ((bowlingorder.index(eachball['bowler']) + 1) in bowlingposition))):
                                    search.bowlerstats(self, eachball, fielders)

                                # Fielding  stats
                                if "wickets" in eachball:
                                    search.fieldingstats(self, eachball)

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
                        search.playerinnings(self)
                    
                    # Team innings scores
                    if self.teams:

                        # Batting innings score
                        if eachinnings["team"] in self.teams:
                            search.teambattinginnings(self, eachinnings["team"], nthinnings)
                            
                        # Bowling innings figures
                        for eachteam in match["info"]["teams"]:
                            if eachteam in self.teams and eachteam not in eachinnings["team"]:
                                search.teambowlinginnings(self, eachteam, nthinnings)
                                

                        # Successfully defended and chased scores.
                        if 'result' not in match['info']['outcome'] and match['info']['outcome']["winner"] in self.teams:
                            search.succesfulscores(self, match['info']['outcome'], match['innings'], nthinnings, eachinnings["team"])

                matchdata.close()
        matches.close()

        # Derived Stats
        search.derivedstats(self)

        if self.players:
            df = pd.DataFrame(self.result)
            self.result = df.transpose()

        elif self.teams:
            df = pd.DataFrame(self.result)
            self.result = df.transpose()
