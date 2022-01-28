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

import datetime
import json
import time
import pandas as pd
import os
import zipfile
import numpy as np
import math

import statsprocessor


# TODO make option to sum players/teams stats better. Insert "all players earlier in result"?
# TODO fix period updating of player index?
# consider maing the temporary innings stats in result inside a dictionary itself so easy to access?
# I have to fix all the players ball stats.
# also why does every innings tally for teams have 2 values? not necessary right?

class search:
    def __init__(self, players=None, teams=None, allplayers=False, allteams=False) -> None:
        self.players = players
        self.teams = teams
        self.allplayers = allplayers
        self.allteams = allteams
        self.result = None
        self.inningsresult = None
        self.ballresult = None
        self.playersballresult = None
        self.teamsballresult = None

    # Setup the statistics to be recorded.
    def playerinningsresultsetup(self):
        self.inningsresult = { 
        "Date":[], "Match Type":[], "Venue":[], "Event":[], "Players":[], "Team":[], "Opposition":[], "Innings":[], 
        "Batting Position":[], "Score": [], "Balls Faced": [], "How Out": [],
        "Batting S/R":[], "Runs/Ball":[], "First Boundary Ball":[], 
        "Bowling Position":[], "Runsgiven": [], "Wickets": [], "Overs Bowled": [], 
        'Economy Rate': [], 'Bowling Avg': [], 'Bowling S/R': [], "Runsgiven/Ball":[], "Avg Consecutive Dot Balls":[]
        }


    # for eachplayer in self.players:
    def addplayerstoresult(self, eachplayer):
        self.result[eachplayer] = {"Players": eachplayer, "Games": 0, "Won": 0, "Drawn": 0, 'Win %': 0,

                                    "Innings Batted": 0, "batinningscount": False,
                                    "inningsruns": [], "inningsballsfaced": 0, "inningspartners":[], "inningsbowlersfaced":[], "inningshowout": [], "inningsbowlersfaced":[], "inningsbowlersfacedtype":[],
                                    "teaminningsscore":[], "teaminningsballs":[],
                                    "Runs": 0, "Fours": 0, "Sixes": 0, "Dot Balls": 0, "Balls Faced": 0, "Outs": 0, 
                                    "Bowled Outs": 0, "LBW Outs": 0, "Caught Outs": 0, "Stumped Outs": 0, "Run Outs": 0, "Caught and Bowled Outs": 0, 
                                    "totalstos": 0, "totalstosopp": 0, 
                                    'Dot Ball %': 0, 'Strike Turnover %': 0, 'Batting S/R': 0, 'Batting S/R MeanAD': 0, 'Batting Avg': 0, "Mean Score":0, 'Score MeanAD': 0, "Consistency Factor":0, 'Boundary %': 0, "Runs/Ball":0,
                                    "Mean Balls Faced":0, "Balls Faced MeanAD":0,
                                    "firstboundary": [], 'Avg First Boundary Ball': 0,
                                    
                                    "Innings Bowled":0, "bowlinningscount": False,
                                    "inningsrunsgiven": [], "inningsballsbowled": 0, "inningswickets": [], "teaminningsballsbowled":[], "inningsbattersbowledat":[],"inningsbattersbowledattype":[], "inningswicketstype":[],
                                    "teaminningsrunsgiven":[],"teaminningswickets":[],"teaminningsballsbowled":[],
                                    "Runsgiven": 0, "Foursgiven": 0, "Sixesgiven": 0, 
                                    "Wickets": 0, "Balls Bowled": 0, "Extras": 0, "No Balls": 0, "Wides":0,
                                    "Dot Balls Bowled": 0, 
                                    "Bowleds": 0, "LBWs": 0, "Hitwickets": 0, "Caughts": 0, "Stumpeds": 0, "Caught and Bowleds": 0,
                                    "totalstosgiven": 0, "totalstosgivenopp": 0, 
                                    "Catches": 0, "Runouts": 0, "Stumpings": 0, 
                                    'Economy Rate': 0, 'Economy Rate MeanAD': 0, 'Dot Ball Bowled %': 0,'Boundary Given %': 0, 'Bowling Avg': 0, "Bowling Avg MeanAD": 0, 'Bowling S/R': 0, "Bowling S/R MeanAD": 0,  "Runsgiven/Ball":0, "dotballseries": [], "Avg Consecutive Dot Balls": 0}

    def teaminningsresultsetup(self):
        self.inningsresult = {
        "Date":[], "Match Type":[],"Venue":[],"Batting Team":[], "Bowling Team":[], "Innings":[], 
        "Defended Score": [], "Chased Score": [], "Margin":[], 
        "Score": [],"Outs": [], "Overs": [],
        "Runs/Outs":[], "Runs/Ball":[], "Run Rate":[], "First Boundary Ball":[],
        "Avg Consecutive Dot Balls":[]
        }

    # for eachteam in self.teams:
    def addteamstoresult(self, eachteam):
        self.result[eachteam] = {"Teams": eachteam, "Games": 0, "Innings Bowled":0, "bowlinningscount": False, "Innings Batted": 0,
                                "batinningscount": False, "Won": 0, "Drawn": 0, 'Win %': 0, "Defended Wins": 0, "Chased Wins": 0, 
                                "Net Boundary %":0, "Net Run Rate":0,
                                
                                "inningsruns": [], "inningsballsfaced": 0, "inningsouts": 0, "inningsballs": [], "inningsballinover":[], "inningsoutsbyball": [], "inningshowout":[], "inningsstrikers": [],"inningsnonstrikers": [],"inningsbowlersfaced": [],"inningsstrikersbattingpos":[],"inningsstrikerstype":[],"inningsbowlersfacedtype": [], "inningsextras":[], "firstboundary": [],
                                "Runs": 0, "Fours": 0, "Sixes": 0, "Dot Balls": 0, "Outs": 0, "Balls Faced": 0, 
                                "Bowled Outs": 0, "LBW Outs": 0, "Caught Outs": 0, "Stumped Outs": 0, "Run Outs": 0, "Caught and Bowled Outs": 0,
                                "Runs/Outs":0, "Runs/Ball":0, "Run Rate":0, 'Avg First Boundary Ball': 0,
                                'Dot Ball %': 0, 'Score MeanAD': 0, "Consistency Factor":0, 'Boundary %': 0, 
                                
                                "inningsrunsgiven": [], "inningsballsbowled": 0, "inningswickets": 0, "inningswicketsbyball":[], "inningswicketstype":[],"inningsstrikersbowledat":[], "inningsnonstrikersbowledat":[],"inningsbowlers":[],"inningsstrikersbowledatbattingpos":[],"inningsbowlerstype":[],"inningsstrikersbowledattype":[], "inningsextrasbowled":[],
                                "Runsgiven":0,"Foursgiven": 0, "Sixesgiven": 0, 
                                "Wickets": 0, "Balls Bowled": 0, "Extras": 0, "No Balls": 0, "Wides":0, "Byes": 0, "Leg Byes": 0, "Dot Balls Bowled": 0, 
                                "Bowleds": 0, "LBWs": 0, "Hitwickets": 0,  "Caughts": 0, "Runouts": 0, "Stumpeds": 0, "Caught and Bowleds": 0,
                                'Dot Ball Bowled %': 0,'Boundary Given %': 0,'Runsgiven/Wicket': 0, "Runsgiven/Ball":0, "Runsgiven Rate": 0,
                                "Avg Consecutive Dot Balls": 0, "dotballseries": [],
                                "inningstally":{"inningsruns": [], "inningsballsfaced": 0, "inningsouts": 0, "inningsballs": [], "inningsballinover":[], "inningsoutsbyball": [], "inningshowout":[], "inningsstrikers": [],"inningsnonstrikers": [],"inningsbowlers": [],"inningsstrikersbattingpos":[],"inningsstrikerstype":[],"inningsbowlerstype": [], "inningsextras":[],"inningsextrastype":[]}
                                }

    # Setup results for ball by ball stats.
    def ballresultsetup(self):
        self.ballresult = { 
        "Date":[], "Match Type":[], "Venue":[], "Batting Team":[], "Bowling Team":[], "Innings":[], "Ball":[], "Ball in Over":[], 
        "Batting Position":[], "Batter":[], "Batter Score": [], "Non_striker": [],
        "Bowling Position":[], "Bowler": [], "Wicket": [], "How Out": [], 
        "Extras": [], "Extras Type": [], "Total Runs": []
        }

    def playersballresultsetup(self):
        self.playersballresult = { 
        "Date":[], "Match Type":[], "Venue":[], "Batting Team":[], "Bowling Team":[], "Innings":[], "Innings Ball":[], 
        "Batting Position":[], "Batter":[], "Non_striker": [], "Batter Score": [], "Balls Faced":[],
        "Runs/Ball": [], "Current Score":[], "Final Score":[], "How Out": [],
        "Bowler": [],"Bowling Position":[], "Balls Bowled":[], "Wicket": [],
        "Extras": [], "Extras Type": [],
        "Current Wickets": [], "Final Wickets":[], 
        "Runsgiven": [], "Runsgiven/Ball": [], "Current Runsgiven": [], "Final Runsgiven":[]
        }

    def teamsballresultsetup(self):
        self.teamsballresult = { 
        "Date":[], "Match Type":[], "Venue":[], "Batting Team":[], "Bowling Team":[], "Innings":[], "Ball":[], "Ball in Over":[],
        "Current Score":[], "Current Outs":[], "Final Score":[],
        "Batter":[], "Batting Position":[],"Batter Type":[], "Non_striker": [], "Runs Scored": [], "Runs/Ball": [], "How Out": [],
        "Bowler": [], "Bowler Type":[], "Extras":[], "Extras Type": [], "Out/NotOut":[],
        }

    # Indexes matches by match type for quick search.
    def fileindexing(self, database, matches):
        currentdir = os.path.dirname(os.path.abspath(__file__))
        databasemtime = os.path.getmtime(database)
        databasetime = time.gmtime(databasemtime)
        databaseyear = int(databasetime[0])
        if not os.path.exists(f"{currentdir}/matchindex.json"):
            newmatchindex = {"file": "", 'indexedtime': 0, "matches":{"Test": {}, "MDM":{}, "ODI":{}, "ODM": {}, "T20":{}, "IT20":{}}}
            for eachmatchtype in newmatchindex["matches"]:
                for eachyear in range(2000, (databaseyear + 1)):
                    newmatchindex["matches"][eachmatchtype][f"{eachyear}"] = []
            file = open(f"{currentdir}/matchindex.json", "w")
            file.write(json.dumps(newmatchindex))
            file.close()

        matchindexfile=open(f"{currentdir}/matchindex.json")
        matchindex = json.load(matchindexfile)
        if os.path.getmtime(database) > matchindex['indexedtime']:
            print("It looks like your database is newer than the index, please wait while the new matches in the database are indexed.")
            newmatchindex = matchindex
            matchindexfile.close()
            for eachmatchtype in matchindex["matches"]:
                if f"{databaseyear}" not in matchindex["matches"][eachmatchtype].keys():
                    matchindex["matches"][eachmatchtype][f"{databaseyear}"] = []
            matchindex['indexedtime'] = os.path.getmtime(database)
            matchindex['file'] = matches.filename
            filelist = matches.namelist()
            for eachfile in filelist:
                if ".json" not in eachfile:
                    continue
                matchdata = matches.open(eachfile)
                match = json.load(matchdata)
                if eachfile not in newmatchindex["matches"][match["info"]["match_type"]][match["info"]["dates"][0][:4]]:
                    newmatchindex["matches"][match["info"]["match_type"]][match["info"]["dates"][0][:4]].append(eachfile)
                matchdata.close
            
            file = open(f"{currentdir}/matchindex.json", "w")
            file.write(json.dumps(newmatchindex))
            file.close()
        if os.path.getmtime(database) < matchindex["indexedtime"]:
            matchindexfile.close()
            raise Exception("Your cricsheet database is older than the index, please download the newest zip file from https://cricsheet.org/downloads/all_json.zip")
        matchindexfile.close()
            
    # Record games played, wins, draws
    def gamesandwins(self, matchinfo):
        if self.players or self.allplayers==True:
            for eachplayer in self.result:
                for eachteam in matchinfo["players"]:
                    if eachplayer in matchinfo["players"][eachteam]:
                        self.result[eachplayer]["Games"] += 1
                        if "result" in matchinfo["outcome"] and matchinfo["outcome"]['result'] == "draw":
                            self.result[eachplayer]["Drawn"] += 1
                        if "winner" in matchinfo["outcome"] and eachteam == matchinfo["outcome"]["winner"]:
                            self.result[eachplayer]["Won"] += 1

        if self.teams or self.allteams==True:
            for eachteam in matchinfo["teams"]:
                if eachteam not in self.result:
                    continue
                self.result[eachteam]["Games"] += 1
                if "result" in matchinfo["outcome"] and matchinfo["outcome"]['result'] == "draw":
                    self.result[eachteam]["Drawn"] += 1
                if "winner" in matchinfo["outcome"] and eachteam in matchinfo["outcome"]["winner"]:
                    self.result[matchinfo["outcome"]
                                ["winner"]]["Won"] += 1
    
    # rest innings lists 
    def setupinningscores(self):
        if self.players or self.allplayers==True:
            for eachplayer in self.result:
                self.result[eachplayer]["batinningscount"] = False
                self.result[eachplayer]["inningsruns"] = []
                self.result[eachplayer]["inningsballsfaced"] = 0
                self.result[eachplayer]["inningspartners"]=[]
                self.result[eachplayer]["inningshowout"] = []
                self.result[eachplayer]["inningsbowlersfaced"]=[]
                self.result[eachplayer]["inningsbowlersfacedtype"]=[]
                self.result[eachplayer]["teaminningsscore"] = []
                self.result[eachplayer]["teaminningsballs"] = []

                self.result[eachplayer]["bowlinningscount"] = False
                self.result[eachplayer]["inningsrunsgiven"] = []
                self.result[eachplayer]["inningsballsbowled"] = 0
                self.result[eachplayer]["inningsbattersbowledat"]=[]
                self.result[eachplayer]["inningsbattersbowledattype"]=[]
                self.result[eachplayer]["inningswickets"] = []
                self.result[eachplayer]["inningswicketstype"] = []
                self.result[eachplayer]["teaminningsrunsgiven"] = []
                self.result[eachplayer]["teaminningswickets"] = []
                self.result[eachplayer]["teaminningsballsbowled"] = []

        if self.teams or self.allteams==True:
            for eachteam in self.result:                
                self.result[eachteam]["batinningscount"] = False
                self.result[eachteam]["inningsouts"] = 0
                self.result[eachteam]["inningsruns"] = []
                self.result[eachteam]["inningsballsfaced"] = 0
                self.result[eachteam]["inningsballs"] = []
                self.result[eachteam]["inningsoutsbyball"] = []
                self.result[eachteam]["inningshowout"] = []
                self.result[eachteam]["inningsstrikers"] = []
                self.result[eachteam]["inningsnonstrikers"] = []
                self.result[eachteam]["inningsbowlersfaced"] = []
                self.result[eachteam]["inningsstrikersbattingpos"] = []
                self.result[eachteam]["inningsstrikerstype"] = []
                self.result[eachteam]["inningsbowlersfacedtype"] = []
                self.result[eachteam]["inningsballinover"] = []
                self.result[eachteam]["inningsextras"] = []


                self.result[eachteam]["bowlinningscount"] = False
                self.result[eachteam]["inningswickets"] = 0
                self.result[eachteam]["inningsrunsgiven"] = []
                self.result[eachteam]["inningsballsbowled"] = 0
                self.result[eachteam]["inningswicketsbyball"] = []
                self.result[eachteam]["inningswicketstype"] = []
                self.result[eachteam]["inningsstrikersbowledat"] = []
                self.result[eachteam]["inningsnonstrikersbowledat"] = []
                self.result[eachteam]["inningsbowlers"] = []
                self.result[eachteam]["inningsstrikersbowledatbattingpos"] = []
                self.result[eachteam]["inningsbowlerstype"] = []
                self.result[eachteam]["inningsstrikersbowledattype"] = []
                self.result[eachteam]["inningsextrasbowled"] = []

    # Record striker's stats for each ball.
    def strikerstats(self, eachball, nthball, eachover,tempplayerindex):
        self.result[eachball['batter']]["batinningscount"] = True
        self.result[eachball['batter']
                    ]["Runs"] += eachball['runs']['batter']
        self.result[eachball['batter']]["inningsruns"].append(eachball['runs']['batter'])
        self.result[eachball['batter']]["inningsbowlersfaced"].append(
            eachball['bowler'])
        over=eachover["over"]
        ball=nthball+1
        self.result[eachball['batter']]["teaminningsballs"].append(float(f"{over}.{ball}"))
        self.result[eachball['batter']]["inningspartners"].append(eachball["non_striker"])
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
                if eachball['batter'] == eachwicket["player_out"]:
                    self.result[eachball['batter']
                                ]["Outs"] += 1
                    self.result[eachball['batter']
                            ]["inningshowout"].append(eachwicket["kind"])
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
                    if eachwicket["kind"] == "caught and bowled":
                        self.result[eachball['batter']
                                    ]["Caught and Bowled Outs"] += 1
        if "wickets" not in eachball:
            self.result[eachball['batter']]["inningshowout"].append(None)
        if (nthball+1) < len(eachover["deliveries"]):
            search.striketurnoverstats(self, eachball, 1, 3)
        if (nthball+1) == len(eachover["deliveries"]):
            search.striketurnoverstats(self, eachball, 0, 2)

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

    # Record strike turn over stats for strikers. 
    def striketurnoverstats(self, eachball, case1, case2):
        # if eachball['batter'] in self.players:
        self.result[eachball['batter']
                    ]["totalstosopp"] += 1
        if eachball['runs']['batter'] == case1 or eachball['runs']['batter'] == case2:
            self.result[eachball['batter']]["totalstos"] += 1
        if "extras" in eachball:
            if not ("wides" in eachball['extras'] or "noballs" in eachball['extras']) and (eachball['runs']['extras'] == case1 or eachball['runs']['extras'] == case2):
                self.result[eachball['batter']]["totalstos"] += 1

    # Record strike turn over given stats for bowlers.
    def striketurnovergivenstats(self, eachball, case1, case2):
        # if eachball['bowler'] in self.players:
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
    def bowlerstats(self, eachball, fielders, nthball, eachover):
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
        over=eachover["over"]
        ball=nthball+1
        self.result[eachball['bowler']]["teaminningsballsbowled"].append(float(f"{over}.{ball}"))
        self.result[eachball['bowler']]["inningsbattersbowledat"].append(eachball["batter"])
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
                                ]["inningswickets"].append(1)
                    self.result[eachball['bowler']
                            ]["inningswicketstype"].append(eachwicket["kind"])
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
                if eachwicket["kind"] == "caught and bowled":
                    self.result[eachball['bowler']
                                ]["Caught and Bowleds"] += 1
        if "wickets" not in eachball:
            self.result[eachball['bowler']]["inningswickets"].append(0)
            self.result[eachball['bowler']]["inningswicketstype"].append(None)
        if (nthball+1) < len(eachover["deliveries"]):
            search.striketurnovergivenstats(self, eachball, 1, 3)
        if (nthball+1) == len(eachover["deliveries"]):
            search.striketurnovergivenstats(self, eachball, 0, 2)
    
    # Record fieling stats for players.
    def fieldingstats(self, eachball):
        for eachwicket in eachball["wickets"]:
            if "fielders" in eachwicket:
                for eachfielder in eachwicket["fielders"]:
                    if "name" not in eachfielder:
                        continue
                    if eachfielder["name"] in self.result:
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
    def teambattingstats(self, eachball, inningsteam, nthball, eachover, battingorder,tempplayerindex):
        self.result[inningsteam]["batinningscount"] = True
        self.result[inningsteam]["inningsstrikers"].append(eachball["batter"])
        self.result[inningsteam]["inningsnonstrikers"].append(eachball["non_striker"])
        self.result[inningsteam]["inningsstrikersbattingpos"].append(battingorder.index(eachball["batter"]) + 1)
        self.result[inningsteam]["inningsbowlersfaced"].append(eachball["bowler"])
        self.result[inningsteam]["inningsruns"].append(eachball['runs']['total'])
        self.result[inningsteam]["inningsextras"].append(eachball['runs']['extras'])
        over=eachover["over"]
        ball=nthball+1
        self.result[inningsteam]["inningsballs"].append(float(f"{over}.{ball}"))
        self.result[inningsteam]["inningsballinover"].append(ball)
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
            self.result[inningsteam]["inningsoutsbyball"].append((len(battingorder)-1))
            for eachwicket in eachball["wickets"]:
                self.result[inningsteam
                            ]["inningshowout"].append(eachwicket["kind"])
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
                if eachwicket["kind"] == "caught and bowled":
                    self.result[inningsteam]["Caught and Bowled Outs"] += 1
        if "wickets" not in eachball:
            self.result[inningsteam]["inningsoutsbyball"].append((len(battingorder)-2))
            self.result[inningsteam]["inningshowout"].append(None)

    # Record team's bowling stats
    def teambowlingstats(self, eachball, inningsteam, nthball, eachover, battingorder,tempplayerindex):
        self.result[inningsteam]["bowlinningscount"] = True
        self.result[inningsteam]["inningsstrikersbowledat"].append(eachball["batter"])
        self.result[inningsteam]["inningsnonstrikersbowledat"].append(eachball["non_striker"])
        self.result[inningsteam]["inningsstrikersbowledatbattingpos"].append(battingorder.index(eachball["batter"]) + 1)
        self.result[inningsteam]["inningsbowlers"].append(eachball["bowler"])
        self.result[inningsteam]["inningsrunsgiven"].append(eachball['runs']['total'])
        self.result[inningsteam]["inningsextrasbowled"].append(eachball['runs']['extras'])
        over=eachover["over"]
        ball=nthball+1
        self.result[inningsteam]["inningsballs"].append(float(f"{over}.{ball}"))
        self.result[inningsteam]["inningsballinover"].append(ball)
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
            self.result[inningsteam]["inningswicketsbyball"].append((len(battingorder)-1))
            for eachwicket in eachball["wickets"]:
                self.result[inningsteam]["inningswicketstype"].append(eachwicket["kind"])
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
                if eachwicket["kind"] == "caught and bowled":
                    self.result[inningsteam]["Caught and Bowleds"] += 1
        if "wickets" not in eachball:
            self.result[inningsteam]["inningswicketsbyball"].append((len(battingorder)-2))
            self.result[inningsteam]["inningswicketstype"].append(None)

    # Record raw ballstats.
    def ballstats(self, matchtimetuple, matchinfo, nthinnings, eachinnings, eachball, nthball, eachover, battingorder, bowlingorder):
        for eachteam in matchinfo["teams"]:
            if eachteam == eachinnings["team"]:
                battingteam = eachteam
            if eachteam != eachinnings["team"]:
                bowlingteam = eachteam

        self.ballresult["Date"].append(datetime.date(matchtimetuple[0], matchtimetuple[1], matchtimetuple[2]))
        self.ballresult["Match Type"].append(matchinfo["match_type"])
        self.ballresult["Venue"].append(matchinfo["venue"])
        self.ballresult["Batting Team"].append(battingteam)
        self.ballresult["Bowling Team"].append(bowlingteam)
        self.ballresult["Innings"].append(nthinnings + 1)
        over = (eachover["over"])
        ball = (nthball + 1)
        self.ballresult["Ball"].append(float(f"{over}.{ball}"))
        self.ballresult["Ball in Over"].append((nthball + 1))
        
        self.ballresult["Batting Position"].append(battingorder.index(eachball["batter"]) + 1)
        self.ballresult["Batter"].append(eachball["batter"])
        self.ballresult["Batter Score"].append(eachball["runs"]["batter"])
        self.ballresult["Non_striker"].append(eachball["non_striker"])

        self.ballresult["Bowling Position"].append(bowlingorder.index(eachball["bowler"]) + 1)
        self.ballresult["Bowler"].append(eachball["bowler"])
        if "wickets" in eachball:
            self.ballresult["Wicket"].append(True)
            # for eachwicket in eachball["wickets"]:
            self.ballresult["How Out"].append(eachball["wickets"][0]["kind"])
        if "wickets" not in eachball:
            self.ballresult["Wicket"].append(False)
            self.ballresult["How Out"].append(None)
        if "extras" in eachball:
            self.ballresult["Extras"].append(eachball["runs"]["extras"])
            self.ballresult["Extras Type"].append( eachball['extras'].keys())
        if "extras" not in eachball:
            self.ballresult["Extras"].append(None)
            self.ballresult["Extras Type"].append(None)
        self.ballresult["Total Runs"].append(eachball["runs"]["total"])

    # Record player's innings stats
    def playerinnings(self, matchtimetuple, matchinfo, nthinnings, eachmatchtype, battingorder, bowlingorder):
        for eachplayer in self.result:
            for eachteam in matchinfo["players"]:
                if eachplayer in matchinfo["players"][eachteam]:
                    playersteam = eachteam
                if eachplayer not in matchinfo["players"][eachteam]:
                    oppositionteam = eachteam

            if self.result[eachplayer]["batinningscount"] == True:
                # record playersinningsresult
                self.result[eachplayer]["Innings Batted"] += 1
                if 4 in self.result[eachplayer]["inningsruns"] or 6 in self.result[eachplayer]["inningsruns"]:
                    self.result[eachplayer]["firstboundary"].append(statsprocessor.firstboundary(self.result[eachplayer]["inningsruns"]))

                self.inningsresult["Players"].append(eachplayer)
                self.inningsresult["Venue"].append(matchinfo["venue"])
                if "event" in matchinfo and "name" in matchinfo["event"]:
                    self.inningsresult["Event"].append(matchinfo["event"]["name"])
                if "event" not in matchinfo or "name" not in matchinfo["event"]:
                    self.inningsresult["Event"].append(None)
                self.inningsresult["Date"].append(datetime.date(matchtimetuple[0], matchtimetuple[1], matchtimetuple[2]))
                self.inningsresult["Match Type"].append(eachmatchtype)
                self.inningsresult["Team"].append(playersteam)
                self.inningsresult["Opposition"].append(oppositionteam)
                self.inningsresult["Innings"].append(nthinnings + 1)

                self.inningsresult["Batting Position"].append(battingorder.index(eachplayer) + 1)
                self.inningsresult["Score"].append(
                    sum(self.result[eachplayer]["inningsruns"]))
                self.inningsresult["Balls Faced"].append(
                    self.result[eachplayer]["inningsballsfaced"])
                if self.result[eachplayer]["inningshowout"]:
                    self.inningsresult["How Out"].append(self.result[eachplayer]["inningshowout"])
                if not self.result[eachplayer]["inningshowout"]:
                    self.inningsresult["How Out"].append("Not Out")
                self.inningsresult["Batting S/R"].append(statsprocessor.ratio(sum(self.result[eachplayer]["inningsruns"]), self.result[eachplayer]["inningsballsfaced"], multiplier=100))
                self.inningsresult["Runs/Ball"].append(statsprocessor.ratio(sum(self.result[eachplayer]["inningsruns"]), self.result[eachplayer]["inningsballsfaced"]))
                self.inningsresult["First Boundary Ball"].append(statsprocessor.firstboundary(
                    self.result[eachplayer]["inningsruns"]))

                for eachstat in ["Bowling Position","Runsgiven","Wickets","Overs Bowled","Economy Rate","Bowling Avg","Bowling S/R","Runsgiven/Ball","Avg Consecutive Dot Balls"]:
                    self.inningsresult[eachstat].append(None)

                # record playersballresult
                for eachball, (eachshot, inningsball, non_striker, bowler, howout) in enumerate(zip(self.result[eachplayer]["inningsruns"],self.result[eachplayer]["teaminningsballs"], self.result[eachplayer]["inningspartners"], self.result[eachplayer]["inningsbowlersfaced"],self.result[eachplayer]["inningshowout"])):
                    self.playersballresult["Date"].append(datetime.date(matchtimetuple[0], matchtimetuple[1], matchtimetuple[2]))
                    self.playersballresult["Match Type"].append(matchinfo["match_type"])
                    self.playersballresult["Venue"].append(matchinfo["venue"])
                    self.playersballresult["Batting Team"].append(playersteam)
                    self.playersballresult["Bowling Team"].append(oppositionteam)
                    self.playersballresult["Innings"].append(nthinnings + 1)
                    self.playersballresult["Innings Ball"].append(inningsball)
                    
                    self.playersballresult["Batter"].append(eachplayer)
                    self.playersballresult["Non_striker"].append(non_striker)
                    self.playersballresult["Batting Position"].append(battingorder.index(eachplayer) + 1)
                    self.playersballresult["Batter Score"].append(eachshot)
                    self.playersballresult["Current Score"].append(sum(self.result[eachplayer]["inningsruns"][:(eachball+1)]))
                    self.playersballresult["Balls Faced"].append((eachball + 1))
                    self.playersballresult["Final Score"].append(sum(self.result[eachplayer]["inningsruns"]))
                    if eachball == (len(self.result[eachplayer]["inningshowout"])-1) and howout==None:
                        self.playersballresult["How Out"].append("Not Out")
                    if eachball!=(len(self.result[eachplayer]["inningshowout"])-1) or (eachball == (len(self.result[eachplayer]["inningshowout"])-1) and howout!=None):
                        self.playersballresult["How Out"].append(howout)
                    self.playersballresult["Runs/Ball"].append(sum(self.result[eachplayer]["inningsruns"][:(eachball+1)])/(eachball+1))

                    self.playersballresult["Bowler"].append(bowler)
                    self.playersballresult["Bowling Position"].append(None)
                    self.playersballresult["Current Wickets"].append(None)
                    self.playersballresult["Final Wickets"].append(None)
                    self.playersballresult["Runsgiven"].append(None)
                    self.playersballresult["Runsgiven/Ball"].append(None)
                    self.playersballresult["Current Runsgiven"].append(None)
                    self.playersballresult["Balls Bowled"].append(None)
                    self.playersballresult["Wicket"].append(None)
                    self.playersballresult["Extras Type"].append(None)
                    self.playersballresult["Extras"].append(None)
                    self.playersballresult["Final Runsgiven"].append(None)

            if self.result[eachplayer]["bowlinningscount"] == True:
                self.result[eachplayer]["Innings Bowled"] += 1
                self.result[eachplayer]["dotballseries"].extend(statsprocessor.dotballseries(self.result[eachplayer]["inningsrunsgiven"]))
                self.inningsresult["Players"].append(eachplayer)
                self.inningsresult["Venue"].append(matchinfo["venue"])
                if "event" in matchinfo and "name" in matchinfo["event"]:
                    self.inningsresult["Event"].append(matchinfo["event"]["name"])
                if "event" not in matchinfo or "name" not in matchinfo["event"]:
                    self.inningsresult["Event"].append(None)
                self.inningsresult["Date"].append(datetime.date(matchtimetuple[0], matchtimetuple[1], matchtimetuple[2]))
                self.inningsresult["Match Type"].append(eachmatchtype)
                self.inningsresult["Team"].append(playersteam)
                self.inningsresult["Opposition"].append(oppositionteam)
                self.inningsresult["Innings"].append(nthinnings + 1)

                for eachstat in ["Batting Position","Score","Balls Faced","How Out","Batting S/R","Runs/Ball","First Boundary Ball"]:
                    self.inningsresult[eachstat].append(None)

                self.inningsresult["Bowling Position"].append(bowlingorder.index(eachplayer) + 1)
                self.inningsresult["Runsgiven"].append(
                    sum(self.result[eachplayer]["inningsrunsgiven"]))
                self.inningsresult["Wickets"].append(
                    self.result[eachplayer]["inningswickets"])
                self.inningsresult["Overs Bowled"].append(
                    math.ceil(self.result[eachplayer]["inningsballsbowled"] / 6))
                if self.result[eachplayer]["inningsballsbowled"]:
                    self.inningsresult["Economy Rate"].append(round(sum(self.result[eachplayer]["inningsrunsgiven"]) / (math.ceil(self.result[eachplayer]["inningsballsbowled"] / 6)),2))
                    self.inningsresult["Runsgiven/Ball"].append(statsprocessor.ratio(sum(self.result[eachplayer]["inningsrunsgiven"]), self.result[eachplayer]["inningsballsbowled"]))
                if not self.result[eachplayer]["inningsballsbowled"]:
                    self.inningsresult["Economy Rate"].append(None)
                    self.inningsresult["Runsgiven/Ball"].append(None)
                if sum(self.result[eachplayer]["inningswickets"])>0:
                    self.inningsresult["Bowling Avg"].append(round(
                        sum(self.result[eachplayer]["inningsrunsgiven"]) / 
                        sum(self.result[eachplayer]["inningswickets"]),2))
                    self.inningsresult["Bowling S/R"].append(round(self.result[eachplayer]["inningsballsbowled"] / sum(self.result[eachplayer]["inningswickets"]),2))
                if sum(self.result[eachplayer]["inningswickets"])==0:
                    self.inningsresult["Bowling Avg"].append(None)
                    self.inningsresult["Bowling S/R"].append(None)
                if 0 in self.result[eachplayer]["inningsrunsgiven"]:
                    self.inningsresult["Avg Consecutive Dot Balls"].append(round(np.mean(statsprocessor.dotballseries(self.result[eachplayer]["inningsrunsgiven"]))))
                if 0 not in self.result[eachplayer]["inningsrunsgiven"]:
                    self.inningsresult["Avg Consecutive Dot Balls"].append(0)

                # setup bowling playersballresult
                for eachball, (eachballrun, inningsball, batter) in enumerate(zip(self.result[eachplayer]["inningsrunsgiven"],self.result[eachplayer]["teaminningsballsbowled"], self.result[eachplayer]["inningsbattersbowledat"])):
                    self.playersballresult["Date"].append(datetime.date(matchtimetuple[0], matchtimetuple[1], matchtimetuple[2]))
                    self.playersballresult["Match Type"].append(matchinfo["match_type"])
                    self.playersballresult["Venue"].append(matchinfo["venue"])
                    self.playersballresult["Batting Team"].append(oppositionteam)
                    self.playersballresult["Bowling Team"].append(playersteam)
                    self.playersballresult["Innings"].append(nthinnings + 1)
                    self.playersballresult["Innings Ball"].append(inningsball)
                    
                    self.playersballresult["Batter"].append(batter)
                    self.playersballresult["Non_striker"].append(None)
                    self.playersballresult["Batting Position"].append(None)
                    self.playersballresult["Batter Score"].append(None)
                    self.playersballresult["Current Score"].append(None)
                    self.playersballresult["Balls Faced"].append(None)
                    self.playersballresult["Final Score"].append(None)
                    self.playersballresult["How Out"].append(None)
                    self.playersballresult["Runs/Ball"].append(None)

                    self.playersballresult["Bowler"].append(eachplayer)
                    self.playersballresult["Bowling Position"].append(bowlingorder.index(eachplayer) + 1)
                    self.playersballresult["Current Wickets"].append(sum(self.result[eachplayer]["inningswickets"][:(eachball+1)]))
                    self.playersballresult["Final Wickets"].append(sum(self.result[eachplayer]["inningswickets"]))
                    self.playersballresult["Runsgiven"].append(eachballrun)
                    self.playersballresult["Runsgiven/Ball"].append(sum(self.result[eachplayer]["inningsrunsgiven"][:(eachball+1)])/(eachball+1))
                    self.playersballresult["Current Runsgiven"].append(sum(self.result[eachplayer]["inningsrunsgiven"][:(eachball+1)]))
                    self.playersballresult["Balls Bowled"].append(eachball)
                    self.playersballresult["Wicket"].append(None)
                    self.playersballresult["Extras Type"].append(None)
                    self.playersballresult["Extras"].append(None)
                    self.playersballresult["Final Runsgiven"].append(sum(self.result[eachplayer]["inningsrunsgiven"]))
                
    # Record team inningsresult
    # TODO have to fix overs faced. it should be "17.5" format. not diviede by 6
    def teaminnings(self, inningsteam, nthinnings, matchinfo, matchtimetuple, matchinnings,tempplayerindex):
        for eachteam in matchinfo["teams"]:
            if eachteam != inningsteam:
                bowlingteam = eachteam

        self.inningsresult["Date"].append(datetime.date(matchtimetuple[0], matchtimetuple[1], matchtimetuple[2]))
        self.inningsresult["Match Type"].append(matchinfo["match_type"])
        self.inningsresult["Venue"].append(matchinfo["venue"])
        self.inningsresult["Batting Team"].append(inningsteam)
        self.inningsresult["Bowling Team"].append(bowlingteam)
        self.inningsresult["Innings"].append(nthinnings + 1)

        if (inningsteam in self.result and bowlingteam not in self.result) or (inningsteam in self.result and bowlingteam in self.result):
            if 4 in self.result[inningsteam]["inningsruns"] or 6 in self.result[inningsteam]["inningsruns"]:
                self.result[inningsteam]["firstboundary"].append(statsprocessor.firstboundary(self.result[inningsteam]["inningsruns"]))

            if self.result[inningsteam]["batinningscount"] == True:
                self.result[inningsteam]["Innings Batted"] += 1
            if bowlingteam in self.result:
                if self.result[bowlingteam]["bowlinningscount"] == True:
                    self.result[bowlingteam]["Innings Bowled"] += 1
                self.result[bowlingteam]["dotballseries"].extend(statsprocessor.dotballseries(self.result[inningsteam]["inningsruns"]))

            self.inningsresult["Score"].append(
                sum(self.result[inningsteam]["inningsruns"]))
            self.inningsresult["Outs"].append(self.result[inningsteam]["inningsouts"])
            self.inningsresult["Overs"].append(
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
            if 0 in self.result[inningsteam]["inningsruns"]:
                self.inningsresult["Avg Consecutive Dot Balls"].append(round(np.mean(statsprocessor.dotballseries(self.result[inningsteam]["inningsruns"]))))
            if 0 not in self.result[inningsteam]["inningsruns"]:
                self.inningsresult["Avg Consecutive Dot Balls"].append(0)

            # record innings ballresult using batting team
            for eachball, (eachshot, inningsball, currentouts,howout,striker,nonstriker,bowler,strikerbattingpos,ballinover,extras) in enumerate(zip(self.result[inningsteam]["inningsruns"],self.result[inningsteam]["inningsballs"], self.result[inningsteam]["inningsoutsbyball"],self.result[inningsteam]["inningshowout"],self.result[inningsteam]["inningsstrikers"],self.result[inningsteam]["inningsnonstrikers"],self.result[inningsteam]["inningsbowlersfaced"],self.result[inningsteam]["inningsstrikersbattingpos"],self.result[inningsteam]["inningsballinover"],self.result[inningsteam]["inningsextras"])):
                self.teamsballresult["Date"].append(datetime.date(matchtimetuple[0], matchtimetuple[1], matchtimetuple[2]))
                self.teamsballresult["Match Type"].append(matchinfo["match_type"])
                self.teamsballresult["Venue"].append(matchinfo["venue"])
                self.teamsballresult["Batting Team"].append(inningsteam)
                self.teamsballresult["Bowling Team"].append(bowlingteam)
                self.teamsballresult["Innings"].append(nthinnings + 1)

                self.teamsballresult["Ball in Over"].append(ballinover)
                self.teamsballresult["Ball"].append(inningsball)
                self.teamsballresult["Current Score"].append(sum(self.result[inningsteam]["inningsruns"][:(eachball+1)]))
                self.teamsballresult["Current Outs"].append(currentouts)
                self.teamsballresult["Batter"].append(striker)
                self.teamsballresult["Batting Position"].append(strikerbattingpos)
                self.teamsballresult["Non_striker"].append(nonstriker)
                self.teamsballresult["Runs Scored"].append(eachshot)
                self.teamsballresult["Extras"].append(extras)
                self.teamsballresult["Extras Type"].append(None)
                self.teamsballresult["Runs/Ball"].append(
                    round(sum(self.result[inningsteam]["inningsruns"][:(eachball+1)])/(eachball+1),2))
                self.teamsballresult["Final Score"].append(sum(self.result[inningsteam]["inningsruns"]))
                if eachball == (len(self.result[inningsteam]["inningsruns"])-1) and howout==None:
                    self.teamsballresult["How Out"].append("Not Out")
                if eachball == (len(self.result[inningsteam]["inningsruns"])-1) and howout!=None:
                    self.teamsballresult["How Out"].append(howout)
                if eachball != (len(self.result[inningsteam]["inningsruns"])-1):
                    self.teamsballresult["How Out"].append(howout)
                if howout==None:
                    self.teamsballresult["Out/NotOut"].append("Not Out")
                if howout!=None:
                    self.teamsballresult["Out/NotOut"].append("Out")    
                self.teamsballresult["Bowler"].append(bowler)
                # self.teamsballresult["Batter Type"].append(strikertype)
                # self.teamsballresult["Bowler Type"].append(bowlertype)
                batterfound=False
                for eachtype in tempplayerindex["Batting"]:
                    if striker in tempplayerindex["Batting"][eachtype]:
                        batterfound=True
                        self.teamsballresult["Batter Type"].append(eachtype)
                bowlerfound=False
                for eachtype in tempplayerindex["Bowling"]:
                    if bowler in tempplayerindex["Bowling"][eachtype]:
                        bowlerfound=True
                        self.teamsballresult["Bowler Type"].append(eachtype)
                        break
                if batterfound==False:
                    self.teamsballresult["Batter Type"].append(None)
                if bowlerfound==False:
                    self.teamsballresult["Bowler Type"].append(None)

        if (inningsteam not in self.result and bowlingteam in self.result):
            if self.result[bowlingteam]["bowlinningscount"] == True:
                self.result[bowlingteam]["Innings Bowled"] += 1
                self.result[bowlingteam]["dotballseries"].extend(statsprocessor.dotballseries(self.result[bowlingteam]["inningsrunsgiven"]))
            self.inningsresult["Score"].append(
                sum(self.result[bowlingteam]["inningsrunsgiven"]))
            self.inningsresult["Outs"].append(self.result[bowlingteam]["inningswickets"])
            self.inningsresult["Overs"].append(
                math.ceil(self.result[bowlingteam]["inningsballsbowled"]/6))
            if self.result[bowlingteam]["inningswickets"] > 0:
                self.inningsresult["Runs/Outs"].append(statsprocessor.ratio(sum(self.result[bowlingteam]["inningsrunsgiven"]), self.result[bowlingteam]["inningswickets"]))
            if self.result[bowlingteam]["inningswickets"]==0:
                self.inningsresult["Runs/Outs"].append(
                sum(self.result[bowlingteam]["inningsrunsgiven"]))
            self.inningsresult["Runs/Ball"].append(statsprocessor.ratio(sum(self.result[bowlingteam]["inningsrunsgiven"]), self.result[bowlingteam]["inningsballsbowled"]))
            self.inningsresult["Run Rate"].append(statsprocessor.ratio(sum(self.result[bowlingteam]["inningsrunsgiven"]), self.result[bowlingteam]["inningsballsbowled"], multiplier=6))
            self.inningsresult["First Boundary Ball"].append(statsprocessor.firstboundary(
                self.result[bowlingteam]["inningsrunsgiven"]))
            if 0 in self.result[bowlingteam]["inningsrunsgiven"]:
                self.inningsresult["Avg Consecutive Dot Balls"].append(round(np.mean(statsprocessor.dotballseries(self.result[bowlingteam]["inningsrunsgiven"]))))
            if 0 not in self.result[bowlingteam]["inningsrunsgiven"]:
                self.inningsresult["Avg Consecutive Dot Balls"].append(0)

            # record innings ballresult using bowling team
            for eachball, (eachshot, inningsball, currentouts,howout,striker,nonstriker,bowler,strikerbattingpos,ballinover,extras) in enumerate(zip(self.result[bowlingteam]["inningsrunsgiven"],self.result[bowlingteam]["inningsballs"], self.result[bowlingteam]["inningswicketsbyball"],self.result[bowlingteam]["inningswicketstype"],self.result[bowlingteam]["inningsstrikersbowledat"],self.result[bowlingteam]["inningsnonstrikersbowledat"],self.result[bowlingteam]["inningsbowlers"],self.result[bowlingteam]["inningsstrikersbowledatbattingpos"],self.result[bowlingteam]["inningsballinover"],self.result[bowlingteam]["inningsextrasbowled"])):
                self.teamsballresult["Date"].append(datetime.date(matchtimetuple[0], matchtimetuple[1], matchtimetuple[2]))
                self.teamsballresult["Match Type"].append(matchinfo["match_type"])
                self.teamsballresult["Venue"].append(matchinfo["venue"])
                self.teamsballresult["Batting Team"].append(inningsteam)
                self.teamsballresult["Bowling Team"].append(bowlingteam)
                self.teamsballresult["Innings"].append(nthinnings + 1)

                self.teamsballresult["Ball in Over"].append(ballinover)
                self.teamsballresult["Ball"].append(inningsball)
                self.teamsballresult["Current Score"].append(sum(self.result[bowlingteam]["inningsrunsgiven"][:(eachball+1)]))
                self.teamsballresult["Current Outs"].append(currentouts)
                self.teamsballresult["Batter"].append(striker)
                self.teamsballresult["Batting Position"].append(strikerbattingpos)
                self.teamsballresult["Non_striker"].append(nonstriker)
                self.teamsballresult["Runs Scored"].append(eachshot)
                self.teamsballresult["Extras"].append(extras)
                self.teamsballresult["Extras Type"].append(None)
                self.teamsballresult["Runs/Ball"].append(round(sum(self.result[bowlingteam]["inningsrunsgiven"][:(eachball+1)])/(eachball+1),2))
                self.teamsballresult["Final Score"].append(sum(self.result[bowlingteam]["inningsrunsgiven"]))
                if eachball == (len(self.result[bowlingteam]["inningsrunsgiven"])-1) and howout==None:
                    self.teamsballresult["How Out"].append("Not Out")
                if eachball == (len(self.result[bowlingteam]["inningsrunsgiven"])-1) and howout!=None:
                    self.teamsballresult["How Out"].append(howout)
                if eachball != (len(self.result[bowlingteam]["inningsrunsgiven"])-1):
                    self.teamsballresult["How Out"].append(howout)
                if howout==None:
                    self.teamsballresult["Out/NotOut"].append("Not Out")
                if howout!=None:
                    self.teamsballresult["Out/NotOut"].append("Out") 
                self.teamsballresult["Bowler"].append(bowler)
                # self.teamsballresult["Batter Type"].append(strikertype)
                # self.teamsballresult["Bowler Type"].append(bowlertype)
                batterfound=False
                for eachtype in tempplayerindex["Batting"]:
                    if striker in tempplayerindex["Batting"][eachtype]:
                        batterfound=True
                        self.teamsballresult["Batter Type"].append(eachtype)
                bowlerfound=False
                for eachtype in tempplayerindex["Bowling"]:
                    if bowler in tempplayerindex["Bowling"][eachtype]:
                        bowlerfound=True
                        self.teamsballresult["Bowler Type"].append(eachtype)
                        break
                if batterfound==False:
                    self.teamsballresult["Batter Type"].append(None)
                if bowlerfound==False:
                    self.teamsballresult["Bowler Type"].append(None)


        # Recording Succesfully Chased Score
        if nthinnings == (len(matchinnings) - 1):
            if "result" not in matchinfo["outcome"]:
                if "by" in matchinfo["outcome"] and "wickets" in matchinfo["outcome"]["by"]:
                    if inningsteam in self.result:
                        self.result[inningsteam]["Chased Wins"] += 1
                        self.inningsresult["Chased Score"].append(sum(self.result[matchinfo["outcome"]["winner"]]["inningsruns"]))
                    if inningsteam not in self.result:
                        self.inningsresult["Chased Score"].append(sum(self.result[bowlingteam]["inningsrunsgiven"]))
                    self.inningsresult["Defended Score"].append(None)
                    self.inningsresult["Margin"].append(matchinfo["outcome"]['by']['wickets'])
                if "by" in matchinfo["outcome"] and "runs" in matchinfo["outcome"]["by"]:
                    if bowlingteam in self.result:
                        self.result[bowlingteam]["Defended Wins"] += 1
                        self.inningsresult["Defended Score"].append(sum(self.result[matchinfo["outcome"]["winner"]]["inningsrunsgiven"]) + matchinfo["outcome"]['by']['runs'])
                    if bowlingteam not in self.result:
                        self.inningsresult["Defended Score"].append(sum(self.result[inningsteam]["inningsruns"]) + matchinfo["outcome"]['by']['runs'])
                    self.inningsresult["Chased Score"].append(None)
                    self.inningsresult["Margin"].append(matchinfo["outcome"]['by']['runs'])
                if "by" not in matchinfo["outcome"]:
                    self.inningsresult["Defended Score"].append(None)
                    self.inningsresult["Chased Score"].append(None)
                    self.inningsresult["Margin"].append(None)
            if "result" in matchinfo["outcome"]:
                self.inningsresult["Defended Score"].append(None)
                self.inningsresult["Chased Score"].append(None)
                self.inningsresult["Margin"].append(None)
        if nthinnings != (len(matchinnings) - 1):
            self.inningsresult["Defended Score"].append(None)
            self.inningsresult["Chased Score"].append(None)
            self.inningsresult["Margin"].append(None)

        # print("Inn", len(self.inningsresult["Innings"]))
        # print(nthinnings +1)
        # print("Def", len(self.inningsresult["Defended Score"]))
        # print("Cha", len(self.inningsresult["Chased Score"]))

    # Record team's bowling innings
    def teambowlinginnings(self, eachteam, battingteam, matchtimetuple, nthinnings, matchoutcome, matchinnings, eachmatchtype, matchvenue):

        self.result[eachteam]["dotballseries"].extend(statsprocessor.dotballseries(self.result[eachteam]["inningsrunsgiven"]))
        if self.result[eachteam]["bowlinningscount"] == True:
            self.result[eachteam]["Innings Bowled"] += 1

        self.inningsresult["Bowling Team"].append(eachteam)
        self.inningsresult["Venue"].append(matchvenue)
        self.inningsresult["Date"].append(datetime.date(matchtimetuple[0], matchtimetuple[1], matchtimetuple[2]))
        self.inningsresult["Match Type"].append(eachmatchtype)
        self.inningsresult["Batting Team"].append(battingteam)
        self.inningsresult["Innings"].append(nthinnings + 1)

        self.inningsresult["Score"].append(None)
        self.inningsresult["Outs"].append(None)
        self.inningsresult["Overs"].append(None)
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
        
        # Recording Succesfully Defended Score
        if nthinnings == (len(matchinnings) - 1):
            if "result" not in matchoutcome and matchoutcome["winner"] == eachteam:
                if "by" in matchoutcome and "runs" in matchoutcome["by"]:
                    self.result[eachteam]["Defended Wins"] += 1
                    self.inningsresult["Defended Score"].append(sum(self.result[matchoutcome["winner"]]["inningsrunsgiven"]) + matchoutcome['by']['runs'])
                    self.inningsresult["Chased Score"].append(None)
                    self.inningsresult["Margin"].append(matchoutcome['by']['runs'])
                if "by" not in matchoutcome or "wickets" in matchoutcome["by"]:
                    self.inningsresult["Defended Score"].append(None)
                    self.inningsresult["Chased Score"].append(None)
                    self.inningsresult["Margin"].append(None)
            if "result" in matchoutcome or matchoutcome["winner"] != eachteam:
                self.inningsresult["Defended Score"].append(None)
                self.inningsresult["Chased Score"].append(None)
                self.inningsresult["Margin"].append(None)
        if nthinnings != (len(matchinnings) - 1):
            self.inningsresult["Defended Score"].append(None)
            self.inningsresult["Chased Score"].append(None)
            self.inningsresult["Margin"].append(None)
        
        # print(nthinnings +1)
        # print("Def", len(self.inningsresult["Defended Score"]))
        # print("Cha", len(self.inningsresult["Chased Score"]))

    # Record successful scores
    # Not used right now. Being recording in self.inningsresult
    def successfulscores(self, matchoutcome, matchinnings, nthinnings, inningsteam):
        if "by" in matchoutcome and "runs" in matchoutcome["by"]:
            if "target" in matchinnings[1]:
                self.result[matchoutcome["winner"]]["Defended Score"].append(
                    matchinnings[1]['target']['runs'] - 1)
            if "target" not in matchinnings[1] and nthinnings == (len(matchinnings) - 1) and matchoutcome["winner"] != inningsteam:
                self.result[matchoutcome["winner"]]["Defended Score"].append(
                    (sum(
                        self.result[matchoutcome["winner"]]["inningsrunsgiven"]))
                    + matchoutcome['by']['runs'])
            self.result[matchoutcome["winner"]]["RunMargin"].append(matchoutcome['by']['runs'])
        if "by" in matchoutcome and 'wickets' in matchoutcome['by']:
            if "target" in matchinnings[1]:
                self.result[matchoutcome["winner"]]["Chased Score"].append(
                    matchinnings[1]['target']['runs'])
                self.result[matchoutcome["winner"]]["Overs Chased"].append(
                    round(self.result[matchoutcome["winner"]]["inningsballsfaced"] / 6))
            if "target" not in matchinnings[1] and nthinnings == (len(matchinnings) - 1) and matchoutcome["winner"] == inningsteam:
                self.result[matchoutcome["winner"]]["Chased Score"].append(
                    (sum(self.result[matchoutcome["winner"]]["inningsruns"])))
                self.result[matchoutcome["winner"]]["Overs Chased"].append(
                    round(self.result[matchoutcome["winner"]]["inningsballsfaced"] / 6))
            self.result[matchoutcome["winner"]]["WicketMargin"].append(
                matchoutcome['by']['wickets'])

    # Calculate and record stats derived from basic stats
    def derivedstats(self):
        if self.players or self.allplayers==True:
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
                    self.result[eachplayer]["Mean Balls Faced"] = round(self.inningsresult.loc[self.inningsresult["Players"]==eachplayer, "Balls Faced"].mean(), 2)
                    self.result[eachplayer]["Balls Faced MeanAD"] = round(self.inningsresult.loc[self.inningsresult["Players"]==eachplayer, "Balls Faced"].mad(), 2)

                if len(self.inningsresult.loc[self.inningsresult["Players"]==eachplayer, "Score"].dropna().index) > 0:
                    self.result[eachplayer]["Mean Score"] = round(self.inningsresult.loc[self.inningsresult["Players"]==eachplayer, "Score"].mean(),2)
                    self.result[eachplayer]["Score MeanAD"] = round(self.inningsresult.loc[self.inningsresult["Players"]==eachplayer, "Score"].mad(),2)
                    self.result[eachplayer]["Consistency Factor"] = statsprocessor.ratio(self.result[eachplayer]["Score MeanAD"], self.result[eachplayer]["Mean Score"], multiplier=100)

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

            
        if self.teams or self.allteams==True:
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

                if len(self.inningsresult.loc[self.inningsresult["Batting Team"]==eachteam, "Overs"].dropna().index) > 0:
                    self.result[eachteam]["Run Rate MeanAD"]=round(self.inningsresult.loc[self.inningsresult["Batting Team"]==eachteam, "Run Rate"].mad(), 2)

                if len(self.inningsresult.loc[self.inningsresult["Batting Team"]==eachteam, "Score"].dropna().index) > 0:
                    self.result[eachteam]["Score MeanAD"]=round(self.inningsresult.loc[self.inningsresult["Batting Team"]==eachteam, "Score"].mad(), 2) 
                    self.result[eachteam]["Mean Score"]=round(self.inningsresult.loc[self.inningsresult["Batting Team"]==eachteam, "Score"].mean(), 2)
                    self.result[eachteam]["Consistency Factor"] = statsprocessor.ratio(self.result[eachteam]["Score MeanAD"], self.result[eachteam]["Mean Score"], multiplier=100)

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
                
                if len(self.inningsresult.loc[self.inningsresult["Bowling Team"]==eachteam, "Overs"].dropna().index) > 0:
                    self.result[eachteam]["Runsgiven Rate MeanAD"] = round(self.inningsresult.loc[self.inningsresult["Bowling Team"]==eachteam, "Run Rate"].mad(), 2)

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

            if len(self.inningsresult["Balls Faced"].dropna().index) > 0:
                self.result[eachplayer]["Mean Balls Faced"] = round(self.inningsresult["Balls Faced"].mean(),2)
                self.result[eachplayer]["Balls Faced MeanAD"] = round(self.inningsresult["Balls Faced"].mad(),2)
            if len(self.inningsresult["Balls Faced"].dropna().index) == 0:
                self.result[eachplayer]["Mean Balls Faced"] = 0
                self.result[eachplayer]["Balls Faced MeanAD"] = 0

            if self.result[eachplayer]["firstboundary"]:
                self.result[eachplayer]["Avg First Boundary Ball"] = round(np.mean(self.result[eachplayer]["firstboundary"]))

            if self.result[eachplayer]["totalstosopp"] > 0:
                self.result[eachplayer]["Strike Turnover %"] = statsprocessor.ratio(self.result[eachplayer]["totalstos"], self.result[eachplayer]["totalstosopp"], multiplier=100)

            if len(self.inningsresult["Batting S/R"].dropna().index) > 0:
                self.result[eachplayer]["Batting S/R MeanAD"] = round(self.inningsresult["Batting S/R"].mad(), 2)
            if len(self.inningsresult["Batting S/R"].dropna().index) == 0:
                self.result[eachplayer]["Batting S/R MeanAD"] = 0

            if len(self.inningsresult["Score"].dropna().index) > 0:
                self.result[eachplayer]["Mean Score"] = round(self.inningsresult["Score"].mean(),2)
                self.result[eachplayer]["Score MeanAD"] = round(self.inningsresult["Score"].mad(),2)
                self.result[eachplayer]["Consistency Factor"] = statsprocessor.ratio(self.result[eachplayer]["Score MeanAD"], self.result[eachplayer]["Mean Score"], multiplier=100)
            if len(self.inningsresult["Score"].dropna().index) == 0:
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

            if len(self.inningsresult["Score"].dropna().index) > 0:
                self.result[eachteam]["Score MeanAD"]=round(self.inningsresult["Score"].mad(), 2) 
                self.result[eachteam]["Mean Score"]=round(self.inningsresult["Score"].mean(), 2)
                self.result[eachteam]["Consistency Factor"] = statsprocessor.ratio(self.result[eachteam]["Score MeanAD"], self.result[eachteam]["Mean Score"], multiplier=100)

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
            removestats = ["batinningscount", "inningsruns", "inningsballsfaced", "inningsouts", "firstboundary", "totalstos", "totalstosopp", "totalstosgiven", "totalstosgivenopp", "bowlinningscount", "inningsrunsgiven", "inningsballsbowled", "inningswickets","dotballseries", "inningshowout", "inningsbowlersfaced", "inningspartners", "teaminningsscore", "teaminningsballs", "inningsbattersbowledat", "inningswicketstype", "teaminningsrunsgiven", "teaminningswickets","teaminningsballsbowled"]
            for eachstat in removestats:
                if eachstat in self.result[eachdict]: 
                    self.result[eachdict].pop(eachstat)

    # This is the main function to be applied to search object.
    # I should make picking oppositon bowlers strongs in a list. yes and then just assign json object tfrom that list.
    def stats(self, database, from_date, to_date, matchtype, betweenovers=None, innings=None, sex=None, playersteams=None, teammates=None, oppositionbatters=None, oppositionbowlers = None, oppositionteams=None, venue=None, event=None, matchresult=None, superover=None, battingposition=None, bowlingposition=None, fielders=None, sumstats=False):
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

        currentdir = os.path.dirname(os.path.abspath(__file__))
        playerindexfile = open(f"{currentdir}/playerindex.json")
        players = json.load(playerindexfile)
        if oppositionbatters == None:
            oppositionbatters = []
        if oppositionbatters:
            battingmatchups = []
            for eachname in oppositionbatters:
                for eachgroup in players["Batting"]:
                    if eachname == eachgroup:
                        battingmatchups.extend(players["Batting"][eachgroup])
                    if eachname != eachgroup:
                        battingmatchups.append(eachname)
        if oppositionbowlers == None:
            oppositionbowlers = []
        if oppositionbowlers:
            bowlingmatchups = []
            for eachname in oppositionbowlers:
                for eachgroup in players["Bowling"]:
                    if eachname == eachgroup:
                        bowlingmatchups.extend(players["Bowling"][eachgroup])
                    if eachname != eachgroup:
                        bowlingmatchups.append(eachname)

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
        self.result = {}
        search.playersballresultsetup(self)
        search.teamsballresultsetup(self)
        if self.allplayers==True:
            search.playerinningsresultsetup(self)
        if self.players:
            search.playerinningsresultsetup(self)
            for eachplayer in self.players:
                search.addplayerstoresult(self, eachplayer)
        if self.allteams==True:
            search.teaminningsresultsetup(self)
        if self.teams:
            search.teaminningsresultsetup(self)
            for eachteam in self.teams:
                search.addteamstoresult(self, eachteam)

        # Ingest zipfile of data
        matches = zipfile.ZipFile(database, 'r')

        # create an index file for eachfile
        search.fileindexing(self, database, matches)

        start = time.time()
        
        # Setup tally of games and results for "all teams" stats.
        allgamesplayed = 0
        allgameswinloss = 0
        allgamesdrawn = 0
        
        currentdir = os.path.dirname(os.path.abspath(__file__))
        matchindexfile = open(f"{currentdir}/matchindex.json")
        matchindex = json.load(matchindexfile)
        # Open each file by searched for matchtype in index
        for eachmatchtype in matchtype:
            for eachyear in matchindex["matches"][eachmatchtype]:
                if int(eachyear) < from_date[0] or int(eachyear) > to_date[0]:
                    continue
                for eachfile in matchindex["matches"][eachmatchtype][eachyear]:
                    # print(eachfile)
                    matchdata = matches.open(eachfile)
                    match = json.load(matchdata)

                    
                    tempplayerindex={"Batting":{"Right hand":[],"Left hand":[]},"Bowling":{"Right arm pace":[],"Left arm pace":[],"Right arm Off break":[],"Right arm Leg break":[],"Left arm orthodox":[],"Left arm wrist spin":[]},"Unknown":[]}
                    for eachplayer in match['info']['registry']['people'].keys():
                        bowlerfound=False
                        for eachtype in players["Batting"]:
                            if eachplayer in players["Batting"][eachtype]:
                                tempplayerindex["Batting"][eachtype].append(eachplayer)
                        for eachtype in players["Bowling"]:
                            if eachplayer in players["Bowling"][eachtype]:
                                bowlerfound=True
                                tempplayerindex["Bowling"][eachtype].append(eachplayer)
                        if eachplayer in players["Unknown"] or bowlerfound==False:
                            tempplayerindex["Unknown"].append(eachplayer)

                    # Dates check
                    year = str(match["info"]["dates"][0][:4])
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

                    # All Players and All Teams games/wins/draw/ties record
                    # TODO rewrite for ties and add these to stats dict. Hard because T20s have superovers to decide ties.
                    # TODO move this inside games and wins. and move games and wins down after innings finished.
                    if sumstats==True:
                        allgamesplayed += 1
                        if "result" in match["info"]["outcome"] and match["info"]["outcome"]['result'] == "draw":
                            allgamesdrawn += 1
                        if "winner" in match["info"]["outcome"]:
                            allgameswinloss += 1

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
                        
                        # PROBLEM this is getting created before the first match where allplayers scoers is create.
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

                                # Record batting lineup.
                                if eachball['batter'] not in battingorder:
                                    battingorder.append(eachball['batter'])
                                if eachball['non_striker'] not in battingorder:
                                    battingorder.append(eachball['non_striker'])

                                # Record bowling order.
                                if eachball['bowler'] not in bowlingorder:
                                    bowlingorder.append(eachball['bowler'])

                                # Add players for allplayers search
                                if self.allplayers==True:
                                    for eachplayer in [eachball["batter"],eachball["non_striker"], eachball["bowler"]]:
                                        if eachplayer not in self.result:
                                            search.addplayerstoresult(self, eachplayer)
                                    if "wickets" in eachball:
                                        for eachwicket in eachball["wickets"]:
                                            if "fielders" in eachwicket:
                                                for eachfielder in eachwicket["fielders"]:
                                                    if "name" not in eachfielder:
                                                        continue
                                                    search.addplayerstoresult(self, eachfielder["name"])

                                # Add teams for allteams search
                                if self.allteams==True:
                                    for eachteam in match["info"]["teams"]:
                                        if eachteam not in self.result:
                                            search.addteamstoresult(self, eachteam)

                                # Player stats
                                if self.players or self.allplayers==True:
                                    
                                    # Striker's stats
                                    if eachball['batter'] in self.result and (not oppositionbowlers or eachball['bowler'] in bowlingmatchups) and (not battingposition or (battingposition and ((battingorder.index(eachball['batter']) + 1) in battingposition))):
                                        search.strikerstats(self, eachball, nthball, eachover)
    
                                    # Non-striker's outs.
                                    if eachball["non_striker"] in self.result and "wickets" in eachball and (not battingposition or (battingposition and ((battingorder.index(eachball['non_striker']) + 1) in battingposition))):
                                        search.nonstrikerstats(self, eachball, oppositionbowlers)

                                    # Bowling stats
                                    if eachball['bowler'] in self.result and (not oppositionbatters or eachball['batter'] in battingmatchups) and (not bowlingposition or (bowlingposition and ((bowlingorder.index(eachball['bowler']) + 1) in bowlingposition))):
                                        search.bowlerstats(self, eachball, fielders, nthball, eachover)

                                    # Fielding stats
                                    if "wickets" in eachball:
                                        search.fieldingstats(self, eachball)

                                # Team stats
                                if self.teams or self.allteams==True:

                                    # Team Batting stats
                                    if eachinnings["team"] in self.result:
                                        search.teambattingstats(self, eachball, eachinnings["team"], nthball, eachover, battingorder,tempplayerindex)

                                    # Team Bowling stats
                                    for eachteam in match["info"]["teams"]:
                                        if eachteam in self.result and eachteam not in eachinnings["team"]:
                                            search.teambowlingstats(self, eachball, eachteam, nthball, eachover, battingorder,tempplayerindex)

                                # search.ballstats(self, matchtimetuple, match["info"], nthinnings, eachinnings, eachball, nthball, eachover, battingorder, bowlingorder)

                        # Player innings scores.
                        if self.players or self.allplayers==True:
                            search.playerinnings(self,matchtimetuple, match["info"], nthinnings, eachmatchtype, battingorder, bowlingorder)
                        
                        # Team innings scores
                        if self.teams or self.allteams==True:

                            # Team innings score
                            # if eachinnings["team"] in self.result:
                            search.teaminnings(self, eachinnings["team"], nthinnings, match["info"], matchtimetuple, match['innings'],tempplayerindex)
                                
                            # Bowling innings figures
                            # for eachteam in match["info"]["teams"]:
                            #     if eachteam in self.result and eachteam not in eachinnings["team"]:
                            #         search.teambowlinginnings(self, eachteam, eachinnings["team"], matchtimetuple, nthinnings, match['info']['outcome'], match['innings'], eachmatchtype, match["info"]["venue"])
                                    
                            # Successfully defended and Chased Score.
                            # if 'result' not in match['info']['outcome'] and match['info']['outcome']["winner"] in self.teams:
                                # search.successfulscores(self,match['info']['outcome'],match['innings'],nthinnings, eachinnings["team"])

                    # Individual team and players games/wins/draw/ties record
                    search.gamesandwins(self, match["info"])

                    matchdata.close()
        matches.close()
        matchindexfile.close()
        playerindexfile.close()
        print(f'Time after stats(): {time.time() - start}')
        

        # for y in self.teamsballresult.keys():
        #      print(y, len(self.teamsballresult[y]))
        # print(self.ballresult)

        if self.players or self.allplayers==True:
            self.ballresult = pd.DataFrame(self.playersballresult)

        if self.teams or self.allteams==True:
            self.ballresult = pd.DataFrame(self.teamsballresult)

        print(f'Time after self.ballresult creation: {time.time() - start}')
        self.inningsresult = pd.DataFrame(self.inningsresult)

        print(f'Time after self.inningsresult creation: {time.time() - start}')
        # Derived Stats
        search.derivedstats(self)

        print(f'Time after derivedstats(): {time.time() - start}')
        # All Player and All Teams Summing function
        if sumstats:
            search.sumstats(self,allgamesplayed, allgameswinloss, allgamesdrawn)

        search.cleanup(self)

        print(f'Time after sumstats(): {time.time() - start}')
        # if self.players or self.teams:
        df = pd.DataFrame(self.result)
        self.result = df.transpose()
        print(f'Time after transpose(): {time.time() - start}')