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

import datetime
import json
import time
import pandas as pd
import os
import zipfile
import numpy as np
import math
from cricketstats import statsprocessor

# TODO make option to sum players/teams stats better. Insert "all players earlier in result"?
# TODO fix the way innings outs are counted. eg. make it more efficient, there's currently 3 lists for it...
# TODO when do allteams/allplayers I should add all players/teams at beginning of match not check at each ball. this counts less for palyers for some reasons
# TODO show stats by season in IPL, battign avg by year

# TODO Redo match tally so it is common tally that can be reference in ball data and innings data. This ouwld make things much easier.
# TODO playerballresult:  wickets left, balls left 
# TODO simplify player innings and then test.
# TODO change innings team to batting and bowling team
# TODO need to do "above average" dervied stats on ball, innings and career. This is easy if I create anew record for "average player", I can then use that to fill in the "above average" fields for career, for  and leave "all players" as a sum/average combo record
# for innings its easy just tak difference to mean
# for ball I need to loop through ball numbers
# have to make derived stats more efficient without looping through all players in self.result. has to be done once

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
        self.matchtally = None
        self.playermatchtally = None

    # Setup Player statistics to be recorded.

    # Player aggregate results
    def addplayerstoresult(self, eachplayer,playerindex):
        self.result[eachplayer] = {"Players": eachplayer, "Batting":None,"Bowling":None, "Games": 0, "Won": 0, "Drawn": 0, 'Win %': 0,

                                    "Innings Batted": 0,
                                    "Runs": 0, "Singles":0, "Fours": 0, "Sixes": 0, "Dot Balls": 0, "Balls Faced": 0, "Outs": 0, 
                                    "Bowled Outs": 0, "LBW Outs": 0, "Hitwicket Outs": 0, "Caught Outs": 0, "Stumped Outs": 0, "Run Outs": 0, "Caught and Bowled Outs": 0, 
                                    "totalstos": 0, "totalstosopp": 0, 
                                    'Dot Ball %': 0, 'Strike Turnover %': 0, 'Batting S/R': 0, 'Batting S/R MeanAD': 0, 'Batting Avg': 0, "Mean Score":0, 'Score MeanAD': 0, "Scoring Consistency":0, 'Boundary %': 0, "Runs/Ball":0,
                                    "Mean Balls Faced":0, "Balls Faced MeanAD":0, "Survival Consistency":0,
                                    "firstboundary": [], 'Avg First Boundary Ball': 0, "Dismissal Rate":0, "Boundary Rate":0,
                                    
                                    "Innings Bowled":0,
                                    "Runsgiven": 0, "Singlesgiven":0, "Foursgiven": 0, "Sixesgiven": 0, 
                                    "Wickets": 0, "Balls Bowled": 0, "Extras": 0, "No Balls": 0, "Wides":0,
                                    "Dot Balls Bowled": 0, 
                                    "Bowleds": 0, "LBWs": 0, "Hitwickets": 0, "Caughts": 0, "Stumpeds": 0, "Caught and Bowleds": 0,
                                    "totalstosgiven": 0, "totalstosgivenopp": 0, 
                                    "Catches": 0, "Runouts": 0, "Stumpings": 0, 
                                    'Economy Rate': 0, 'Economy Rate MeanAD': 0, 'Dot Ball Bowled %': 0,'Boundary Given %': 0, 'Bowling Avg': 0, "Bowling Avg MeanAD": 0, 'Bowling S/R': 0, "Bowling S/R MeanAD": 0,  "Runsgiven/Ball":0, "Boundary Given Rate":0,
                                    "dotballseries": [], "Avg Consecutive Dot Balls": 0,
                                    }
        if eachplayer in playerindex.keys():
            self.result[eachplayer]["Batting"]=playerindex[eachplayer]["Batting"]
            self.result[eachplayer]["Bowling"]=playerindex[eachplayer]["Bowling"]

    
    # Player innings results
    def playerinningsresultsetup(self):
        self.inningsresult = { 
        "Date":[], "Year":[], "Month":[], "Match Type":[], "Venue":[], "Event":[],"Match Winner":[],  "Player":[], "Team":[], "Opposition":[], "Innings":[], "Innings Type":[],"Target":[],"Chase":[],"Defence":[],'% Target Achieved':[],"Runs Required":[], "Run Rate Required":[],
        "Fielder":[],

        "Batter Type":[], "Batting Position":[], "Score": [], "Balls Faced": [],  "How Out": [], "First Boundary Ball":[], "Batting S/R":[], "Runs/Ball":[], "Boundary %":[],"Boundary Rate":[],

        "Bowler Type":[], "Bowling Position":[], "Runsgiven": [], "Wickets": [], "Overs Bowled": [], "Balls Bowled":[],
        'Economy Rate': [], 'Bowling Avg': [], "Avg Consecutive Dot Balls":[], "Bowling S/R":[],"Runsgiven/Ball":[],
        }

    # Player ball results
    def playersballresultsetup(self):
        self.playersballresult = { 
        "Date":[], "Year":[], "Month":[], "Match Type":[], "Venue":[], "Event":[], "Match Winner":[], "Batting Team":[], "Bowling Team":[], "Innings":[],"Innings Type":[], #"Phase": [],
        "Ball":[], "Innings Ball":[], "Innings Outs":[], "Innings Runs":[], "Target":[],"Chase":[],"Defence":[],"% Target Achieved":[],"Runs Required":[],"Run Rate Required":[],
        "Runs":[], "Batter Score":[], "Extras":[],"Noballs":[], "Wides":[],"Byes":[], "Legbyes":[], "How Out":[],"Fielder":[], "Out/NotOut":[], "Runs/Ball":[], "Bowler Extras":[], "Fielding Extras":[],

        "Batter":[], "Batting Position":[], "Batter Type":[], "Non_striker": [], "Balls Faced":[],
        "Strike Rate": [], "S/R Zone":[], "Boundary %":[],"Boundary Rate":[],"Current Score":[], "Final Score":[],
        
        "Bowler": [],"Bowler Type":[], "Bowling Position":[], "Balls Bowled":[],
        "Current Wickets": [], "Final Wickets":[], "Current Runsgiven": [], "Final Runsgiven":[]
        }

    # Setup teams statistics to be recorded
    # Team aggregate results
    def addteamstoresult(self, eachteam):
        self.result[eachteam] = {"Teams": eachteam, "Games": 0, "Innings Bowled":0, "Innings Batted": 0,
                                "Won": 0, "Drawn": 0, 'Win %': 0, "Defended Wins": 0, "Chased Wins": 0, 
                                "Net Boundary %":0, "Net Run Rate":0,
                                
                                "Runs": 0, "Singles":0,"Twos":0, "Fours": 0, "Sixes": 0, "Dot Balls": 0, "Outs": 0, "Balls Faced": 0, 
                                "Bowled Outs": 0, "LBW Outs": 0, "Caught Outs": 0, "Stumped Outs": 0, "Run Outs": 0, "Caught and Bowled Outs": 0,
                                "Runs/Wicket":0, "Runs/Ball":0, "Run Rate":0, 'Avg First Boundary Ball': 0,
                                'Dot Ball %': 0, 'Score MeanAD': 0, "Scoring Consistency":0, 'Boundary %': 0, 

                                "Runsgiven":0, "Singlesgiven":0,"Foursgiven": 0, "Sixesgiven": 0, 
                                "Wickets": 0, "Balls Bowled": 0, "Extras": 0, "No Balls": 0, "Wides":0, "Byes": 0, "Leg Byes": 0, "Dot Balls Bowled": 0, 
                                "Bowleds": 0, "LBWs": 0, "Hitwickets": 0,  "Caughts": 0, "Runouts": 0, "Stumpeds": 0, "Caught and Bowleds": 0,
                                'Dot Ball Bowled %': 0,'Boundary Given %': 0,'Runsgiven/Wicket': 0, "Runsgiven/Ball":0, "Runsgiven Rate": 0,
                                "Avg Consecutive Dot Balls": 0, "dotballseries": [],
                                }

    # Team innings results
    def teaminningsresultsetup(self):
        self.inningsresult = {
        "Date":[],"Year":[], "Month":[], "Match Type":[],"Venue":[], "Event":[], "Match Winner":[], "Toss Winner":[],"Toss Decision":[], "Batting Team":[], "Bowling Team":[], "Innings":[], 
        "Defence":[], "Defended Score": [],"Chase":[], "Chased Score": [], "Margin":[], "Declared":[],
        "Score": [], "Outs": [], "Overs": [], "Extras": [],
        "Runs/Wicket":[], "Runs/Ball":[], "Run Rate":[], "First Boundary Ball":[], "Boundary %":[], "Net Boundary %":[], "TwosThrees %": [],
        "Avg Consecutive Dot Balls":[]
        }

    # Team ball results
    def teamsballresultsetup(self):
        self.teamsballresult = { 
        "Date":[],"Year":[], "Month":[], "Match Type":[], "Venue":[], "Event":[], "Match Winner":[],"Toss Winner":[],"Toss Decision":[], "Batting Team":[], "Bowling Team":[], "Innings":[], "Defence":[], "Chase":[], "Target":[], "% Target Achieved":[], "Runs Required":[], "Run Rate Required":[],
        "Innings Ball":[], "Innings Over":[], "Ball":[], "Ball in Over":[], "Nth Ball in Over":[], "Phase":[],
        "Current Score":[], "Current Outs":[], "Final Score":[], "Final Outs":[],"Final Overs":[],
        "Batter":[], "Batting Position":[],"Batter Type":[], "Non_striker": [], 
        "Runs Scored": [], "Batter Score":[], "Runs/Ball": [],
        "Bowler": [], "Bowler Type":[], "Extras":[], "Extras Type": [], "How Out": [], "Fielder":[], "Out/NotOut":[],
        }

    def teammatchtallysetup(self,matchinfo, matchinnings):
        for nthinnings, eachinnings in enumerate(matchinnings):
            if "super_over" in eachinnings:
                continue
            for eachteam in matchinfo["teams"]:
                if eachteam != eachinnings["team"]:
                    bowlingteam = eachteam
            self.matchtally[nthinnings] = {"batting team": eachinnings["team"], "bowling team":bowlingteam,
            "inningsruns": [], "inningsbatterscore":[], "inningssingles":[],"inningstwosthrees":[],"inningsfours":[],"inningssixes":[],"inningsdotballs":[], 
            "inningsouts": [],"inningsballsseries":[], "inningsballs": [], "inningsballinover":[],"inningsnthballinover":[], "inningsoutsbyball": [], "inningshowout":[],"inningswides":[], "inningsnoballs":[], "inningsbyes":[],"inningslegbyes":[],
            "inningsstrikers": [],"inningsnonstrikers": [],"inningsbowlers": [],"inningsstrikersbattingpos":[], "inningsextras":[],"inningsextrastype":[], "inningsfielder":[], "inningsdeclared":False}

    def playermatchtallysetup(self,matchinfo, matchinnings):
        for nthinnings, eachinnings in enumerate(matchinnings):
            if "super_over" in eachinnings:
                continue
            self.playermatchtally[nthinnings]={}
            for eachteam in matchinfo["players"]:
                for eachplayer in matchinfo["players"][eachteam]:
                    self.playermatchtally[nthinnings][eachplayer]= {
                        "teaminningsscore":[], "teaminningsouts":[], "teaminningsballs":[], "inningsballs":[], 
                        "batinningscount": False, "bowlinningscount": False, 

                        "inningsruns": [], "inningsbatterscore":[],"inningsextras":[], "inningsnoballs":[],"inningswides":[],"inningsbyes":[],"inningslegbyes":[],"inningsnonstriker":[], "inningshowout": [], "inningsfielder":[],

                        "inningsballsfaced": 0, "inningsbowlersfaced":[], 
                        
                        "inningsballsbowled": 0, "inningswickets": [], "inningsbattersbowledat":[],
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
    def gamesandwins(self, matchinfo,matchinnings,innings):
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
                if innings and not any(True for eachinnings in innings if matchinnings[(eachinnings-1)]["team"] == eachteam):
                    continue
                self.result[eachteam]["Games"] += 1
                if "result" in matchinfo["outcome"] and matchinfo["outcome"]['result'] == "draw":
                    self.result[eachteam]["Drawn"] += 1
                if "winner" in matchinfo["outcome"] and eachteam in matchinfo["outcome"]["winner"]:
                    self.result[matchinfo["outcome"]
                                ["winner"]]["Won"] += 1


    # Record innings tally
    def teaminningstally(self,nthball,eachball,legdel,eachover, battingorder, nthinnings):
        # record innings tally
        over=eachover["over"]
        self.matchtally[nthinnings]["batinningscount"] = True
        self.matchtally[nthinnings]["inningsstrikers"].append(eachball["batter"])
        self.matchtally[nthinnings]["inningsnonstrikers"].append(eachball["non_striker"])
        self.matchtally[nthinnings]["inningsstrikersbattingpos"].append(battingorder.index(eachball["batter"]) + 1)
        self.matchtally[nthinnings]["inningsbowlers"].append(eachball["bowler"])
        
        self.matchtally[nthinnings]["inningsballs"].append(float(f"{over}.{legdel}"))
        self.matchtally[nthinnings]["inningsballsseries"].append((over * 6) + legdel)
        self.matchtally[nthinnings]["inningsballinover"].append(legdel)
        self.matchtally[nthinnings]["inningsnthballinover"].append(nthball+1)

        self.matchtally[nthinnings]["inningsruns"].append(eachball['runs']['total'])
        self.matchtally[nthinnings]["inningsbatterscore"].append(eachball['runs']['batter'])
        self.matchtally[nthinnings]["inningsextras"].append(eachball['runs']['extras'])
        if eachball['runs']['batter'] == 1:
            self.matchtally[nthinnings]["inningssingles"].append(eachball['runs']['batter'])
        if eachball['runs']['batter'] == 2 or eachball['runs']['batter'] == 3:
            self.matchtally[nthinnings]["inningstwosthrees"].append(eachball['runs']['batter'])
        if eachball['runs']['batter'] == 4:
            self.matchtally[nthinnings]["inningsfours"].append(eachball['runs']['batter'])
        if eachball['runs']['batter'] == 6:
            self.matchtally[nthinnings]["inningssixes"].append(eachball['runs']['batter'])
        if eachball['runs']['total'] == 0:
            self.matchtally[nthinnings]["inningsdotballs"].append(eachball['runs']['total'])

        if "extras" not in eachball:
            self.matchtally[nthinnings]["inningswides"].append(None)
            self.matchtally[nthinnings]["inningsnoballs"].append(None)
            self.matchtally[nthinnings]["inningsbyes"].append(None)
            self.matchtally[nthinnings]["inningslegbyes"].append(None)
        if "extras" in eachball:
            if "wides" in eachball["extras"]:
                self.matchtally[nthinnings]["inningswides"].append(eachball['extras']["wides"])
            if "noballs" in eachball['extras']:
                self.matchtally[nthinnings]["inningsnoballs"].append(eachball['extras']["noballs"])
            if "byes" in eachball['extras']:
                self.matchtally[nthinnings]["inningsbyes"].append(eachball['extras']["byes"])
            if "legbyes" in eachball['extras']:
                self.matchtally[nthinnings]["inningslegbyes"].append(eachball['extras']["legbyes"])


        if "wickets" in eachball:
            self.matchtally[nthinnings]["inningsoutsbyball"].append((len(battingorder)-1))
            for eachwicket in eachball["wickets"]:
                self.matchtally[nthinnings]["inningshowout"].append(eachwicket["kind"])
                self.matchtally[nthinnings]["inningsouts"].append(1)
                if eachwicket["kind"] == "bowled":
                    self.matchtally[nthinnings]["inningsfielder"].append(None)
                if eachwicket["kind"] == "lbw":
                    self.matchtally[nthinnings]["inningsfielder"].append(None)
                if eachwicket["kind"] == "hit wicket":
                    self.matchtally[nthinnings]["inningsfielder"].append(None)
                if eachwicket["kind"] == "caught":
                    if "fielders" in eachwicket:
                        if "name" in eachwicket["fielders"][0]:
                            self.matchtally[nthinnings]["inningsfielder"].append(eachwicket["fielders"][0]["name"])
                        if "name" not in eachwicket["fielders"][0]:
                            self.matchtally[nthinnings]["inningsfielder"].append(None)
                if eachwicket["kind"] == "stumped":
                    if "fielders" in eachwicket:
                        if "name" in eachwicket["fielders"][0]:
                            self.matchtally[nthinnings]["inningsfielder"].append(eachwicket["fielders"][0]["name"])
                        if "name" not in eachwicket["fielders"][0]:
                            self.matchtally[nthinnings]["inningsfielder"].append(None)
                if eachwicket["kind"] == "run out":
                    if "fielders" in eachwicket:
                        if "name" in eachwicket["fielders"][0]:
                            self.matchtally[nthinnings]["inningsfielder"].append(eachwicket["fielders"][0]["name"])
                        if "name" not in eachwicket["fielders"][0]:
                            self.matchtally[nthinnings]["inningsfielder"].append(None)
                if eachwicket["kind"] == "caught and bowled":
                    self.matchtally[nthinnings]["inningsfielder"].append(None)
        if "wickets" not in eachball:
            self.matchtally[nthinnings]["inningsoutsbyball"].append((len(battingorder)-2))
            self.matchtally[nthinnings]["inningshowout"].append(None)
            self.matchtally[nthinnings]["inningsouts"].append(0)
            self.matchtally[nthinnings]["inningsfielder"].append(None)

    # Record striker's stats for each ball.
    def strikerstats(self, eachball, nthball, eachover,battingorder,legdel,nthinnings):
        self.playermatchtally[nthinnings][eachball['batter']]["batinningscount"] = True
        self.playermatchtally[nthinnings][eachball['batter']]["inningsruns"].append(eachball['runs']['total'])
        self.playermatchtally[nthinnings][eachball['batter']]["inningsbatterscore"].append(eachball['runs']['batter'])
        self.playermatchtally[nthinnings][eachball['batter']]["inningsbowlersfaced"].append(eachball['bowler'])
        over=eachover["over"]
        self.playermatchtally[nthinnings][eachball['batter']]["teaminningsballs"].append(float(f"{over}.{legdel}"))
        self.playermatchtally[nthinnings][eachball['batter']]["inningsballs"].append((over * 6) + legdel)
        self.playermatchtally[nthinnings][eachball['batter']]["teaminningsscore"].append(sum(self.matchtally[nthinnings]["inningsruns"]))
        self.playermatchtally[nthinnings][eachball['batter']]["inningsnonstriker"].append(eachball["non_striker"])
        

        self.result[eachball['batter']]["Runs"] += eachball['runs']['batter']
        if eachball['runs']['batter'] == 1:
            self.result[eachball['batter']
                        ]["Singles"] += 1
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
            self.result[eachball['batter']]["Balls Faced"] += 1
            self.playermatchtally[nthinnings][eachball['batter']]["inningsballsfaced"] += 1
            self.playermatchtally[nthinnings][eachball['batter']]["inningsextras"].append(0)
            self.playermatchtally[nthinnings][eachball['batter']]["inningswides"].append(0)
            self.playermatchtally[nthinnings][eachball['batter']]["inningsnoballs"].append(0)
            self.playermatchtally[nthinnings][eachball['batter']]["inningsbyes"].append(0)
            self.playermatchtally[nthinnings][eachball['batter']]["inningslegbyes"].append(0)
        if "extras" in eachball:
            self.playermatchtally[nthinnings][eachball['batter']]["inningsextras"].append(eachball["runs"]["extras"])

            if "wides" in eachball['extras']:
                self.playermatchtally[nthinnings][eachball['batter']]["inningswides"].append(eachball['extras']["wides"])
            if "wides" not in eachball['extras']:
                self.result[eachball['batter']]["Balls Faced"] += 1
                self.playermatchtally[nthinnings][eachball['batter']]["inningsballsfaced"] += 1
                self.playermatchtally[nthinnings][eachball['batter']]["inningswides"].append(0)
                
            if "noballs" in eachball['extras']:
                self.playermatchtally[nthinnings][eachball['batter']]["inningsnoballs"].append(eachball['extras']["noballs"])
            if "noballs" not in eachball['extras']:
                self.playermatchtally[nthinnings][eachball['batter']]["inningsnoballs"].append(0)

            if "byes" in eachball['extras']:
                self.playermatchtally[nthinnings][eachball['batter']]["inningsbyes"].append(eachball['extras']["byes"])
            if "byes" not in eachball['extras']:
                self.playermatchtally[nthinnings][eachball['batter']]["inningsbyes"].append(0)
                

            if "legbyes" in eachball['extras']:
                self.playermatchtally[nthinnings][eachball['batter']]["inningslegbyes"].append(eachball['extras']["legbyes"])
            if "legbyes" not in eachball['extras']:
                self.playermatchtally[nthinnings][eachball['batter']]["inningslegbyes"].append(0)
                


        if "wickets" in eachball:
            self.playermatchtally[nthinnings][eachball['batter']]["teaminningsouts"].append((len(battingorder)-1))
            for eachwicket in eachball["wickets"]:
                if eachball['batter'] == eachwicket["player_out"]:
                    self.result[eachball['batter']
                                ]["Outs"] += 1
                    self.playermatchtally[nthinnings][eachball['batter']]["inningshowout"].append(eachwicket["kind"])
                    if eachwicket["kind"] == "bowled":
                        self.result[eachball['batter']
                                    ]["Bowled Outs"] += 1
                        self.playermatchtally[nthinnings][eachball['batter']]["inningsfielder"].append(None)
                    if eachwicket["kind"] == "lbw":
                        self.result[eachball['batter']
                                    ]["LBW Outs"] += 1
                        self.playermatchtally[nthinnings][eachball['batter']]["inningsfielder"].append(None)
                    if eachwicket["kind"] == "hit wicket":
                        self.result[eachball['batter']
                                    ]["Hitwicket Outs"] += 1
                        self.playermatchtally[nthinnings][eachball['batter']]["inningsfielder"].append(None)
                    if eachwicket["kind"] == "caught":
                        self.result[eachball['batter']
                                    ]["Caught Outs"] += 1
                        if "fielders" in eachwicket:
                            if "name" in eachwicket["fielders"][0]:
                                self.playermatchtally[nthinnings][eachball['batter']]["inningsfielder"].append(eachwicket["fielders"][0]["name"])
                            if "name" not in eachwicket["fielders"][0]:
                                self.playermatchtally[nthinnings][eachball['batter']]["inningsfielder"].append(None)
                    if eachwicket["kind"] == "stumped":
                        self.result[eachball['batter']
                                    ]["Stumped Outs"] += 1
                        if "fielders" in eachwicket:
                            if "name" in eachwicket["fielders"][0]:
                                self.playermatchtally[nthinnings][eachball['batter']]["inningsfielder"].append(eachwicket["fielders"][0]["name"])
                            if "name" not in eachwicket["fielders"][0]:
                                self.playermatchtally[nthinnings][eachball['batter']]["inningsfielder"].append(None)
                    if eachwicket["kind"] == "run out":
                        self.result[eachball['batter']
                                    ]["Run Outs"] += 1
                        if "fielders" in eachwicket:
                            if "name" in eachwicket["fielders"][0]:
                                self.playermatchtally[nthinnings][eachball['batter']]["inningsfielder"].append(eachwicket["fielders"][0]["name"])
                            if "name" not in eachwicket["fielders"][0]:
                                self.playermatchtally[nthinnings][eachball['batter']]["inningsfielder"].append(None)
                    if eachwicket["kind"] == "caught and bowled":
                        self.result[eachball['batter']
                                    ]["Caught and Bowled Outs"] += 1
                        self.playermatchtally[nthinnings][eachball['batter']]["inningsfielder"].append(None)
        if "wickets" not in eachball:
            self.playermatchtally[nthinnings][eachball['batter']]["inningshowout"].append(None)
            self.playermatchtally[nthinnings][eachball['batter']]["teaminningsouts"].append((len(battingorder)-2))
            self.playermatchtally[nthinnings][eachball['batter']]["inningsfielder"].append(None)
        if (nthball+1) < len(eachover["deliveries"]):
            search.striketurnoverstats(self, eachball, 1, 3)
        if (nthball+1) == len(eachover["deliveries"]):
            search.striketurnoverstats(self, eachball, 0, 2)

    # Record non-strikers's stats for each ball. 
    def nonstrikerstats(self, eachball, oppositionbowlers,nthinnings):
        self.playermatchtally[nthinnings][eachball['batter']]["batinningscount"] = True
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
    def bowlerstats(self, eachball, fielders, nthball, eachover,battingorder,legdel,nthinnings):
        self.playermatchtally[nthinnings][eachball['bowler']]["bowlinningscount"] = True
        over=eachover["over"]
        self.playermatchtally[nthinnings][eachball['bowler']]["teaminningsballs"].append(float(f"{over}.{legdel}"))
        self.playermatchtally[nthinnings][eachball['bowler']]["inningsballs"].append((over * 6) + legdel)
        self.playermatchtally[nthinnings][eachball['bowler']]["teaminningsscore"].append(sum(self.matchtally[nthinnings]["inningsruns"]))
        self.playermatchtally[nthinnings][eachball['bowler']]["inningsbattersbowledat"].append(eachball["batter"])

        self.playermatchtally[nthinnings][eachball['bowler']]["inningsbatterscore"].append(eachball['runs']['batter'])
        self.playermatchtally[nthinnings][eachball['bowler']]["inningsnonstriker"].append(eachball["non_striker"])
        

        self.result[eachball['bowler']]["Runsgiven"] += eachball['runs']['batter']
        if eachball['runs']['batter'] == 1:
            self.result[eachball['bowler']
                        ]["Singlesgiven"] += 1
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
            self.result[eachball['bowler']]["Balls Bowled"] += 1

            self.playermatchtally[nthinnings][eachball['bowler']]["inningsruns"].append(eachball['runs']['total'])
            self.playermatchtally[nthinnings][eachball['bowler']]["inningsballsbowled"] += 1
            self.playermatchtally[nthinnings][eachball['bowler']]["inningsextras"].append(0)
            self.playermatchtally[nthinnings][eachball['bowler']]["inningswides"].append(0)
            self.playermatchtally[nthinnings][eachball['bowler']]["inningsnoballs"].append(0)
            self.playermatchtally[nthinnings][eachball['bowler']]["inningsbyes"].append(0)
            self.playermatchtally[nthinnings][eachball['bowler']]["inningslegbyes"].append(0)


        if "extras" in eachball:
            self.playermatchtally[nthinnings][eachball['bowler']]["inningsextras"].append(eachball["runs"]["extras"])

            if "wides" not in eachball['extras'] and "noballs" not in eachball['extras']:
                self.result[eachball['bowler']]["Balls Bowled"] += 1
                self.playermatchtally[nthinnings][eachball['bowler']]["inningsballsbowled"] += 1
                self.playermatchtally[nthinnings][eachball['bowler']]["inningsruns"].append((eachball['runs']['batter']))
                
            
            if "byes" in eachball['extras']:
                self.playermatchtally[nthinnings][eachball['bowler']]["inningsbyes"].append(eachball['extras']["byes"])
            if "byes" not in eachball['extras']:
                self.playermatchtally[nthinnings][eachball['bowler']]["inningsbyes"].append(0)
            
            if "legbyes" in eachball['extras']:
                self.playermatchtally[nthinnings][eachball['bowler']]["inningslegbyes"].append(eachball['extras']["legbyes"])
            if "legbyes" not in eachball['extras']:
                self.playermatchtally[nthinnings][eachball['bowler']]["inningslegbyes"].append(0)
            
            if "wides" in eachball['extras']:
                self.result[eachball['bowler']]["Runsgiven"] += eachball['extras']['wides']
                self.result[eachball['bowler']]["Wides"] += eachball['extras']['wides']
                self.result[eachball['bowler']]["Extras"] += eachball['extras']['wides']
                self.playermatchtally[nthinnings][eachball['bowler']]["inningsruns"].append((eachball['runs']['batter'] + eachball['extras']['wides']))
                self.playermatchtally[nthinnings][eachball['bowler']]["inningswides"].append((eachball['extras']['wides']))
            if "wides" not in eachball['extras']:
                self.playermatchtally[nthinnings][eachball['bowler']]["inningswides"].append(0)
            
            if "noballs" in eachball['extras']:
                self.result[eachball['bowler']]["Runsgiven"] += eachball['extras']['noballs']
                self.result[eachball['bowler']]["No Balls"] += eachball['extras']['noballs']
                self.result[eachball['bowler']]["Extras"] += eachball['extras']['noballs']
                self.playermatchtally[nthinnings][eachball['bowler']]["inningsruns"].append((eachball['runs']['batter'] + eachball['extras']['noballs']))
                self.playermatchtally[nthinnings][eachball['bowler']]["inningsnoballs"].append((eachball['extras']['noballs']))
            if "noballs" not in eachball['extras']:
                self.playermatchtally[nthinnings][eachball['bowler']]["inningsnoballs"].append(0)

        if "wickets" in eachball:
            self.playermatchtally[nthinnings][eachball['bowler']]["teaminningsouts"].append((len(battingorder)-1))
            for eachwicket in eachball["wickets"]:
                if any([eachwicket["kind"] == "bowled",
                        eachwicket["kind"] == "lbw",
                        eachwicket["kind"] == "hit wicket", 
                        eachwicket["kind"] == "caught",
                        eachwicket["kind"] == "stumped",
                        eachwicket["kind"] == "caught and bowled"]):
                    self.result[eachball['bowler']
                                ]["Wickets"] += 1
                    self.playermatchtally[nthinnings][eachball['bowler']]["inningswickets"].append(1)
                    self.playermatchtally[nthinnings][eachball['bowler']]["inningshowout"].append(eachwicket["kind"])
                if eachwicket["kind"] == "bowled":
                    self.result[eachball['bowler']
                                ]["Bowleds"] += 1
                    self.playermatchtally[nthinnings][eachball['bowler']]["inningsfielder"].append(None)
                if eachwicket["kind"] == "lbw":
                    self.result[eachball['bowler']
                                ]["LBWs"] += 1
                    self.playermatchtally[nthinnings][eachball['bowler']]["inningsfielder"].append(None)
                if eachwicket["kind"] == "hit wicket":
                    self.result[eachball['bowler']
                                ]["Hitwickets"] += 1
                    self.playermatchtally[nthinnings][eachball['bowler']]["inningsfielder"].append(None)
                if eachwicket["kind"] == "caught" and (not fielders or (fielders and (eachwicket["fielders"]["name"] in fielders))):
                    self.result[eachball['bowler']
                                ]["Caughts"] += 1
                    if "fielders" in eachwicket:
                            if "name" in eachwicket["fielders"][0]:
                                self.playermatchtally[nthinnings][eachball['bowler']]["inningsfielder"].append(eachwicket["fielders"][0]["name"])
                            if "name" not in eachwicket["fielders"][0]:
                                self.playermatchtally[nthinnings][eachball['bowler']]["inningsfielder"].append(None)
                if eachwicket["kind"] == "stumped":
                    self.result[eachball['bowler']
                                ]["Stumpeds"] += 1
                    if "fielders" in eachwicket:
                            if "name" in eachwicket["fielders"][0]:
                                self.playermatchtally[nthinnings][eachball['bowler']]["inningsfielder"].append(eachwicket["fielders"][0]["name"])
                            if "name" not in eachwicket["fielders"][0]:
                                self.playermatchtally[nthinnings][eachball['bowler']]["inningsfielder"].append(None)
                if eachwicket["kind"] == "caught and bowled":
                    self.result[eachball['bowler']
                                ]["Caught and Bowleds"] += 1
                    self.playermatchtally[nthinnings][eachball['bowler']]["inningsfielder"].append(None)
        if "wickets" not in eachball:
            self.playermatchtally[nthinnings][eachball['bowler']]["inningswickets"].append(0)
            self.playermatchtally[nthinnings][eachball['bowler']]["inningshowout"].append(None)
            self.playermatchtally[nthinnings][eachball['bowler']]["teaminningsouts"].append((len(battingorder)-2))
            self.playermatchtally[nthinnings][eachball['bowler']]["inningsfielder"].append(None)
        if (nthball+1) < len(eachover["deliveries"]):
            search.striketurnovergivenstats(self, eachball, 1, 3)
        if (nthball+1) == len(eachover["deliveries"]):
            search.striketurnovergivenstats(self, eachball, 0, 2)
    
    # Record fielding stats for players.
    def fieldingstats(self, eachball, eachinnings, oppositionbatters, battingmatchups, oppositionteams):
        for eachwicket in eachball["wickets"]:
            if "fielders" in eachwicket:
                for eachfielder in eachwicket["fielders"]:
                    if "name" not in eachfielder:
                        continue
                    if eachfielder["name"] in self.result and (not oppositionbatters or eachball['batter'] in battingmatchups) and (not oppositionteams or eachinnings["team"] in oppositionteams):
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
    def teambattingstats(self, eachball, inningsteam, nthball, eachover, battingorder,legdel,nthinnings):

        self.result[inningsteam]["Runs"] += eachball['runs']['total']
        if eachball['runs']['batter'] == 1:
            self.result[inningsteam]["Singles"] += 1
        if eachball['runs']['batter'] == 2:
            self.result[inningsteam]["Twos"] += 1
        if eachball['runs']['batter'] == 4:
            self.result[inningsteam]["Fours"] += 1
        if eachball['runs']['batter'] == 6:
            self.result[inningsteam]["Sixes"] += 1
        if eachball['runs']['total'] == 0:
            self.result[inningsteam
                        ]["Dot Balls"] += 1
        if "extras" not in eachball:
            self.result[inningsteam]["Balls Faced"] += 1
        if "extras" in eachball:
            if not ("wides" in eachball['extras'] or "noballs" in eachball['extras']):
                self.result[inningsteam]["Balls Faced"] += 1
        if "wickets" in eachball:
            for eachwicket in eachball["wickets"]:
                self.result[inningsteam]["Outs"] += 1
                if eachwicket["kind"] == "bowled":
                    self.result[inningsteam]["Bowled Outs"] += 1
                if eachwicket["kind"] == "lbw":
                    self.result[inningsteam]["LBW Outs"] += 1
                if eachwicket["kind"] == "hit wicket":
                    self.result[inningsteam]["Hitwickets"] += 1
                if eachwicket["kind"] == "caught":
                    self.result[inningsteam]["Caught Outs"] += 1
                if eachwicket["kind"] == "stumped":
                    self.result[inningsteam]["Stumped Outs"] += 1
                if eachwicket["kind"] == "run out":
                    self.result[inningsteam]["Run Outs"] += 1
                if eachwicket["kind"] == "caught and bowled":
                    self.result[inningsteam]["Caught and Bowled Outs"] += 1


    # Record team's bowling stats
    def teambowlingstats(self, eachball, inningsteam, nthball, eachover, battingorder,legdel):

        self.result[inningsteam]["Runsgiven"] += eachball['runs']['total']
        if eachball['runs']['batter'] == 1:
            self.result[inningsteam]["Singlesgiven"] += 1
        if eachball['runs']['batter'] == 4:
            self.result[inningsteam]["Foursgiven"] += 1
        if eachball['runs']['batter'] == 6:
            self.result[inningsteam]["Sixesgiven"] += 1
        if eachball['runs']['total'] == 0:
            self.result[inningsteam]["Dot Balls Bowled"] += 1
        if "extras" not in eachball:
            self.result[inningsteam]["Balls Bowled"] += 1
            # self.result[inningsteam]["inningstally"]["inningsballstotal"].append(1)
        if "extras" in eachball:
            if "wides" in eachball['extras']:
                self.result[inningsteam]["Wides"] += eachball['extras']['wides']
                self.result[inningsteam]["Extras"] += eachball['extras']['wides']
            if "noballs" in eachball['extras']:
                self.result[inningsteam]["No Balls"] += eachball['extras']['noballs']
                self.result[inningsteam]["Extras"] += eachball['extras']['noballs']
            if "byes" in eachball['extras']:
                self.result[inningsteam]["Balls Bowled"] += 1
                # self.result[inningsteam]["inningstally"]["inningsballstotal"].append(1)
                self.result[inningsteam]["Byes"] += eachball['extras']['byes']
                self.result[inningsteam]["Extras"] += eachball['extras']['byes']
            if "legbyes" in eachball['extras']:
                self.result[inningsteam]["Balls Bowled"] += 1
                # self.result[inningsteam]["inningstally"]["inningsballstotal"].append(1)
                self.result[inningsteam]["Leg Byes"] += eachball['extras']['legbyes']
                self.result[inningsteam]["Extras"] += eachball['extras']['legbyes']
        if "wickets" in eachball:
            # self.result[inningsteam]["inningstally"]["inningsoutsbyball"].append((len(battingorder)-1))
            for eachwicket in eachball["wickets"]:
                # self.result[inningsteam]["inningstally"]["inningshowout"].append(eachwicket["kind"])
                # self.result[inningsteam]["inningstally"]["inningsouts"].append(1)
                self.result[inningsteam]["Wickets"] += 1
                if eachwicket["kind"] == "bowled":
                    self.result[inningsteam]["Bowleds"] += 1
                    # self.result[inningsteam]["inningstally"]["inningsfielder"].append(None)
                if eachwicket["kind"] == "lbw":
                    self.result[inningsteam]["LBWs"] += 1
                    # self.result[inningsteam]["inningstally"]["inningsfielder"].append(None)
                if eachwicket["kind"] == "hit wicket":
                    self.result[inningsteam]["Hitwickets"] += 1
                    # self.result[inningsteam]["inningstally"]["inningsfielder"].append(None)
                if eachwicket["kind"] == "caught":
                    self.result[inningsteam]["Caughts"] += 1
                    # if "fielders" in eachwicket:
                    #     if "name" in eachwicket["fielders"][0]:
                    #         self.result[inningsteam]["inningstally"]["inningsfielder"].append(eachwicket["fielders"][0]["name"])
                    #     if "name" not in eachwicket["fielders"][0]:
                    #         self.result[inningsteam]["inningstally"]["inningsfielder"].append(None)
                if eachwicket["kind"] == "stumped":
                    self.result[inningsteam]["Stumpeds"] += 1
                    # if "fielders" in eachwicket:
                    #     if "name" in eachwicket["fielders"][0]:
                    #         self.result[inningsteam]["inningstally"]["inningsfielder"].append(eachwicket["fielders"][0]["name"])
                    #     if "name" not in eachwicket["fielders"][0]:
                    #         self.result[inningsteam]["inningstally"]["inningsfielder"].append(None)
                if eachwicket["kind"] == "run out":
                    self.result[inningsteam]["Runouts"] += 1
                    # if "fielders" in eachwicket:
                    #     if "name" in eachwicket["fielders"][0]:
                    #         self.result[inningsteam]["inningstally"]["inningsfielder"].append(eachwicket["fielders"][0]["name"])
                    #     if "name" not in eachwicket["fielders"][0]:
                    #         self.result[inningsteam]["inningstally"]["inningsfielder"].append(None)
                if eachwicket["kind"] == "caught and bowled":
                    self.result[inningsteam]["Caught and Bowleds"] += 1
                    # self.result[inningsteam]["inningstally"]["inningsfielder"].append(None)
        # if "wickets" not in eachball:
        #     self.result[inningsteam]["inningstally"]["inningsouts"].append(0)
        #     self.result[inningsteam]["inningstally"]["inningshowout"].append(None)
        #     self.result[inningsteam]["inningstally"]["inningsoutsbyball"].append((len(battingorder)-2))
        #     self.result[inningsteam]["inningstally"]["inningsfielder"].append(None)



    # Record player's innings stats
    def playerinnings(self, matchtimetuple, matchinfo, nthinnings, inningsteam, eachmatchtype, battingorder, bowlingorder,tempplayerindex):
        # for eachteam in matchinfo["players"]:
        #     for eachplayer in matchinfo["players"][eachteam]:
        for eachplayer in self.playermatchtally[nthinnings]:

            # for teams in matchinfo["players"]:
            #     if eachplayer in matchinfo["players"][teams]:
            #         playersteam = teams
            #     if eachplayer not in matchinfo["players"][teams]:
            #         oppositionteam = teams

            
            
            
            if eachplayer in self.result and self.playermatchtally[nthinnings][eachplayer]["batinningscount"] == True:
                # record playersinningsresult
                for eachteam in matchinfo["teams"]:
                    if eachteam != inningsteam:
                        oppositionteam = eachteam
                playersteam = inningsteam



                self.result[eachplayer]["Innings Batted"] += 1
        
                self.inningsresult["Player"].append(eachplayer)
                self.inningsresult["Venue"].append(matchinfo["venue"])
                if "event" in matchinfo and "name" in matchinfo["event"]:
                    self.inningsresult["Event"].append(matchinfo["event"]["name"])
                if "event" not in matchinfo or "name" not in matchinfo["event"]:
                    self.inningsresult["Event"].append(None)
                self.inningsresult["Date"].append(datetime.date(matchtimetuple[0], matchtimetuple[1], matchtimetuple[2]))
                self.inningsresult["Year"].append(matchtimetuple[0])
                self.inningsresult["Month"].append(matchtimetuple[1])
                self.inningsresult["Match Type"].append(eachmatchtype)
                self.inningsresult["Team"].append(playersteam)
                self.inningsresult["Opposition"].append(oppositionteam)
                self.inningsresult["Innings"].append(nthinnings + 1)
                self.inningsresult["Innings Type"].append("Batting")

                self.inningsresult["Batting Position"].append(int(battingorder.index(eachplayer) + 1))
                self.inningsresult["Score"].append(
                    sum(self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"]))
                self.inningsresult["Balls Faced"].append(
                    self.playermatchtally[nthinnings][eachplayer]["inningsballsfaced"])
                if self.playermatchtally[nthinnings][eachplayer]["inningshowout"] and self.playermatchtally[nthinnings][eachplayer]["inningshowout"][-1]!=None:
                    self.inningsresult["How Out"].append(self.playermatchtally[nthinnings][eachplayer]["inningshowout"][-1])
                if (self.playermatchtally[nthinnings][eachplayer]["inningshowout"] and self.playermatchtally[nthinnings][eachplayer]["inningshowout"][-1]==None) or (not self.playermatchtally[nthinnings][eachplayer]["inningshowout"]):
                    self.inningsresult["How Out"].append("not out")
                if self.playermatchtally[nthinnings][eachplayer]["inningsfielder"]:    
                    if self.playermatchtally[nthinnings][eachplayer]["inningsfielder"][-1]!=None:
                        self.inningsresult["Fielder"].append(self.playermatchtally[nthinnings][eachplayer]["inningsfielder"][-1])
                    if self.playermatchtally[nthinnings][eachplayer]["inningsfielder"][-1]==None:
                        self.inningsresult["Fielder"].append(None)
                if not self.playermatchtally[nthinnings][eachplayer]["inningsfielder"]:
                    self.inningsresult["Fielder"].append(None)
                self.inningsresult["Batting S/R"].append(statsprocessor.ratio(sum(self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"]), self.playermatchtally[nthinnings][eachplayer]["inningsballsfaced"], multiplier=100))
                self.inningsresult["Runs/Ball"].append(statsprocessor.ratio(sum(self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"]), self.playermatchtally[nthinnings][eachplayer]["inningsballsfaced"]))
                self.inningsresult["Boundary %"].append(statsprocessor.ratio((self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"].count(4) + self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"].count(6)),
                    self.playermatchtally[nthinnings][eachplayer]["inningsballsfaced"]))
                self.inningsresult["Boundary Rate"].append(statsprocessor.ratio(
                    self.playermatchtally[nthinnings][eachplayer]["inningsballsfaced"], (self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"].count(4) + self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"].count(6))))

                if 4 in self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"] or 6 in self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"]:
                    self.inningsresult["First Boundary Ball"].append(statsprocessor.firstboundary(self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"]))
                if 4 not in self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"] and 6 not in self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"]:
                    self.inningsresult["First Boundary Ball"].append(None)

                if 4 in self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"] or 6 in self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"]:
                    self.result[eachplayer]["firstboundary"].append(statsprocessor.firstboundary(self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"]))

                if eachplayer in tempplayerindex.keys():
                    self.inningsresult["Batter Type"].append(tempplayerindex[eachplayer]["Batting"])
                if eachplayer not in tempplayerindex.keys():
                    self.inningsresult["Batter Type"].append(None)


                for eachstat in ["Bowler Type", "Bowling Position","Runsgiven","Wickets","Balls Bowled","Overs Bowled","Economy Rate","Bowling Avg","Avg Consecutive Dot Balls", "Bowling S/R", "Runsgiven/Ball"]:
                    self.inningsresult[eachstat].append(None)

                if "result" not in matchinfo["outcome"]:
                        self.inningsresult["Match Winner"].append(matchinfo["outcome"]["winner"])
                        if matchinfo["match_type"] in ["ODI", "ODM", "T20"]:
                            if nthinnings == 0:
                                if matchinfo["outcome"]["winner"]==playersteam:
                                    self.inningsresult["Defence"].append("Successful")
                                    self.inningsresult["Chase"].append(None)
                                if matchinfo["outcome"]["winner"]==oppositionteam:
                                    self.inningsresult["Defence"].append("Unsuccessful")
                                    self.inningsresult["Chase"].append(None)
                                self.inningsresult["Target"].append(None)
                                self.inningsresult["% Target Achieved"].append(None)
                                self.inningsresult["Runs Required"].append(None)
                                self.inningsresult["Run Rate Required"].append(None)
                            if nthinnings == 1:
                                if matchinfo["outcome"]["winner"]==playersteam:
                                    self.inningsresult["Defence"].append(None)
                                    self.inningsresult["Chase"].append("Successful")
                                if matchinfo["outcome"]["winner"]==oppositionteam:
                                    self.inningsresult["Defence"].append(None)
                                    self.inningsresult["Chase"].append("Unsuccessful")
                                self.inningsresult["Target"].append(sum(self.matchtally[(nthinnings-1)]["inningsruns"])+1)
                                self.inningsresult["% Target Achieved"].append(statsprocessor.ratio(sum(self.matchtally[nthinnings]["inningsruns"]),sum(self.matchtally[(nthinnings-1)]["inningsruns"])+1,multiplier=100))
                                self.inningsresult["Runs Required"].append((sum(self.matchtally[(nthinnings-1)]["inningsruns"])+1) - sum(self.matchtally[nthinnings]["inningsruns"]))
                                # self.inningsresult["Run Rate Required"].append(((sum(self.matchtally[(nthinnings-1)]["inningsruns"])+1) - inningsruns)/ (len(set(self.matchtally[nthinnings]["inningsballs"][eachball:]))/6))
                                self.inningsresult["Run Rate Required"].append(None)

                            if nthinnings!= 0 and nthinnings!= 1:
                                self.inningsresult["Chase"].append(None)
                                self.inningsresult["Defence"].append(None)
                                self.inningsresult["Target"].append(None)
                                self.inningsresult["% Target Achieved"].append(None)
                                self.inningsresult["Runs Required"].append(None)
                                self.inningsresult["Run Rate Required"].append(None)

                        if matchinfo["match_type"] in ["Test", "MDM"]:
                            if nthinnings == 2:
                                if matchinfo["outcome"]["winner"]==playersteam:
                                    self.inningsresult["Defence"].append("Successful")
                                    self.inningsresult["Chase"].append(None)
                                if matchinfo["outcome"]["winner"]==oppositionteam:
                                    self.inningsresult["Defence"].append("Unsuccessful")
                                    self.inningsresult["Chase"].append(None)
                                self.inningsresult["Target"].append(None)
                                self.inningsresult["Runs Required"].append(None)
                                self.inningsresult["Run Rate Required"].append(None)
                                self.inningsresult["% Target Achieved"].append(None)
                            if nthinnings == 3:
                                if matchinfo["outcome"]["winner"]==playersteam:
                                    self.inningsresult["Defence"].append(None)
                                    self.inningsresult["Chase"].append("Successful")
                                if matchinfo["outcome"]["winner"]==oppositionteam:
                                    self.inningsresult["Defence"].append(None)
                                    self.inningsresult["Chase"].append("Unsuccessful")
                                self.inningsresult["Target"].append((sum(self.matchtally[(nthinnings-3)]["inningsruns"]) - sum(self.matchtally[(nthinnings-2)]["inningsruns"]) + sum(self.matchtally[(nthinnings-1)]["inningsruns"]))+1)
                                self.inningsresult["% Target Achieved"].append(statsprocessor.ratio(sum(self.matchtally[nthinnings]["inningsruns"]),((sum(self.matchtally[(nthinnings-3)]["inningsruns"]) - sum(self.matchtally[(nthinnings-2)]["inningsruns"]) + sum(self.matchtally[(nthinnings-1)]["inningsruns"]))+1)))

                                self.inningsresult["Runs Required"].append(((sum(self.matchtally[(nthinnings-3)]["inningsruns"]) - sum(self.matchtally[(nthinnings-2)]["inningsruns"]) + sum(self.matchtally[(nthinnings-1)]["inningsruns"])) - sum(self.matchtally[nthinnings]["inningsruns"]))+1)
                                self.inningsresult["Run Rate Required"].append(None)

                            if nthinnings<2:
                                self.inningsresult["Chase"].append(None)
                                self.inningsresult["Defence"].append(None)
                                self.inningsresult["Target"].append(None)
                                self.inningsresult["% Target Achieved"].append(None)
                                self.inningsresult["Runs Required"].append(None)
                                self.inningsresult["Run Rate Required"].append(None)

                if "result" in matchinfo["outcome"]:
                    self.inningsresult["Match Winner"].append(None)
                    self.inningsresult["Chase"].append(None)
                    self.inningsresult["Defence"].append(None)
                    self.inningsresult["Target"].append(None)
                    self.inningsresult["% Target Achieved"].append(None)
                    self.inningsresult["Runs Required"].append(None)
                    self.inningsresult["Run Rate Required"].append(None)



                # for eachstat in self.playermatchtally[nthinnings][eachplayer]:
                #     if type(self.playermatchtally[nthinnings][eachplayer][eachstat])==bool or type(self.playermatchtally[nthinnings][eachplayer][eachstat])==int:
                #         continue
                #     print(f"{eachstat}: {len(self.playermatchtally[nthinnings][eachplayer][eachstat])}")
                
                # record playersballresult
                for eachball, (eachballrun,batterscore, inningsball,inningsruns, non_striker, bowler, howout,inningsouts,fielder,extras,noball,wide,bye,legbye,balls) in enumerate(zip(
                    self.playermatchtally[nthinnings][eachplayer]["inningsruns"],
                    self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"],
                    self.playermatchtally[nthinnings][eachplayer]["teaminningsballs"],
                    self.playermatchtally[nthinnings][eachplayer]["teaminningsscore"],
                    self.playermatchtally[nthinnings][eachplayer]["inningsnonstriker"],
                    self.playermatchtally[nthinnings][eachplayer]["inningsbowlersfaced"],
                    self.playermatchtally[nthinnings][eachplayer]["inningshowout"],
                    self.playermatchtally[nthinnings][eachplayer]["teaminningsouts"],
                    self.playermatchtally[nthinnings][eachplayer]["inningsfielder"],
                    self.playermatchtally[nthinnings][eachplayer]["inningsextras"],
                    self.playermatchtally[nthinnings][eachplayer]["inningsnoballs"],
                    self.playermatchtally[nthinnings][eachplayer]["inningswides"],
                    self.playermatchtally[nthinnings][eachplayer]["inningsbyes"],
                    self.playermatchtally[nthinnings][eachplayer]["inningslegbyes"],
                    self.playermatchtally[nthinnings][eachplayer]["inningsballs"],
                    )):

                    self.playersballresult["Date"].append(datetime.date(matchtimetuple[0], matchtimetuple[1], matchtimetuple[2]))
                    self.playersballresult["Year"].append(matchtimetuple[0])
                    self.playersballresult["Month"].append(matchtimetuple[1])
                    self.playersballresult["Match Type"].append(matchinfo["match_type"])
                    self.playersballresult["Venue"].append(matchinfo["venue"])
                    if "event" in matchinfo:
                        self.playersballresult["Event"].append(matchinfo["event"]["name"])
                    if "event" not in matchinfo:
                        self.playersballresult["Event"].append(None)
                    self.playersballresult["Batting Team"].append(playersteam)
                    self.playersballresult["Bowling Team"].append(oppositionteam)
                    self.playersballresult["Innings"].append(nthinnings + 1)
                    self.playersballresult["Innings Type"].append("Batting")
                    self.playersballresult["Innings Ball"].append(inningsball)
                    self.playersballresult["Ball"].append(balls)
                    self.playersballresult["Innings Outs"].append(inningsouts)
                    self.playersballresult["Innings Runs"].append(inningsruns)


                    self.playersballresult["Runs"].append(eachballrun)
                    self.playersballresult["Batter Score"].append(batterscore)
                    self.playersballresult["Extras"].append(extras)
                    self.playersballresult["Noballs"].append(noball)
                    self.playersballresult["Wides"].append(wide)
                    self.playersballresult["Byes"].append(bye)
                    self.playersballresult["Legbyes"].append(legbye)
                    self.playersballresult["Bowler Extras"].append(noball+wide)
                    self.playersballresult["Fielding Extras"].append(bye+legbye)

                    if eachball == (len(self.playermatchtally[nthinnings][eachplayer]["inningshowout"])-1) and howout==None:
                        self.playersballresult["How Out"].append("not out")
                    if eachball!=(len(self.playermatchtally[nthinnings][eachplayer]["inningshowout"])-1) or (eachball == (len(self.playermatchtally[nthinnings][eachplayer]["inningshowout"])-1) and howout!=None):
                        self.playersballresult["How Out"].append(howout)
                    if howout==None:
                        self.playersballresult["Out/NotOut"].append("Not Out")
                    if howout!=None:
                        self.playersballresult["Out/NotOut"].append("Out")
                    self.playersballresult["Fielder"].append(fielder)
                    self.playersballresult["Runs/Ball"].append(sum(self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"][:(eachball+1)])/(eachball+1))


                    self.playersballresult["Batter"].append(eachplayer)
                    if eachplayer in tempplayerindex.keys():
                        self.playersballresult["Batter Type"].append(tempplayerindex[eachplayer]["Batting"])
                    if eachplayer not in tempplayerindex.keys():
                        self.playersballresult["Batter Type"].append(None)
                    self.playersballresult["Non_striker"].append(non_striker)
                    self.playersballresult["Batting Position"].append(int(battingorder.index(eachplayer) + 1))

                    self.playersballresult["Current Score"].append(sum(self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"][:(eachball+1)]))
                    self.playersballresult["Balls Faced"].append((eachball + 1))
                    self.playersballresult["Final Score"].append(sum(self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"]))
                    

                    self.playersballresult["Strike Rate"].append(round((sum(self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"][:(eachball+1)])/(eachball+1))*100,2))

                    if (sum(self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"][:(eachball+1)])/(eachball+1)) > 1:
                        self.playersballresult["S/R Zone"].append("Positive")
                    if (sum(self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"][:(eachball+1)])/(eachball+1)) <= 1:
                        self.playersballresult["S/R Zone"].append("Negative")

                    self.playersballresult["Boundary %"].append(statsprocessor.ratio((self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"][:(eachball+1)].count(4) + self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"][:(eachball+1)].count(6)),(eachball+1)))
                    self.playersballresult["Boundary Rate"].append(statsprocessor.ratio((eachball+1), (self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"][:(eachball+1)].count(4) + self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"][:(eachball+1)].count(6))))


                    self.playersballresult["Bowler"].append(bowler)
                    if bowler in tempplayerindex.keys():
                        self.playersballresult["Bowler Type"].append(tempplayerindex[bowler]["Bowling"])
                    if bowler not in tempplayerindex.keys():
                        self.playersballresult["Bowler Type"].append(None)
                    self.playersballresult["Bowling Position"].append(int(bowlingorder.index(bowler) + 1))
                    
                    self.playersballresult["Balls Bowled"].append(None)
                    self.playersballresult["Current Wickets"].append(None)
                    self.playersballresult["Final Wickets"].append(None)
                    self.playersballresult["Current Runsgiven"].append(None)
                    self.playersballresult["Final Runsgiven"].append(None)


                    if "result" not in matchinfo["outcome"]:
                        self.playersballresult["Match Winner"].append(matchinfo["outcome"]["winner"])
                        if matchinfo["match_type"] in ["ODI", "ODM", "T20"]:
                            if nthinnings == 0:
                                if matchinfo["outcome"]["winner"]==playersteam:
                                    self.playersballresult["Defence"].append("Successful")
                                    self.playersballresult["Chase"].append(None)
                                if matchinfo["outcome"]["winner"]==oppositionteam:
                                    self.playersballresult["Defence"].append("Unsuccessful")
                                    self.playersballresult["Chase"].append(None)
                                self.playersballresult["Target"].append(None)
                                self.playersballresult["% Target Achieved"].append(None)
                                self.playersballresult["Runs Required"].append(None)
                                self.playersballresult["Run Rate Required"].append(None)
                            if nthinnings == 1:
                                if matchinfo["outcome"]["winner"]==playersteam:
                                    self.playersballresult["Defence"].append(None)
                                    self.playersballresult["Chase"].append("Successful")
                                if matchinfo["outcome"]["winner"]==oppositionteam:
                                    self.playersballresult["Defence"].append(None)
                                    self.playersballresult["Chase"].append("Unsuccessful")
                                self.playersballresult["Target"].append(sum(self.matchtally[(nthinnings-1)]["inningsruns"])+1)
                                self.playersballresult["% Target Achieved"].append(statsprocessor.ratio(inningsruns,sum(self.matchtally[(nthinnings-1)]["inningsruns"])+1,multiplier=100))
                                self.playersballresult["Runs Required"].append((sum(self.matchtally[(nthinnings-1)]["inningsruns"])+1) - inningsruns)
                                # self.playersballresult["Run Rate Required"].append(((sum(self.matchtally[(nthinnings-1)]["inningsruns"])+1) - inningsruns)/ (len(set(self.matchtally[nthinnings]["inningsballs"][eachball:]))/6))
                                self.playersballresult["Run Rate Required"].append(None)

                            if nthinnings!= 0 and nthinnings!= 1:
                                self.playersballresult["Chase"].append(None)
                                self.playersballresult["Defence"].append(None)
                                self.playersballresult["Target"].append(None)
                                self.playersballresult["% Target Achieved"].append(None)
                                self.playersballresult["Runs Required"].append(None)
                                self.playersballresult["Run Rate Required"].append(None)

                        if matchinfo["match_type"] in ["Test", "MDM"]:
                            if nthinnings == 2:
                                if matchinfo["outcome"]["winner"]==playersteam:
                                    self.playersballresult["Defence"].append("Successful")
                                    self.playersballresult["Chase"].append(None)
                                if matchinfo["outcome"]["winner"]==oppositionteam:
                                    self.playersballresult["Defence"].append("Unsuccessful")
                                    self.playersballresult["Chase"].append(None)
                                self.playersballresult["Target"].append(None)
                                self.playersballresult["Runs Required"].append(None)
                                self.playersballresult["Run Rate Required"].append(None)
                                self.playersballresult["% Target Achieved"].append(None)
                            if nthinnings == 3:
                                if matchinfo["outcome"]["winner"]==playersteam:
                                    self.playersballresult["Defence"].append(None)
                                    self.playersballresult["Chase"].append("Successful")
                                if matchinfo["outcome"]["winner"]==oppositionteam:
                                    self.playersballresult["Defence"].append(None)
                                    self.playersballresult["Chase"].append("Unsuccessful")
                                self.playersballresult["Target"].append((sum(self.matchtally[(nthinnings-3)]["inningsruns"]) - sum(self.matchtally[(nthinnings-2)]["inningsruns"]) + sum(self.matchtally[(nthinnings-1)]["inningsruns"]))+1)
                                self.playersballresult["% Target Achieved"].append(statsprocessor.ratio(inningsruns,((sum(self.matchtally[(nthinnings-3)]["inningsruns"]) - sum(self.matchtally[(nthinnings-2)]["inningsruns"]) + sum(self.matchtally[(nthinnings-1)]["inningsruns"]))+1)))

                                self.playersballresult["Runs Required"].append(((sum(self.matchtally[(nthinnings-3)]["inningsruns"]) - sum(self.matchtally[(nthinnings-2)]["inningsruns"]) + sum(self.matchtally[(nthinnings-1)]["inningsruns"])) - inningsruns)+1)
                                self.playersballresult["Run Rate Required"].append(None)

                            if nthinnings<2:
                                self.playersballresult["Chase"].append(None)
                                self.playersballresult["Defence"].append(None)
                                self.playersballresult["Target"].append(None)
                                self.playersballresult["% Target Achieved"].append(None)
                                self.playersballresult["Runs Required"].append(None)
                                self.playersballresult["Run Rate Required"].append(None)

                    if "result" in matchinfo["outcome"]:
                        self.playersballresult["Match Winner"].append(None)
                        self.playersballresult["Chase"].append(None)
                        self.playersballresult["Defence"].append(None)
                        self.playersballresult["Target"].append(None)
                        self.playersballresult["% Target Achieved"].append(None)
                        self.playersballresult["Runs Required"].append(None)
                        self.playersballresult["Run Rate Required"].append(None)

                
            if eachplayer in self.result and self.playermatchtally[nthinnings][eachplayer]["bowlinningscount"] == True:
                for eachteam in matchinfo["teams"]:
                    if eachteam != inningsteam:
                        playersteam = eachteam
                oppositionteam = inningsteam

                self.result[eachplayer]["Innings Bowled"] += 1
                self.result[eachplayer]["dotballseries"].extend(statsprocessor.dotballseries(self.playermatchtally[nthinnings][eachplayer]["inningsruns"]))
                self.inningsresult["Player"].append(eachplayer)
                self.inningsresult["Venue"].append(matchinfo["venue"])
                if "event" in matchinfo and "name" in matchinfo["event"]:
                    self.inningsresult["Event"].append(matchinfo["event"]["name"])
                if "event" not in matchinfo or "name" not in matchinfo["event"]:
                    self.inningsresult["Event"].append(None)
                self.inningsresult["Date"].append(datetime.date(matchtimetuple[0], matchtimetuple[1], matchtimetuple[2]))
                self.inningsresult["Year"].append(matchtimetuple[0])
                self.inningsresult["Month"].append(matchtimetuple[1])
                self.inningsresult["Match Type"].append(eachmatchtype)
                self.inningsresult["Team"].append(playersteam)
                self.inningsresult["Opposition"].append(oppositionteam)
                self.inningsresult["Innings"].append(nthinnings + 1)
                self.inningsresult["Innings Type"].append("Bowling")

                for eachstat in ["Batter Type", "Batting Position","Score","Balls Faced","How Out","First Boundary Ball", "Batting S/R", "Runs/Ball", "Boundary %", "Boundary Rate"]:
                    self.inningsresult[eachstat].append(None)

                self.inningsresult["Bowling Position"].append(bowlingorder.index(eachplayer) + 1)
                self.inningsresult["Runsgiven"].append(sum(self.playermatchtally[nthinnings][eachplayer]["inningsruns"]))
                self.inningsresult["Wickets"].append(sum(self.playermatchtally[nthinnings][eachplayer]["inningswickets"]))
                self.inningsresult["Overs Bowled"].append(self.playermatchtally[nthinnings][eachplayer]["teaminningsballs"][-1])
                self.inningsresult["Balls Bowled"].append(math.ceil(self.playermatchtally[nthinnings][eachplayer]["inningsballsbowled"]))
                if self.playermatchtally[nthinnings][eachplayer]["inningsfielder"]:
                    if self.playermatchtally[nthinnings][eachplayer]["inningsfielder"][-1]!=None:
                        self.inningsresult["Fielder"].append(self.playermatchtally[nthinnings][eachplayer]["inningsfielder"][-1])
                    if self.playermatchtally[nthinnings][eachplayer]["inningsfielder"][-1]==None:
                        self.inningsresult["Fielder"].append(None)
                if not self.playermatchtally[nthinnings][eachplayer]["inningsfielder"]:
                    self.inningsresult["Fielder"].append(None)
                if self.playermatchtally[nthinnings][eachplayer]["inningsballsbowled"]:
                    self.inningsresult["Economy Rate"].append(round(sum(self.playermatchtally[nthinnings][eachplayer]["inningsruns"]) / (math.ceil(self.playermatchtally[nthinnings][eachplayer]["inningsballsbowled"] / 6)),2))
                    self.inningsresult["Runsgiven/Ball"].append(statsprocessor.ratio(sum(self.playermatchtally[nthinnings][eachplayer]["inningsruns"]), self.playermatchtally[nthinnings][eachplayer]["inningsballsbowled"]))
                if not self.playermatchtally[nthinnings][eachplayer]["inningsballsbowled"]:
                    self.inningsresult["Economy Rate"].append(None)
                    self.inningsresult["Runsgiven/Ball"].append(None)
                if sum(self.playermatchtally[nthinnings][eachplayer]["inningswickets"])>0:
                    self.inningsresult["Bowling Avg"].append(round(
                        sum(self.playermatchtally[nthinnings][eachplayer]["inningsruns"]) / 
                        sum(self.playermatchtally[nthinnings][eachplayer]["inningswickets"]),2))
                    self.inningsresult["Bowling S/R"].append(round(self.playermatchtally[nthinnings][eachplayer]["inningsballsbowled"] / sum(self.playermatchtally[nthinnings][eachplayer]["inningswickets"]),2))
                if sum(self.playermatchtally[nthinnings][eachplayer]["inningswickets"])==0:
                    self.inningsresult["Bowling Avg"].append(None)
                    self.inningsresult["Bowling S/R"].append(None)
                if 0 in self.playermatchtally[nthinnings][eachplayer]["inningsruns"]:
                    self.inningsresult["Avg Consecutive Dot Balls"].append(round(np.mean(statsprocessor.dotballseries(self.playermatchtally[nthinnings][eachplayer]["inningsruns"]))))
                if 0 not in self.playermatchtally[nthinnings][eachplayer]["inningsruns"]:
                    self.inningsresult["Avg Consecutive Dot Balls"].append(0)

                if eachplayer in tempplayerindex.keys():
                    self.inningsresult["Bowler Type"].append(tempplayerindex[eachplayer]["Bowling"])
                if eachplayer not in tempplayerindex.keys():
                    self.inningsresult["Bowler Type"].append(None)

                if "result" not in matchinfo["outcome"]:
                        self.inningsresult["Match Winner"].append(matchinfo["outcome"]["winner"])
                        if matchinfo["match_type"] in ["ODI", "ODM", "T20"]:
                            if nthinnings == 0:
                                if matchinfo["outcome"]["winner"]==playersteam:
                                    self.inningsresult["Defence"].append(None)
                                    self.inningsresult["Chase"].append("Successful")
                                if matchinfo["outcome"]["winner"]==oppositionteam:
                                    self.inningsresult["Defence"].append(None)
                                    self.inningsresult["Chase"].append("Unsuccessful")
                                self.inningsresult["Target"].append(None)
                                self.inningsresult["% Target Achieved"].append(None)
                                self.inningsresult["Runs Required"].append(None)
                                self.inningsresult["Run Rate Required"].append(None)
                            if nthinnings == 1:
                                if matchinfo["outcome"]["winner"]==playersteam:
                                    self.inningsresult["Defence"].append("Successful")
                                    self.inningsresult["Chase"].append(None)
                                if matchinfo["outcome"]["winner"]==oppositionteam:
                                    self.inningsresult["Defence"].append("Unsuccessful")
                                    self.inningsresult["Chase"].append(None)
                                self.inningsresult["Target"].append(sum(self.matchtally[(nthinnings-1)]["inningsruns"])+1)
                                self.inningsresult["% Target Achieved"].append(statsprocessor.ratio(sum(self.matchtally[nthinnings]["inningsruns"]),sum(self.matchtally[(nthinnings-1)]["inningsruns"])+1,multiplier=100))
                                self.inningsresult["Runs Required"].append((sum(self.matchtally[(nthinnings-1)]["inningsruns"])+1) - sum(self.matchtally[nthinnings]["inningsruns"]))
                                # self.inningsresult["Run Rate Required"].append(((sum(self.matchtally[(nthinnings-1)]["inningsruns"])+1) - inningsruns)/ (len(set(self.matchtally[nthinnings]["inningsballs"][eachball:]))/6))
                                self.inningsresult["Run Rate Required"].append(None)

                            if nthinnings!= 0 and nthinnings!= 1:
                                self.inningsresult["Chase"].append(None)
                                self.inningsresult["Defence"].append(None)
                                self.inningsresult["Target"].append(None)
                                self.inningsresult["% Target Achieved"].append(None)
                                self.inningsresult["Runs Required"].append(None)
                                self.inningsresult["Run Rate Required"].append(None)

                        if matchinfo["match_type"] in ["Test", "MDM"]:
                            if nthinnings == 2:
                                if matchinfo["outcome"]["winner"]==playersteam:
                                    self.inningsresult["Defence"].append(None)
                                    self.inningsresult["Chase"].append("Successful")
                                if matchinfo["outcome"]["winner"]==oppositionteam:
                                    self.inningsresult["Defence"].append(None)
                                    self.inningsresult["Chase"].append("Unsuccessful")
                                self.inningsresult["Target"].append(None)
                                self.inningsresult["Runs Required"].append(None)
                                self.inningsresult["Run Rate Required"].append(None)
                                self.inningsresult["% Target Achieved"].append(None)
                            if nthinnings == 3:
                                if matchinfo["outcome"]["winner"]==playersteam:
                                    self.inningsresult["Defence"].append("Successful")
                                    self.inningsresult["Chase"].append(None)
                                if matchinfo["outcome"]["winner"]==oppositionteam:
                                    self.inningsresult["Defence"].append("Unsuccessful")
                                    self.inningsresult["Chase"].append(None)
                                self.inningsresult["Target"].append((sum(self.matchtally[(nthinnings-3)]["inningsruns"]) - sum(self.matchtally[(nthinnings-2)]["inningsruns"]) + sum(self.matchtally[(nthinnings-1)]["inningsruns"]))+1)
                                self.inningsresult["% Target Achieved"].append(statsprocessor.ratio(sum(self.matchtally[nthinnings]["inningsruns"]),((sum(self.matchtally[(nthinnings-3)]["inningsruns"]) - sum(self.matchtally[(nthinnings-2)]["inningsruns"]) + sum(self.matchtally[(nthinnings-1)]["inningsruns"]))+1)))

                                self.inningsresult["Runs Required"].append(((sum(self.matchtally[(nthinnings-3)]["inningsruns"]) - sum(self.matchtally[(nthinnings-2)]["inningsruns"]) + sum(self.matchtally[(nthinnings-1)]["inningsruns"])) - sum(self.matchtally[nthinnings]["inningsruns"]))+1)
                                self.inningsresult["Run Rate Required"].append(None)

                            if nthinnings<2:
                                self.inningsresult["Chase"].append(None)
                                self.inningsresult["Defence"].append(None)
                                self.inningsresult["Target"].append(None)
                                self.inningsresult["% Target Achieved"].append(None)
                                self.inningsresult["Runs Required"].append(None)
                                self.inningsresult["Run Rate Required"].append(None)

                if "result" in matchinfo["outcome"]:
                    self.inningsresult["Match Winner"].append(None)
                    self.inningsresult["Chase"].append(None)
                    self.inningsresult["Defence"].append(None)
                    self.inningsresult["Target"].append(None)
                    self.inningsresult["% Target Achieved"].append(None)
                    self.inningsresult["Runs Required"].append(None)
                    self.inningsresult["Run Rate Required"].append(None)

                # for eachstat in self.playermatchtally[nthinnings][eachplayer]:
                #     if type(self.playermatchtally[nthinnings][eachplayer][eachstat])==bool or type(self.playermatchtally[nthinnings][eachplayer][eachstat])==int:
                #         continue
                #     print(f"{eachstat}: {len(self.playermatchtally[nthinnings][eachplayer][eachstat])}")
                # setup bowling playersballresult
                for eachball,(eachballrun,inningsball,inningsruns,batter,nonstriker,howout,inningsouts,fielder,batterscore,extras,noball,wide,bye,legbye,balls) in enumerate(zip(
                    self.playermatchtally[nthinnings][eachplayer]["inningsruns"],
                    self.playermatchtally[nthinnings][eachplayer]["teaminningsballs"],
                    self.playermatchtally[nthinnings][eachplayer]["teaminningsscore"],
                    self.playermatchtally[nthinnings][eachplayer]["inningsbattersbowledat"],
                    self.playermatchtally[nthinnings][eachplayer]["inningsnonstriker"],
                    self.playermatchtally[nthinnings][eachplayer]["inningshowout"],
                    self.playermatchtally[nthinnings][eachplayer]["teaminningsouts"],
                    self.playermatchtally[nthinnings][eachplayer]["inningsfielder"],
                    self.playermatchtally[nthinnings][eachplayer]["inningsbatterscore"],
                    self.playermatchtally[nthinnings][eachplayer]["inningsextras"],
                    self.playermatchtally[nthinnings][eachplayer]["inningsnoballs"],
                    self.playermatchtally[nthinnings][eachplayer]["inningswides"],
                    self.playermatchtally[nthinnings][eachplayer]["inningsbyes"],
                    self.playermatchtally[nthinnings][eachplayer]["inningslegbyes"],
                    self.playermatchtally[nthinnings][eachplayer]["inningsballs"],
                    )):

                    self.playersballresult["Date"].append(datetime.date(matchtimetuple[0], matchtimetuple[1], matchtimetuple[2]))
                    self.playersballresult["Year"].append(matchtimetuple[0])
                    self.playersballresult["Month"].append(matchtimetuple[1])
                    self.playersballresult["Match Type"].append(matchinfo["match_type"])
                    self.playersballresult["Venue"].append(matchinfo["venue"])
                    if "event" in matchinfo:
                        self.playersballresult["Event"].append(matchinfo["event"]["name"])
                    if "event" not in matchinfo:
                        self.playersballresult["Event"].append(None)
                    self.playersballresult["Batting Team"].append(oppositionteam)
                    self.playersballresult["Bowling Team"].append(playersteam)
                    self.playersballresult["Innings"].append(nthinnings + 1)
                    self.playersballresult["Innings Type"].append("Bowling")
                    self.playersballresult["Innings Ball"].append(inningsball)
                    self.playersballresult["Innings Outs"].append(inningsouts)
                    self.playersballresult["Innings Runs"].append(inningsouts)
                    self.playersballresult["Ball"].append(balls)

                    self.playersballresult["Runs"].append(eachballrun)
                    self.playersballresult["Batter Score"].append(batterscore)
                    self.playersballresult["Extras"].append(extras)
                    self.playersballresult["Noballs"].append(noball)
                    self.playersballresult["Wides"].append(wide)
                    self.playersballresult["Byes"].append(bye)
                    self.playersballresult["Legbyes"].append(legbye)
                    self.playersballresult["Bowler Extras"].append(noball+wide)
                    self.playersballresult["Fielding Extras"].append(bye+legbye)


                    if eachball == (len(self.playermatchtally[nthinnings][eachplayer]["inningshowout"])-1) and howout==None:
                        self.playersballresult["How Out"].append("not out")
                    if eachball!=(len(self.playermatchtally[nthinnings][eachplayer]["inningshowout"])-1) or (eachball == (len(self.playermatchtally[nthinnings][eachplayer]["inningshowout"])-1) and howout!=None):
                        self.playersballresult["How Out"].append(howout)
                    if howout==None:
                        self.playersballresult["Out/NotOut"].append("Not Out")
                    if howout!=None:
                        self.playersballresult["Out/NotOut"].append("Out")
                    self.playersballresult["Fielder"].append(fielder)
                    self.playersballresult["Runs/Ball"].append(sum(self.playermatchtally[nthinnings][eachplayer]["inningsruns"][:(eachball+1)])/(eachball+1))
                    
                    self.playersballresult["Batter"].append(batter)
                    if batter in tempplayerindex.keys():
                        self.playersballresult["Batter Type"].append(tempplayerindex[batter]["Batting"])
                    if batter not in tempplayerindex.keys():
                        self.playersballresult["Batter Type"].append(None)
                    self.playersballresult["Non_striker"].append(nonstriker)
                    self.playersballresult["Batting Position"].append(int(battingorder.index(batter) + 1))
                    self.playersballresult["Current Score"].append(None)
                    self.playersballresult["Balls Faced"].append(None)
                    self.playersballresult["Final Score"].append(None)
                    self.playersballresult["Strike Rate"].append(None)
                    self.playersballresult["S/R Zone"].append(None)
                    self.playersballresult["Boundary %"].append(None)
                    self.playersballresult["Boundary Rate"].append(None)

                    self.playersballresult["Bowler"].append(eachplayer)
                    if eachplayer in tempplayerindex.keys():
                        self.playersballresult["Bowler Type"].append(tempplayerindex[eachplayer]["Bowling"])
                    if eachplayer not in tempplayerindex.keys():
                        self.playersballresult["Bowler Type"].append(None)
                    self.playersballresult["Bowling Position"].append(int(bowlingorder.index(eachplayer) + 1))
                    self.playersballresult["Balls Bowled"].append(eachball+1)
                    self.playersballresult["Current Wickets"].append(sum(self.playermatchtally[nthinnings][eachplayer]["inningswickets"][:(eachball+1)]))
                    self.playersballresult["Final Wickets"].append(sum(self.playermatchtally[nthinnings][eachplayer]["inningswickets"]))
                    self.playersballresult["Current Runsgiven"].append(sum(self.playermatchtally[nthinnings][eachplayer]["inningsruns"][:(eachball+1)]))
                    self.playersballresult["Final Runsgiven"].append(sum(self.playermatchtally[nthinnings][eachplayer]["inningsruns"]))


                    if "result" not in matchinfo["outcome"]:
                        self.playersballresult["Match Winner"].append(matchinfo["outcome"]["winner"])
                        if matchinfo["match_type"] in ["ODI", "ODM", "T20"]:
                            if nthinnings == 0:
                                if matchinfo["outcome"]["winner"]==playersteam:
                                    self.playersballresult["Defence"].append(None)
                                    self.playersballresult["Chase"].append("Successful")
                                if matchinfo["outcome"]["winner"]==oppositionteam:
                                    self.playersballresult["Defence"].append(None)
                                    self.playersballresult["Chase"].append("Unsuccessful")
                                self.playersballresult["Target"].append(None)
                                self.playersballresult["% Target Achieved"].append(None)
                                self.playersballresult["Runs Required"].append(None)
                                self.playersballresult["Run Rate Required"].append(None)
                            if nthinnings == 1:
                                if matchinfo["outcome"]["winner"]==playersteam:
                                    self.playersballresult["Defence"].append("Successful")
                                    self.playersballresult["Chase"].append(None)
                                if matchinfo["outcome"]["winner"]==oppositionteam:
                                    self.playersballresult["Defence"].append("Unsuccessful")
                                    self.playersballresult["Chase"].append(None)
                                self.playersballresult["Target"].append(sum(self.matchtally[(nthinnings-1)]["inningsruns"])+1)
                                self.playersballresult["% Target Achieved"].append(statsprocessor.ratio(inningsruns,sum(self.matchtally[(nthinnings-1)]["inningsruns"])+1,multiplier=100))
                                self.playersballresult["Runs Required"].append((sum(self.matchtally[(nthinnings-1)]["inningsruns"])+1) - inningsruns)
                                # self.playersballresult["Run Rate Required"].append(((sum(self.matchtally[(nthinnings-1)]["inningsruns"])+1) - inningsruns)/ (len(set(self.matchtally[nthinnings]["inningsballs"][eachball:]))/6))
                                self.playersballresult["Run Rate Required"].append(None)

                            if nthinnings!= 0 and nthinnings!= 1:
                                self.playersballresult["Chase"].append(None)
                                self.playersballresult["Defence"].append(None)
                                self.playersballresult["Target"].append(None)
                                self.playersballresult["% Target Achieved"].append(None)
                                self.playersballresult["Runs Required"].append(None)
                                self.playersballresult["Run Rate Required"].append(None)

                        if matchinfo["match_type"] in ["Test", "MDM"]:
                            if nthinnings == 2:
                                if matchinfo["outcome"]["winner"]==playersteam:
                                    self.playersballresult["Defence"].append("Successful")
                                    self.playersballresult["Chase"].append(None)
                                if matchinfo["outcome"]["winner"]==oppositionteam:
                                    self.playersballresult["Defence"].append("Unsuccessful")
                                    self.playersballresult["Chase"].append(None)
                                self.playersballresult["Target"].append(None)
                                self.playersballresult["Runs Required"].append(None)
                                self.playersballresult["Run Rate Required"].append(None)
                                self.playersballresult["% Target Achieved"].append(None)
                            if nthinnings == 3:
                                if matchinfo["outcome"]["winner"]==playersteam:
                                    self.playersballresult["Defence"].append(None)
                                    self.playersballresult["Chase"].append("Successful")
                                if matchinfo["outcome"]["winner"]==oppositionteam:
                                    self.playersballresult["Defence"].append(None)
                                    self.playersballresult["Chase"].append("Unsuccessful")
                                self.playersballresult["Target"].append((sum(self.matchtally[(nthinnings-3)]["inningsruns"]) - sum(self.matchtally[(nthinnings-2)]["inningsruns"]) + sum(self.matchtally[(nthinnings-1)]["inningsruns"]))+1)
                                self.playersballresult["% Target Achieved"].append(statsprocessor.ratio(inningsruns,((sum(self.matchtally[(nthinnings-3)]["inningsruns"]) - sum(self.matchtally[(nthinnings-2)]["inningsruns"]) + sum(self.matchtally[(nthinnings-1)]["inningsruns"]))+1)))

                                self.playersballresult["Runs Required"].append(((sum(self.matchtally[(nthinnings-3)]["inningsruns"]) - sum(self.matchtally[(nthinnings-2)]["inningsruns"]) + sum(self.matchtally[(nthinnings-1)]["inningsruns"])) - inningsruns)+1)
                                self.playersballresult["Run Rate Required"].append(None)

                            if nthinnings<2:
                                self.playersballresult["Chase"].append(None)
                                self.playersballresult["Defence"].append(None)
                                self.playersballresult["Target"].append(None)
                                self.playersballresult["% Target Achieved"].append(None)
                                self.playersballresult["Runs Required"].append(None)
                                self.playersballresult["Run Rate Required"].append(None)

                    if "result" in matchinfo["outcome"]:
                        self.playersballresult["Match Winner"].append(None)
                        self.playersballresult["Chase"].append(None)
                        self.playersballresult["Defence"].append(None)
                        self.playersballresult["Target"].append(None)
                        self.playersballresult["% Target Achieved"].append(None)
                        self.playersballresult["Runs Required"].append(None)
                        self.playersballresult["Run Rate Required"].append(None)

                        
                        
                
    # Record team inningsresult
    def teaminnings(self, inningsteam, nthinnings, matchinfo, matchtimetuple, matchinnings,tempplayerindex):
        for eachteam in matchinfo["teams"]:
            if eachteam != inningsteam:
                bowlingteam = eachteam

        # things to put in ball result, required run rate, wickets left,
        self.inningsresult["Date"].append(datetime.date(matchtimetuple[0], matchtimetuple[1], matchtimetuple[2]))
        self.inningsresult["Year"].append(matchtimetuple[0])
        self.inningsresult["Month"].append(matchtimetuple[1])
        self.inningsresult["Match Type"].append(matchinfo["match_type"])
        self.inningsresult["Venue"].append(matchinfo["venue"])
        if "event" in matchinfo:
            self.inningsresult["Event"].append(matchinfo["event"]["name"])
        if "event" not in matchinfo:
            self.inningsresult["Event"].append(None)
        if "toss" in matchinfo:
            self.inningsresult["Toss Winner"].append(matchinfo["toss"]["winner"])
            self.inningsresult["Toss Decision"].append(matchinfo["toss"]["decision"])
        if "toss" not in matchinfo:
            self.inningsresult["Toss Winner"].append(None)
            self.inningsresult["Toss Decision"].append(None)
        if "result" not in matchinfo["outcome"]:
            self.inningsresult["Match Winner"].append(matchinfo["outcome"]["winner"])
        if "result" in matchinfo["outcome"]:
            self.inningsresult["Match Winner"].append(None)

        self.inningsresult["Batting Team"].append(inningsteam)
        self.inningsresult["Bowling Team"].append(bowlingteam)
        self.inningsresult["Innings"].append(nthinnings + 1)


        if inningsteam in self.result:
                self.result[inningsteam]["Innings Batted"] += 1
        if bowlingteam in self.result:
                self.result[bowlingteam]["Innings Bowled"] += 1
                self.result[bowlingteam]["dotballseries"].extend(statsprocessor.dotballseries(self.matchtally[nthinnings]["inningsruns"]))

        self.inningsresult["Declared"].append(self.matchtally[nthinnings]["inningsdeclared"])

        self.inningsresult["Score"].append(sum(self.matchtally[nthinnings]["inningsruns"]))

        self.inningsresult["Outs"].append(sum(self.matchtally[nthinnings]["inningsouts"]))
        self.inningsresult["Extras"].append(sum(self.matchtally[nthinnings]["inningsextras"]))
        self.inningsresult["Overs"].append(self.matchtally[nthinnings]["inningsballs"][-1])
        if sum(self.matchtally[nthinnings]["inningsouts"]) > 0:
            self.inningsresult["Runs/Wicket"].append(statsprocessor.ratio(sum(self.matchtally[nthinnings]["inningsruns"]), sum(self.matchtally[nthinnings]["inningsouts"])))
        if sum(self.matchtally[nthinnings]["inningsouts"])==0:
            self.inningsresult["Runs/Wicket"].append(
            sum(self.matchtally[nthinnings]["inningsruns"]))
        self.inningsresult["Runs/Ball"].append(statsprocessor.ratio(sum(self.matchtally[nthinnings]["inningsruns"]), len(set(self.matchtally[nthinnings]["inningsballs"]))))
        self.inningsresult["Run Rate"].append(statsprocessor.ratio(sum(self.matchtally[nthinnings]["inningsruns"]), len(set(self.matchtally[nthinnings]["inningsballs"])), multiplier=6))

        if 4 in self.matchtally[nthinnings]["inningsruns"] or 6 in self.matchtally[nthinnings]["inningsruns"]:
            self.inningsresult["First Boundary Ball"].append(statsprocessor.firstboundary(self.matchtally[nthinnings]["inningsruns"]))
        if 4 not in self.matchtally[nthinnings]["inningsruns"] and 6 not in self.matchtally[nthinnings]["inningsruns"]:
            self.inningsresult["First Boundary Ball"].append(None)

        self.inningsresult["Boundary %"].append(statsprocessor.ratio(
            len(self.matchtally[nthinnings]["inningsfours"]) + len(self.matchtally[nthinnings]["inningssixes"]),len(set(self.matchtally[nthinnings]["inningsballs"])), multiplier=100))

        self.inningsresult["TwosThrees %"].append(statsprocessor.ratio(
            len(self.matchtally[nthinnings]["inningstwosthrees"]),len(set(self.matchtally[nthinnings]["inningsballs"])), multiplier=100))

        if 0 in self.matchtally[nthinnings]["inningsruns"]:
            self.inningsresult["Avg Consecutive Dot Balls"].append(round(np.mean(statsprocessor.dotballseries(self.matchtally[nthinnings]["inningsruns"]))))
        if 0 not in self.matchtally[nthinnings]["inningsruns"]:
            self.inningsresult["Avg Consecutive Dot Balls"].append(0)

        if matchinfo["match_type"] in ["ODI", "ODM", "T20"]:
            if nthinnings == 0:
                self.inningsresult["Net Boundary %"].append(None)
            if nthinnings == 1:
                self.inningsresult["Net Boundary %"].append(statsprocessor.ratio(
            len(self.matchtally[nthinnings]["inningsfours"]) + len(self.matchtally[nthinnings]["inningssixes"]),len(set(self.matchtally[nthinnings]["inningsballs"])), multiplier=100) - statsprocessor.ratio(
            len(self.matchtally[nthinnings-1]["inningsfours"]) + len(self.matchtally[nthinnings-1]["inningssixes"]),len(set(self.matchtally[nthinnings-1]["inningsballs"])), multiplier=100))
        if matchinfo["match_type"] not in ["ODI", "ODM", "T20"]:
            self.inningsresult["Net Boundary %"].append(None)

        
        # record innings ballresult using batting team
        for eachball,(
            eachshot,
            inningsball,
            currentouts,
            howout,
            striker,
            nonstriker,
            bowler,
            strikerbattingpos,
            nthballinover,
            ballinover,
            extras,
            fielder
            ) in enumerate(zip(
                self.matchtally[nthinnings]["inningsruns"],
                self.matchtally[nthinnings]["inningsballs"],
                self.matchtally[nthinnings]["inningsoutsbyball"],
                self.matchtally[nthinnings]["inningshowout"],
                self.matchtally[nthinnings]["inningsstrikers"],
                self.matchtally[nthinnings]["inningsnonstrikers"],
                self.matchtally[nthinnings]["inningsbowlers"],
                self.matchtally[nthinnings]["inningsstrikersbattingpos"],
                self.matchtally[nthinnings]["inningsnthballinover"],
                self.matchtally[nthinnings]["inningsballinover"],
                self.matchtally[nthinnings]["inningsextras"],
                self.matchtally[nthinnings]["inningsfielder"])):
            self.teamsballresult["Date"].append(datetime.date(matchtimetuple[0], matchtimetuple[1], matchtimetuple[2]))
            self.teamsballresult["Year"].append(matchtimetuple[0])
            self.teamsballresult["Month"].append(matchtimetuple[1])
            self.teamsballresult["Match Type"].append(matchinfo["match_type"])
            self.teamsballresult["Venue"].append(matchinfo["venue"])
            if "event" in matchinfo:
                self.teamsballresult["Event"].append(matchinfo["event"]["name"])
            if "event" not in matchinfo:
                self.teamsballresult["Event"].append(None)
            if "toss" in matchinfo:
                self.teamsballresult["Toss Winner"].append(matchinfo["toss"]["winner"])
                self.teamsballresult["Toss Decision"].append(matchinfo["toss"]["decision"])
            if "toss" not in matchinfo:
                self.teamsballresult["Toss Winner"].append(None)
                self.teamsballresult["Toss Decision"].append(None)
            if "result" not in matchinfo["outcome"]:
                self.teamsballresult["Match Winner"].append(matchinfo["outcome"]["winner"])
                if matchinfo["match_type"] in ["ODI", "ODM", "T20"]:
                    if nthinnings == 0:
                        if matchinfo["outcome"]["winner"]==inningsteam:
                            self.teamsballresult["Defence"].append("Successful")
                            self.teamsballresult["Chase"].append(None)
                        if matchinfo["outcome"]["winner"]==bowlingteam:
                            self.teamsballresult["Defence"].append("Unsuccessful")
                            self.teamsballresult["Chase"].append(None)
                        self.teamsballresult["Target"].append(None)
                        self.teamsballresult["% Target Achieved"].append(None)
                        self.teamsballresult["Runs Required"].append(None)
                        self.teamsballresult["Run Rate Required"].append(None)
                    if nthinnings == 1:
                        if matchinfo["outcome"]["winner"]==inningsteam:
                            self.teamsballresult["Defence"].append(None)
                            self.teamsballresult["Chase"].append("Successful")
                        if matchinfo["outcome"]["winner"]==bowlingteam:
                            self.teamsballresult["Defence"].append(None)
                            self.teamsballresult["Chase"].append("Unsuccessful")
                        self.teamsballresult["Target"].append(sum(self.matchtally[(nthinnings-1)]["inningsruns"])+1)
                        self.teamsballresult["% Target Achieved"].append(statsprocessor.ratio(sum(self.matchtally[nthinnings]["inningsruns"][:(eachball+1)]),sum(self.matchtally[(nthinnings-1)]["inningsruns"])+1,multiplier=100))
                        self.teamsballresult["Runs Required"].append((sum(self.matchtally[(nthinnings-1)]["inningsruns"])+1) - sum(self.matchtally[nthinnings]["inningsruns"][:(eachball+1)]))

                        self.teamsballresult["Run Rate Required"].append(
                            ((sum(self.matchtally[(nthinnings-1)]["inningsruns"])+1) - sum(self.matchtally[nthinnings]["inningsruns"][:(eachball+1)]))/ (len(set(self.matchtally[nthinnings]["inningsballs"][eachball:]))/6)
                            )

                    if nthinnings!= 0 and nthinnings!= 1:
                        self.teamsballresult["Chase"].append(None)
                        self.teamsballresult["Defence"].append(None)
                        self.teamsballresult["Target"].append(None)
                        self.teamsballresult["% Target Achieved"].append(None)
                        self.teamsballresult["Runs Required"].append(None)
                        self.teamsballresult["Run Rate Required"].append(None)

                if matchinfo["match_type"] in ["Test", "MDM"]:
                    if nthinnings == 2:
                        if matchinfo["outcome"]["winner"]==inningsteam:
                            self.teamsballresult["Defence"].append("Successful")
                            self.teamsballresult["Chase"].append(None)
                        if matchinfo["outcome"]["winner"]==bowlingteam:
                            self.teamsballresult["Defence"].append("Unsuccessful")
                            self.teamsballresult["Chase"].append(None)
                        self.teamsballresult["Target"].append(None)
                        self.teamsballresult["% Target Achieved"].append(None)
                        self.teamsballresult["Runs Required"].append(None)
                        self.teamsballresult["Run Rate Required"].append(None)
                    if nthinnings == 3:
                        if matchinfo["outcome"]["winner"]==inningsteam:
                            self.teamsballresult["Defence"].append(None)
                            self.teamsballresult["Chase"].append("Successful")
                        if matchinfo["outcome"]["winner"]==bowlingteam:
                            self.teamsballresult["Defence"].append(None)
                            self.teamsballresult["Chase"].append("Unsuccessful")
                        self.teamsballresult["Target"].append((sum(self.matchtally[(nthinnings-3)]["inningsruns"]) - sum(self.matchtally[(nthinnings-2)]["inningsruns"]) + sum(self.matchtally[(nthinnings-1)]["inningsruns"]))+1)
                        self.teamsballresult["% Target Achieved"].append(statsprocessor.ratio(
                        sum(self.matchtally[nthinnings]["inningsruns"][:(eachball+1)]),((sum(self.matchtally[(nthinnings-3)]["inningsruns"]) - sum(self.matchtally[(nthinnings-2)]["inningsruns"]) + sum(self.matchtally[(nthinnings-1)]["inningsruns"]))+1)))

                        self.teamsballresult["Runs Required"].append(((sum(self.matchtally[(nthinnings-3)]["inningsruns"]) - sum(self.matchtally[(nthinnings-2)]["inningsruns"]) + sum(self.matchtally[(nthinnings-1)]["inningsruns"])) - sum(self.matchtally[nthinnings]["inningsruns"][:(eachball+1)]))+1)
                        self.teamsballresult["Run Rate Required"].append(None)
                    if nthinnings<2:
                        self.teamsballresult["Chase"].append(None)
                        self.teamsballresult["Defence"].append(None)
                        self.teamsballresult["Target"].append(None)
                        self.teamsballresult["% Target Achieved"].append(None)
                        self.teamsballresult["Runs Required"].append(None)
                        self.teamsballresult["Run Rate Required"].append(None)

            if "result" in matchinfo["outcome"]:
                self.teamsballresult["Match Winner"].append(None)
                self.teamsballresult["Chase"].append(None)
                self.teamsballresult["Defence"].append(None)
                self.teamsballresult["Target"].append(None)
                self.teamsballresult["% Target Achieved"].append(None)
                self.teamsballresult["Runs Required"].append(None)
                self.teamsballresult["Run Rate Required"].append(None)

            if matchinfo["match_type"]=="T20":
                if inningsball <6.1:
                    self.teamsballresult["Phase"].append("Powerplay")
                if inningsball > 6.0 and inningsball <  15.0:
                    self.teamsballresult["Phase"].append("Middle")
                if inningsball > 15.0:
                    self.teamsballresult["Phase"].append("Death")
            if matchinfo["match_type"]!="T20":
                self.teamsballresult["Phase"].append(None)

            self.teamsballresult["Batting Team"].append(inningsteam)
            self.teamsballresult["Bowling Team"].append(bowlingteam)
            self.teamsballresult["Innings"].append(nthinnings + 1)

            self.teamsballresult["Ball in Over"].append(ballinover)
            self.teamsballresult["Nth Ball in Over"].append(nthballinover)
            self.teamsballresult["Ball"].append(len(set(self.matchtally[nthinnings]["inningsballs"][:(eachball+1)])))
            self.teamsballresult["Innings Ball"].append(inningsball)
            self.teamsballresult["Innings Over"].append(int(math.ceil(inningsball)))
            self.teamsballresult["Current Score"].append(sum(self.matchtally[nthinnings]["inningsruns"][:(eachball+1)]))
            self.teamsballresult["Current Outs"].append(sum(self.matchtally[nthinnings]["inningsouts"][:(eachball+1)]))
            self.teamsballresult["Batter"].append(striker)
            self.teamsballresult["Batting Position"].append(strikerbattingpos)
            self.teamsballresult["Non_striker"].append(nonstriker)
            self.teamsballresult["Runs Scored"].append(eachshot)
            self.teamsballresult["Batter Score"].append(eachshot-extras)
            self.teamsballresult["Extras"].append(extras)
            self.teamsballresult["Extras Type"].append(None)
            self.teamsballresult["Runs/Ball"].append(
                round(sum(self.matchtally[nthinnings]["inningsruns"][:(eachball+1)])/(eachball+1),2))
            self.teamsballresult["Final Score"].append(sum(self.matchtally[nthinnings]["inningsruns"]))
            self.teamsballresult["Final Outs"].append(sum(self.matchtally[nthinnings]["inningsouts"]))
            self.teamsballresult["Final Overs"].append(self.matchtally[nthinnings]["inningsballs"][-1])
                
            if howout==None:
                self.teamsballresult["How Out"].append("Not Out")
                self.teamsballresult["Out/NotOut"].append("Not Out")
            if howout!=None:
                self.teamsballresult["How Out"].append(howout)
                self.teamsballresult["Out/NotOut"].append("Out")
            self.teamsballresult["Fielder"].append(fielder)   
            self.teamsballresult["Bowler"].append(bowler)

            if striker in tempplayerindex.keys():
                self.teamsballresult["Batter Type"].append(tempplayerindex[striker]["Batting"])
            if striker not in tempplayerindex.keys():
                self.teamsballresult["Batter Type"].append(None)
            if bowler in tempplayerindex.keys():
                self.teamsballresult["Bowler Type"].append(tempplayerindex[bowler]["Bowling"])
            if bowler not in tempplayerindex.keys():
                self.teamsballresult["Bowler Type"].append(None)


        # Recording Succesfully Defended/Chased Score
        if nthinnings == (len(matchinnings) - 1):
            if "result" not in matchinfo["outcome"]:
                if "by" in matchinfo["outcome"] and "wickets" in matchinfo["outcome"]["by"]:
                    if inningsteam in self.result:
                        self.result[inningsteam]["Chased Wins"] += 1
                        self.inningsresult["Chase"].append("Successful")
                        self.inningsresult["Chased Score"].append(sum(self.matchtally[(nthinnings-1)]["inningsruns"])+1)
                        self.inningsresult["Defence"].append("Unsuccessful")
                    if inningsteam not in self.result:
                        self.inningsresult["Chase"].append("Successful")
                        self.inningsresult["Chased Score"].append(sum(self.matchtally[(nthinnings-1)]["inningsruns"])+1)
                        self.inningsresult["Defence"].append("Unsuccessful")
                    self.inningsresult["Defended Score"].append(None)
                    self.inningsresult["Margin"].append(matchinfo["outcome"]['by']['wickets'])
                if "by" in matchinfo["outcome"] and "runs" in matchinfo["outcome"]["by"]:
                    if bowlingteam in self.result:
                        self.result[bowlingteam]["Defended Wins"] += 1
                        self.inningsresult["Defence"].append("Successful")
                        self.inningsresult["Defended Score"].append(sum(self.matchtally[(nthinnings-1)]["inningsruns"]))
                        self.inningsresult["Chase"].append("Unsuccessful")
                    if bowlingteam not in self.result:
                        self.inningsresult["Defence"].append("Successful")
                        self.inningsresult["Defended Score"].append(sum(self.matchtally[(nthinnings-1)]["inningsruns"]))
                        self.inningsresult["Chase"].append("Unsuccessful")
                    self.inningsresult["Chased Score"].append(None)
                    self.inningsresult["Margin"].append(matchinfo["outcome"]['by']['runs'])
                if "by" not in matchinfo["outcome"]:
                    self.inningsresult["Defended Score"].append(None)
                    self.inningsresult["Chased Score"].append(None)
                    self.inningsresult["Margin"].append(None)
                    self.inningsresult["Chase"].append(None)
                    self.inningsresult["Defence"].append(None)
            if "result" in matchinfo["outcome"]:
                self.inningsresult["Defended Score"].append(None)
                self.inningsresult["Chased Score"].append(None)
                self.inningsresult["Margin"].append(None)
                self.inningsresult["Chase"].append(None)
                self.inningsresult["Defence"].append(None)

        if nthinnings== (len(matchinnings) - 2):
            if "result" not in matchinfo["outcome"]:
                if matchinfo["outcome"]["winner"]==inningsteam:
                    self.inningsresult["Defended Score"].append(None)
                    self.inningsresult["Chased Score"].append(None)
                    self.inningsresult["Margin"].append(None)
                    self.inningsresult["Chase"].append(None)
                    self.inningsresult["Defence"].append("Successful")
                if matchinfo["outcome"]["winner"]!=inningsteam:
                    self.inningsresult["Defended Score"].append(None)
                    self.inningsresult["Chased Score"].append(None)
                    self.inningsresult["Margin"].append(None)
                    self.inningsresult["Chase"].append(None)
                    self.inningsresult["Defence"].append("Unsuccessful")
            if "result" in matchinfo["outcome"]:
                self.inningsresult["Defended Score"].append(None)
                self.inningsresult["Chased Score"].append(None)
                self.inningsresult["Margin"].append(None)
                self.inningsresult["Chase"].append(None)
                self.inningsresult["Defence"].append(None)
        if nthinnings!= (len(matchinnings) - 1) and nthinnings!= (len(matchinnings) - 2):
            self.inningsresult["Defended Score"].append(None)
            self.inningsresult["Chased Score"].append(None)
            self.inningsresult["Margin"].append(None)
            self.inningsresult["Chase"].append(None)
            self.inningsresult["Defence"].append(None)

        # print("Inn", len(self.inningsresult["Innings"]))
        # print(nthinnings +1)
        # print("Def", len(self.inningsresult["Defended Score"]))
        # print("Cha", len(self.inningsresult["Chased Score"]))

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

                if self.result[eachplayer]["Outs"] > 0:
                    self.result[eachplayer]["Batting Avg"] = statsprocessor.ratio(self.result[eachplayer]["Runs"],self.result[eachplayer]["Outs"], multiplier=0)
                    self.result[eachplayer]["Dismissal Rate"] = statsprocessor.ratio(self.result[eachplayer]["Balls Faced"],self.result[eachplayer]["Outs"], multiplier=0)

                if self.result[eachplayer]["firstboundary"]:
                    self.result[eachplayer]["Avg First Boundary Ball"] = round(statsprocessor.ratio(sum(self.result[eachplayer]["firstboundary"]), len(self.result[eachplayer]["firstboundary"])),2)

                if self.result[eachplayer]["totalstosopp"] > 0:
                    self.result[eachplayer]["Strike Turnover %"] = statsprocessor.ratio(self.result[eachplayer]["totalstos"], self.result[eachplayer]["totalstosopp"], multiplier=100)

                if self.result[eachplayer]["Balls Faced"] > 0 and self.result[eachplayer]["Innings Batted"] > 0:
                    self.result[eachplayer]["Batting S/R MeanAD"] = round((self.inningsresult.loc[self.inningsresult["Player"]==eachplayer,"Batting S/R"] - self.inningsresult.loc[self.inningsresult["Player"]==eachplayer,"Batting S/R"].mean()).abs().mean(), 2)
                    self.result[eachplayer]["Mean Balls Faced"] = round(statsprocessor.ratio(self.result[eachplayer]["Balls Faced"],self.result[eachplayer]["Innings Batted"], multiplier=0), 2)
                    self.result[eachplayer]["Balls Faced MeanAD"] = round((self.inningsresult.loc[self.inningsresult["Player"]==eachplayer,"Balls Faced"] - self.inningsresult.loc[self.inningsresult["Player"]==eachplayer,"Balls Faced"].mean()).abs().mean(), 2)
                    self.result[eachplayer]["Survival Consistency"] = 100 - statsprocessor.ratio(self.result[eachplayer]["Balls Faced MeanAD"], self.result[eachplayer]["Mean Balls Faced"], multiplier=100)

                if self.result[eachplayer]["Balls Faced"] > 0 and self.result[eachplayer]["Runs"] > 0:
                    self.result[eachplayer]["Mean Score"] = round(statsprocessor.ratio(self.result[eachplayer]["Runs"],self.result[eachplayer]["Innings Batted"], multiplier=0), 2)
                    self.result[eachplayer]["Score MeanAD"] = round((self.inningsresult.loc[self.inningsresult["Player"]==eachplayer,"Score"] - self.inningsresult.loc[self.inningsresult["Player"]==eachplayer,"Score"].mean()).abs().mean(),2)
                    self.result[eachplayer]["Scoring Consistency"] = 100 - statsprocessor.ratio(self.result[eachplayer]["Score MeanAD"], self.result[eachplayer]["Mean Score"], multiplier=100)

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
                    self.result[eachplayer]["Avg Consecutive Dot Balls"] = round(np.mean(self.result[eachplayer]["dotballseries"]),2)

                if self.result[eachplayer]["Wickets"] > 0:
                    self.result[eachplayer]["Bowling Avg"] = statsprocessor.ratio(
                        self.result[eachplayer]["Runsgiven"], self.result[eachplayer]["Wickets"], multiplier=0)
                    self.result[eachplayer]["Bowling S/R"] = statsprocessor.ratio(
                        self.result[eachplayer]["Balls Bowled"], self.result[eachplayer]["Wickets"], multiplier=0)

                if (self.result[eachplayer]["Fours"]+self.result[eachplayer]["Sixes"])>0:
                    self.result[eachplayer]["Boundary Rate"] = statsprocessor.ratio(self.result[eachplayer]["Balls Faced"],(self.result[eachplayer]["Fours"]+self.result[eachplayer]["Sixes"]), multiplier=0)

                if (self.result[eachplayer]["Foursgiven"]+self.result[eachplayer]["Sixesgiven"])>0:
                    self.result[eachplayer]["Boundary Given Rate"] = statsprocessor.ratio(self.result[eachplayer]["Balls Bowled"],(self.result[eachplayer]["Foursgiven"]+self.result[eachplayer]["Sixesgiven"]), multiplier=0) 

                if self.result[eachplayer]["Balls Bowled"] > 5 and self.result[eachplayer]["Economy Rate"]>0:
                    self.result[eachplayer]["Economy Rate MeanAD"] = round((self.inningsresult.loc[self.inningsresult["Player"]==eachplayer,"Economy Rate"] - self.inningsresult.loc[self.inningsresult["Player"]==eachplayer,"Economy Rate"].mean()).abs().mean(),2)

                if self.result[eachplayer]["Wickets"] > 0 and self.result[eachplayer]["Bowling Avg"]>0:
                    self.result[eachplayer]["Bowling Avg MeanAD"] = round((self.inningsresult.loc[self.inningsresult["Player"]==eachplayer,"Bowling Avg"] - self.inningsresult.loc[self.inningsresult["Player"]==eachplayer,"Bowling Avg"].mean()).abs().mean(),2)

                if self.result[eachplayer]["Wickets"] > 0 and self.result[eachplayer]["Bowling S/R"]>0:
                    self.result[eachplayer]["Bowling S/R MeanAD"] = round((self.inningsresult.loc[self.inningsresult["Player"]==eachplayer,"Bowling S/R"] - self.inningsresult.loc[self.inningsresult["Player"]==eachplayer,"Bowling S/R"].mean()).abs().mean(),2)

            self.inningsresult["Batting S/R AA"]= np.nan
            self.inningsresult.loc[self.inningsresult["Innings Type"]=="Batting","Batting S/R AA"] = self.inningsresult["Batting S/R"] - self.inningsresult["Batting S/R"].mean()

            self.ballresult["Batter Score AA"] = np.nan
            self.ballresult["Batting S/R AA"] = np.nan
            for everyball in pd.unique(self.ballresult['Balls Faced']):
                self.ballresult.loc[((self.ballresult["Innings Type"]=="Batting")&(self.ballresult["Balls Faced"]==everyball)),"Batter Score AA"] = self.ballresult.loc[((self.ballresult["Innings Type"]=="Batting")&(self.ballresult["Balls Faced"]==everyball)),"Batter Score"] - self.ballresult.loc[((self.ballresult["Innings Type"]=="Batting")&(self.ballresult["Balls Faced"]==everyball)),"Batter Score"].mean()
                self.ballresult.loc[((self.ballresult["Innings Type"]=="Batting")&(self.ballresult["Balls Faced"]==everyball)),"Batting S/R AA"] = self.ballresult.loc[((self.ballresult["Innings Type"]=="Batting")&(self.ballresult["Balls Faced"]==everyball)),"Strike Rate"] - self.ballresult.loc[((self.ballresult["Innings Type"]=="Batting")&(self.ballresult["Balls Faced"]==everyball)),"Strike Rate"].mean()
            
            
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

                self.result[eachteam]["Avg First Boundary Ball"] = round(self.inningsresult.loc[self.inningsresult["Batting Team"]==eachteam,"First Boundary Ball"].mean(),2)

                if self.result[eachteam]["Outs"] > 0:
                    self.result[eachteam]["Runs/Ball"] = statsprocessor.ratio(self.result[eachteam]["Runs"],self.result[eachteam]["Outs"])

                if self.result[eachteam]["Balls Faced"] > 5 and self.result[eachteam]["Run Rate"]>0:
                    self.result[eachteam]["Run Rate MeanAD"]=round((self.inningsresult.loc[self.inningsresult["Batting Team"]==eachteam,"Run Rate"] - self.inningsresult.loc[self.inningsresult["Batting Team"]==eachteam,"Run Rate"].mean()).abs().mean(), 2)

                if self.result[eachteam]["Runs"] > 0 and self.result[eachteam]["Innings Batted"] > 0:
                    self.result[eachteam]["Score MeanAD"]=round((self.inningsresult.loc[self.inningsresult["Batting Team"]==eachteam,"Score"] - self.inningsresult.loc[self.inningsresult["Batting Team"]==eachteam,"Score"].mean()).abs().mean(), 2) 
                    self.result[eachteam]["Mean Score"]=round(statsprocessor.ratio(self.result[eachteam]["Runs"], self.result[eachteam]["Innings Batted"], multiplier=0), 2)
                    self.result[eachteam]["Scoring Consistency"] = statsprocessor.ratio(self.result[eachteam]["Score MeanAD"], self.result[eachteam]["Mean Score"], multiplier=100)

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
                
                if self.result[eachteam]["Balls Bowled"] > 5 and self.result[eachteam]["Runsgiven Rate"]>0:
                    self.result[eachteam]["Runsgiven Rate MeanAD"] = round((self.inningsresult.loc[self.inningsresult["Bowling Team"]==eachteam,"Run Rate"] - self.inningsresult.loc[self.inningsresult["Bowling Team"]==eachteam,"Run Rate"].mean()).abs().mean(), 2)

                if self.result[eachteam]["Wickets"] > 0:
                    self.result[eachteam]['Runsgiven/Wicket'] = statsprocessor.ratio(
                        self.result[eachteam]["Runsgiven"], self.result[eachteam]["Wickets"])
                
                if self.result[eachteam]["dotballseries"]:
                    self.result[eachteam]["Avg Consecutive Dot Balls"] = round(np.mean(self.result[eachteam]["dotballseries"]),2)

                self.result[eachteam]["Net Run Rate"] = self.result[eachteam]["Run Rate"] - self.result[eachteam]["Runsgiven Rate"]
                self.result[eachteam]["Net Boundary %"] = self.result[eachteam]["Boundary %"] - self.result[eachteam]["Boundary Given %"]

    # Sum and record stats from all players and teams in a search
    def sumstats(self, allgamesplayed, allgameswinloss, allgamesdrawn,playerindex):    
        if self.players or self.allplayers==True:
            search.addplayerstoresult(self, "All Players",playerindex)
            # self.result["All Players"] = {}
            # for eachstat in self.result[0].keys():
            #     if eachstat == "Players":
            #         self.result["All Players"][eachstat] = "All Players"
            #     if type(self.result[0][eachstat]) == int:
            #         self.result["All Players"][eachstat] = 0
            #     if type(self.result[0][eachstat]) == list:
            #         self.result["All Players"][eachstat] = []
            
            
            for eachstat in self.result["All Players"]:
                statavg=[]
                if type(self.result["All Players"][eachstat]) == int or type(self.result["All Players"][eachstat]) == float:
                    for eachplayer in self.result:
                        if eachplayer != "All Players":
                            # statavg.append(self.result[eachplayer][eachstat])
                            self.result["All Players"][eachstat] += self.result[eachplayer][eachstat]
                    # self.result["All Players"][eachstat] = round(np.mean(statavg))
                if type(self.result["All Players"][eachstat]) == list:
                    for eachplayer in self.result:
                        if eachplayer != "All Players":
                            self.result["All Players"][eachstat].extend(self.result[eachplayer][eachstat])

        if self.teams or self.allteams==True:
            search.addteamstoresult(self, "All Teams")
            # self.result["All Teams"] = {}
            # for eachstat in self.result[0].keys():
            #     if eachstat == "Teams":
            #         self.result["All Teams"][eachstat] = "All Teams"
            #     if type(self.result[0][eachstat]) == int:
            #         self.result["All Teams"][eachstat] = 0
            #     if type(self.result[0][eachstat]) == list:
            #         self.result["All Teams"][eachstat] = []
            
            for eachstat in self.result["All Teams"]:
                if type(self.result["All Teams"][eachstat]) == int:
                    for eachteam in self.result:
                        if eachteam != "All Teams":
                            self.result["All Teams"][eachstat] += self.result[eachteam][eachstat]
                if type(self.result["All Teams"][eachstat]) == list:
                    for eachteam in self.result:
                        if eachteam != "All Teams":
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
                self.result[eachplayer]["Balls Faced MeanAD"] = round((self.inningsresult["Balls Faced"] - self.inningsresult["Balls Faced"].mean()).abs().mean(),2)
                self.result[eachplayer]["Survival Consistency"] = statsprocessor.ratio(self.result[eachplayer]["Balls Faced MeanAD"], self.result[eachplayer]["Mean Balls Faced"], multiplier=100)
            if len(self.inningsresult["Balls Faced"].dropna().index) == 0:
                self.result[eachplayer]["Mean Balls Faced"] = 0
                self.result[eachplayer]["Balls Faced MeanAD"] = 0
                self.result[eachplayer]["Survival Consistency"] = 0

            if self.result[eachplayer]["firstboundary"]:
                self.result[eachplayer]["Avg First Boundary Ball"] = round(np.mean(self.result[eachplayer]["firstboundary"]))

            if self.result[eachplayer]["totalstosopp"] > 0:
                self.result[eachplayer]["Strike Turnover %"] = statsprocessor.ratio(self.result[eachplayer]["totalstos"], self.result[eachplayer]["totalstosopp"], multiplier=100)

            if len(self.inningsresult["Batting S/R"].dropna().index) > 0:
                self.result[eachplayer]["Batting S/R MeanAD"] = round((self.inningsresult["Batting S/R"] - self.inningsresult["Batting S/R"].mean()).abs().mean(), 2)
            if len(self.inningsresult["Batting S/R"].dropna().index) == 0:
                self.result[eachplayer]["Batting S/R MeanAD"] = 0

            if len(self.inningsresult["Score"].dropna().index) > 0:
                self.result[eachplayer]["Mean Score"] = round(self.inningsresult["Score"].mean(),2)
                self.result[eachplayer]["Score MeanAD"] = round((self.inningsresult["Score"] - self.inningsresult["Score"].mean()).abs().mean(),2)
                self.result[eachplayer]["Scoring Consistency"] = statsprocessor.ratio(self.result[eachplayer]["Score MeanAD"], self.result[eachplayer]["Mean Score"], multiplier=100)
            if len(self.inningsresult["Score"].dropna().index) == 0:
                self.result[eachplayer]["Mean Score"] = 0
                self.result[eachplayer]["Score MeanAD"] = 0
                self.result[eachplayer]["Scoring Consistency"] = 0

            if self.result[eachplayer]["Outs"] > 0:
                self.result[eachplayer]["Batting Avg"] = statsprocessor.ratio(self.result[eachplayer]["Runs"],self.result[eachplayer]["Outs"], multiplier=0)
                self.result[eachplayer]["Dismissal Rate"] = statsprocessor.ratio(self.result[eachplayer]["Balls Faced"],self.result[eachplayer]["Outs"], multiplier=0)

            if (self.result[eachplayer]["Fours"]+self.result[eachplayer]["Sixes"])>0:
                self.result[eachplayer]["Boundary Rate"] = statsprocessor.ratio(self.result[eachplayer]["Balls Faced"],(self.result[eachplayer]["Fours"]+self.result[eachplayer]["Sixes"]), multiplier=0)

            if (self.result[eachplayer]["Foursgiven"]+self.result[eachplayer]["Sixesgiven"])>0:
                self.result[eachplayer]["Boundary Given Rate"] = statsprocessor.ratio(self.result[eachplayer]["Balls Bowled"],(self.result[eachplayer]["Foursgiven"]+self.result[eachplayer]["Sixesgiven"]), multiplier=0) 

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
                    np.mean(self.result[eachplayer]["dotballseries"]),2)

            if len(self.inningsresult["Overs Bowled"].dropna().index) > 0:
                self.result[eachplayer]["Economy Rate MeanAD"] = round((self.inningsresult["Economy Rate"] - self.inningsresult["Economy Rate"].mean()).abs().mean(),2)
            if len(self.inningsresult["Overs Bowled"].dropna().index) == 0:
                self.result[eachplayer]["Economy Rate MeanAD"] = 0

            if len(self.inningsresult["Wickets"].dropna().index) > 0:
                self.result[eachplayer]["Bowling Avg MeanAD"] = round((self.inningsresult["Bowling Avg"] - self.inningsresult["Bowling Avg"].mean()).abs().mean(),2)
            if len(self.inningsresult["Wickets"].dropna().index) == 0:
                self.result[eachplayer]["Bowling Avg MeanAD"] = 0

            if len(self.inningsresult["Bowling S/R"].dropna().index) > 0:
                self.result[eachplayer]["Bowling S/R MeanAD"] = round((self.inningsresult["Bowling S/R"] - self.inningsresult["Bowling S/R"].mean()).abs().mean(),2)
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

            
            self.result[eachteam]["Avg First Boundary Ball"] = round(self.inningsresult["First Boundary Ball"].mean(),2)
                
            if self.result[eachteam]["Outs"] > 0:
                self.result[eachteam]["Runs/Ball"] = statsprocessor.ratio(self.result[eachteam]["Runs"],self.result[eachteam]["Outs"])

            if len(self.inningsresult["Run Rate"].dropna().index) > 0:
                self.result[eachteam]["Run Rate MeanAD"]=round((self.inningsresult["Run Rate"] - self.inningsresult["Run Rate"].mean()).abs().mean(), 2)

            if len(self.inningsresult["Score"].dropna().index) > 0:
                self.result[eachteam]["Score MeanAD"]=round((self.inningsresult["Score"] - self.inningsresult["Score"].mean()).abs().mean(), 2) 
                self.result[eachteam]["Mean Score"]=round(self.inningsresult["Score"].mean(), 2)
                self.result[eachteam]["Scoring Consistency"] = statsprocessor.ratio(self.result[eachteam]["Score MeanAD"], self.result[eachteam]["Mean Score"], multiplier=100)

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
                self.result[eachteam]["Avg Consecutive Dot Balls"] = round(np.mean(self.result[eachteam]["dotballseries"]),2)
            
            if len(self.inningsresult["Run Rate"].dropna().index) > 0:
                self.result[eachteam]["Runsgiven Rate MeanAD"] = round((self.inningsresult["Run Rate"] - self.inningsresult["Run Rate"].mean()).abs().mean(), 2)

            if self.result[eachteam]["Wickets"] > 0:
                self.result[eachteam]['Runsgiven/Wicket'] = statsprocessor.ratio(
                    self.result[eachteam]["Runsgiven"], self.result[eachteam]["Wickets"], multiplier=0)

            self.result[eachteam]["Net Run Rate"] = self.result[eachteam]["Run Rate"] - self.result[eachteam]["Runsgiven Rate"]
            self.result[eachteam]["Net Boundary %"] = self.result[eachteam]["Boundary %"] - self.result[eachteam]["Boundary Given %"]

    def cleanup(self):
        for eachdict in self.result:
            removestats = ["firstboundary", "totalstos", "totalstosopp", "totalstosgiven", "totalstosgivenopp","dotballseries","inningstally"]
            for eachstat in removestats:
                if eachstat in self.result[eachdict]: 
                    self.result[eachdict].pop(eachstat)

    # This is the main function to be applied to search object.
    def stats(self, database, from_date, to_date, matchtype, betweenovers=None, innings=None, sex=None, playersteams=None, teammates=None, oppositionbatters=None, oppositionbowlers = None, oppositionteams=None, venue=None, event=None, teamtype=None, matchresult=None, superover=None, battingposition=None, bowlingposition=None, fielders=None, toss=None, tossdecision=None, sumstats=False, playerindexfile=None):
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
        if playerindexfile==None:
            pindexfile = open(f"{currentdir}/playerindex.json")
            playerindex = json.load(pindexfile)
        if playerindexfile!=None:
            pindexfile = open(playerindexfile)
            playerindex = json.load(pindexfile)

        battingmatchups=None
        if oppositionbatters == None:
            oppositionbatters = []
            battingmatchups = []

        
        if oppositionbatters:
            battingmatchups = []
            for eachname in oppositionbatters:
                if eachname in playerindex.keys():
                    battingmatchups.append(eachname)
                if eachname in ["Right hand","Left hand"]:
                    for eachplayer in playerindex:
                        battingmatchups.extend([eachplayer for (k,v) in playerindex[eachplayer].items() if v==eachname])

        bowlingmatchups=None
        if oppositionbowlers == None:
            oppositionbowlers = []
            bowlingmatchups = []
        if oppositionbowlers:
            bowlingmatchups = []
            for eachname in oppositionbowlers:
                if eachname in playerindex.keys():
                    bowlingmatchups.append(eachname)
                if eachname in ["Right arm pace","Left arm pace","Right arm off break","Right arm leg break","Left arm orthodox","Left arm wrist spin"]:
                    for eachplayer in playerindex:
                        bowlingmatchups.extend([eachplayer for (k,v) in playerindex[eachplayer].items() if v==eachname])

        if oppositionteams == None:
            oppositionteams = []
        if venue == None:
            venue = []
        if event ==None:
            event =[]
        if teamtype ==None:
            teamtype =[]
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
                search.addplayerstoresult(self, eachplayer,playerindex)
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

        # start = time.time()
        
        # Setup tally of games and results for "all teams" stats.
        allgamesplayed = 0
        allgameswinloss = 0
        allgamesdrawn = 0

        # load playerindex
        # playerindexfile = open(f"{currentdir}/playerindex.json")
        # players = json.load(playerindexfile)
        
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

                    # creat temporary player index
                    # tempplayerindex={"Batting":{"Right hand":[],"Left hand":[]},"Bowling":{"Right arm pace":[],"Left arm pace":[],"Right arm off break":[],"Right arm leg break":[],"Left arm orthodox":[],"Left arm wrist spin":[]}}
                    # for eachplayer in match['info']['registry']['people'].keys():
                    #     if eachplayer in playerindex.keys():
                    #         if  playerindex[eachplayer]["Batting"] in tempplayerindex["Batting"]:
                    #             tempplayerindex["Batting"][playerindex[eachplayer]["Batting"]].append(eachplayer)
                    #         if  playerindex[eachplayer]["Bowling"] in tempplayerindex["Bowling"]:
                    #             tempplayerindex["Bowling"][playerindex[eachplayer]["Bowling"]].append(eachplayer)
                    tempplayerindex = playerindex



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

                    # Team type check
                    if teamtype and ("team_type" not in match["info"] or match["info"]["team_type"] not in teamtype):
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

                    # Toss check
                    if toss and "winner" in match["info"]["toss"] and ((toss=="won" and match["info"]["toss"]["winner"] not in self.teams) or (toss=="lost" and match["info"]["toss"]["winner"] in self.teams)):
                        continue

                    # Toss decision check
                    if tossdecision and "decision" in  match["info"]["toss"] and match["info"]["toss"]["decision"]!=tossdecision:
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

                    # Add teams for allteams search
                    if self.allteams==True:
                        for eachteam in match["info"]["teams"]:
                            if eachteam not in self.result:
                                search.addteamstoresult(self, eachteam)

                    # Add players for allplayers search
                    # if self.allplayers==True:
                    #     for eachteam in match["info"]["players"]:
                    #         for eachplayer in match["info"]["players"][eachteam]:
                    #             if eachplayer not in self.result:
                    #                 search.addplayerstoresult(self, eachplayer)

                    # All Players and All Teams games/wins/draw/ties record
                    # TODO rewrite for ties and add these to stats dict. Hard because T20s have superovers to decide ties.
                    # TODO move this inside games and wins. and move games and wins down after innings finished.
                    if sumstats==True:
                        allgamesplayed += 1
                        if "result" in match["info"]["outcome"] and match["info"]["outcome"]['result'] == "draw":
                            allgamesdrawn += 1
                        if "winner" in match["info"]["outcome"]:
                            allgameswinloss += 1

                    self.matchtally = {}
                    search.teammatchtallysetup(self,match["info"],match['innings'])

                    self.playermatchtally = {}
                    search.playermatchtallysetup(self,match["info"],match['innings'])

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
                        
                        # PROBLEM this is getting created before the first match where allplayers scores is create.
                        # Setup running tally of innings scores
                        # search.setupinningscores(self)

                        # Create list of batters in for this innings.
                        battingorder = []
                        bowlingorder = []

                        # Creat list of mandatory and optional powerplays in this innings.
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
                            legdel=1
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
                                            search.addplayerstoresult(self, eachplayer,playerindex)
                                    if "wickets" in eachball:
                                        for eachwicket in eachball["wickets"]:
                                            if "fielders" in eachwicket:
                                                for eachfielder in eachwicket["fielders"]:
                                                    if "name" not in eachfielder:
                                                        continue
                                                    if eachfielder["name"] not in self.result:
                                                        search.addplayerstoresult(self, eachfielder["name"],playerindex)

                                # Record team innings tally
                                search.teaminningstally(self,nthball,eachball,legdel,eachover, battingorder, nthinnings)
                                if "declared" in eachinnings:
                                    self.matchtally[nthinnings]["inningsdeclared"] = True
                                
                                # record player innings tally
                                # search.playerinningstally(self,nthball,eachball,legdel,eachover, battingorder, nthinnings)

                                # Record Player stats
                                if self.players or self.allplayers==True:
                                    
                                    # Striker's stats
                                    if eachball['batter'] in self.result and (not oppositionbowlers or eachball['bowler'] in bowlingmatchups) and (not oppositionteams or eachinnings["team"] not in oppositionteams) and (not battingposition or (battingposition and ((battingorder.index(eachball['batter']) + 1) in battingposition))):
                                        search.strikerstats(self, eachball, nthball, eachover,battingorder,legdel, nthinnings)
    
                                    # Non-striker's outs.
                                    if eachball["non_striker"] in self.result and "wickets" in eachball and (not oppositionteams or eachinnings["team"] not in oppositionteams) and (not battingposition or (battingposition and ((battingorder.index(eachball['non_striker']) + 1) in battingposition))):
                                        search.nonstrikerstats(self, eachball, oppositionbowlers,nthinnings)

                                    # Bowling stats
                                    if eachball['bowler'] in self.result and (not oppositionbatters or eachball['batter'] in battingmatchups) and (not oppositionteams or eachinnings["team"] in oppositionteams) and (not bowlingposition or (bowlingposition and ((bowlingorder.index(eachball['bowler']) + 1) in bowlingposition))):
                                        search.bowlerstats(self, eachball, fielders, nthball, eachover,battingorder,legdel,nthinnings)

                                    # Fielding stats
                                    if "wickets" in eachball:
                                        search.fieldingstats(self, eachball, eachinnings, oppositionbatters, battingmatchups, oppositionteams)

                                # Record Team stats
                                if self.teams or self.allteams==True:

                                    # Team Batting stats
                                    if eachinnings["team"] in self.result:
                                        search.teambattingstats(self, eachball, eachinnings["team"], nthball, eachover, battingorder,legdel,nthinnings)

                                    # Team Bowling stats
                                    for eachteam in match["info"]["teams"]:
                                        if eachteam in self.result and eachteam != eachinnings["team"]:
                                            search.teambowlingstats(self, eachball, eachteam, nthball, eachover, battingorder,legdel)
                                
                                if "extras" in eachball and ("wides" not in eachball['extras'] and "noballs" not in eachball['extras']):
                                    legdel+=1
                                if "extras" not in eachball:
                                    legdel+=1

                        # Should move this to recordign at end of match so I can put in dervied innings stats like net boundary %
                        # Record Player innings and ball by ball stats
                        if self.players or self.allplayers==True:
                            search.playerinnings(self,matchtimetuple, match["info"], nthinnings, eachinnings["team"], eachmatchtype, battingorder, bowlingorder,tempplayerindex)
                        
                        # Record Team innings and ball by ball stats
                        if self.teams or self.allteams==True:

                            # Team innings score
                            # if eachinnings["team"] in self.result:
                            search.teaminnings(self, eachinnings["team"], nthinnings, match["info"], matchtimetuple, match['innings'],tempplayerindex)
                                
                        # if len(self.playersballresult["Defence"]) != len(self.playersballresult["Target"]):
                        #     print(eachfile)

                    # Individual team and players games/wins/draw/ties record
                    search.gamesandwins(self, match["info"],match['innings'],innings)

                    matchdata.close()
        matches.close()
        matchindexfile.close()
        pindexfile.close()
        # print(f'Time after stats(): {time.time() - start}')
        

        # for y in self.playersballresult.keys():
        #     print(y, len(self.playersballresult[y]))
        # print(self.ballresult)

        if self.players or self.allplayers==True:
            self.ballresult = pd.DataFrame(self.playersballresult)#.convert_dtypes(convert_integer=False,convert_floating=False)

        if self.teams or self.allteams==True:
            self.ballresult = pd.DataFrame(self.teamsballresult)

        # print(f'Time after self.ballresult creation: {time.time() - start}')
        self.inningsresult = pd.DataFrame(self.inningsresult)

        # This is commented out because it auto-includes time which doesn't look good for plotting.
        self.ballresult["Date"] = pd.to_datetime(self.ballresult["Date"])
        self.inningsresult["Date"] = pd.to_datetime(self.inningsresult["Date"])

        # print(f'Time after self.inningsresult creation: {time.time() - start}')
        # Derived Stats
        search.derivedstats(self)

        # print(f'Time after derivedstats(): {time.time() - start}')
        # All Player and All Teams Summing function
        if sumstats:
            search.sumstats(self,allgamesplayed, allgameswinloss, allgamesdrawn,playerindex)

        search.cleanup(self)

        # print(f'Time after sumstats(): {time.time() - start}')
        # if self.players or self.teams:
        df = pd.DataFrame(self.result)
        self.result = df.transpose()
        # print(f'Time after transpose(): {time.time() - start}')