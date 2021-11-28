import json
import time
import pandas as pd
import os
import zipfile
import numpy as np

import statsprocessor
import index

# for reverse lookup, I need to look for stats. One way is to write a new type of search with new class and get stats func. Other way is to write function that lists every player for a particular stat and inputs subset of tha tlist into getstats()

# Stats by batting position is just a check. to add. Hmm have to thinka bout how to do this.

class search:
    def __init__(self, players=None, teams=None, result=None) -> None:
        self.players = players
        self.teams = teams
        self.result = result


    def getstats(self, database, fromtime, totime, betweenovers=None, innings=None, sex=None, playerteams=None, oppositionbatters=None, oppositionbowlers=None, oppositionteams=None, venue=None, event=None, matchtype=None, matchresult=None):
        if betweenovers == None:
            betweenovers = []
        if innings == None:
            innings = []
        if sex == None:
            sex = []
        if playerteams ==None:
            playerteams = []
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
        if matchtype == None:
            matchtype = []
        if matchresult == None:
            matchresult = []

        if self.players:
            self.result = {}
            for eachplayer in self.players:
                self.result[eachplayer] = {"Caps": 0, "Won": 0, "Drawn": 0, "All Scores": [], "All Balls Faced": [],
                                            "inningsruns": [], "1stboundary": [], "inningsballsfaced": 0, "Runs": 0, "Fours": 0, "Sixes": 0,
                                            "Dot Balls": 0, "Balls Faced": 0, "Outs": 0, "Bowled Outs": 0, "LBW Outs": 0, "Caught Outs": 0, "Stumped Outs": 0, "Run Outs": 0, "totalstos": 0,
                                            "totalstosopp": 0, "All Runsgiven": [], "All Wickets": [],
                                            "All Overs Bowled": [], "inningsrunsgiven": [], "inningsballsbowled": 0,
                                            "inningswickets": 0, "totalrunsgiven": 0, "totalfoursgiven": 0,
                                            "totalsixesgiven": 0, "Wickets": 0, "Balls Bowled": 0, "totalextras": 0,
                                            "totaldotballsbowled": 0, "totalbowleds": 0, "totallbws": 0,
                                            "totalhitwickets": 0, "totalcaughts": 0, "totalstumpeds": 0,
                                            "totalstosgiven": 0, "totalstosgivenopp": 0, "totalcatches": 0,
                                            "totalrunouts": 0, "totalstumpings": 0, 'Win %': 0, 'Avg First Boundary Ball': 0, 'Strike Rate': 0, 'Boundary %': 0,'Dot Ball %': 0, 'Strike Turnover %': 0, 'Strike Rate MeanAD': 0, 'Score MeanAD': 0,'Average': 0, 'Economy Rate': 0, 'Economy Rate MeanAD': 0, 'Dot Ball Bowled %': 0,'Boundary Given %': 0, 'Bowling Avg': 0, 'Bowling SR': 0}
        if self.teams:
            self.result = {}
            for eachteam in self.teams:
                self.result[eachteam] = {"Games": 0, "Won": 0, "Drawn": 0, "All Scores": [], "All Outs": [],
                                        "All Overs Faced": [], "1st Innings Scores": [], "2nd Innings Scores": [],
                                        "3rd Innings Scores": [], "4th Innings Scores": [], "inningsruns": [],
                                        "inningsballsfaced": 0, "inningsouts": 0, "Defended Scores": [],
                                        "Chased Scores": [], "runmargins": [], "wicketmargins": [], "overschased": [],
                                        "Runs": 0, "Fours": 0, "Sixes": 0, "Dot Balls": 0, "Outs": 0, "Balls Faced": 0,
                                        "All Runsgiven": [], "All Wickets": [], "All Overs Bowled": [],
                                        "1st Innings Wickets": [], "2nd Innings Wickets": [], "3rd Innings Wickets": [],
                                        "4th Innings Wickets": [], "inningsrunsgiven": [], "inningsballsbowled": 0,
                                        "inningswickets": 0, "totalrunsgiven": 0, "totalfoursgiven": 0,
                                        "totalsixesgiven": 0, "Wickets": 0, "Balls Bowled": 0, "totalextras": 0,
                                        "totaldotsbowled": 0, "totalcaughts": 0, "totalrunouts": 0, "totalstumpeds": 0}

        # Ingest zipfile of data
        matches = zipfile.ZipFile(database, 'r')
        filelist = matches.namelist()
        # create an index file for eachfile
        if os.path.getmtime(database) > index.matchindex['indexedtime']:
            matchindex = {'indexedtime': 0,'Test': [], 'MDM': [], 'ODI': [], 'ODM': [], 'T20': [], 'IT20': []}
            matchindex['indexedtime'] = os.path.getmtime(database)
            for eachfile in filelist:
                if ".json" not in eachfile:
                    continue
                matchdata = matches.open(eachfile)
                match = json.load(matchdata)
                matchindex[match["info"]["match_type"]].append(eachfile)
                matchdata.close
            file = open("index.py", "w")
            file.write("matchindex = " + repr(matchindex))
            file.close

        for eachmatchtype in matchtype:
            for eachfile in index.matchindex[eachmatchtype]:
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
                if time.mktime(matchtimetuple) < time.mktime(fromtime + (0, 0, 0, 0, 0, 0)) or time.mktime(matchtimetuple) > time.mktime(totime + (0, 0, 0, 0, 0, 0)):
                    continue
                # Event Check
                if event and ("event" not in match["info"] or match["info"]["event"]["name"] not in event):
                    continue
                # Mens/Womens Check
                if sex and match["info"]["gender"] not in sex:
                    continue
                # Match type check
                if matchtype and match["info"]["match_type"] not in matchtype:
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

                # Caps and Wins record
                # rewrite for ties and superovers, and add these to stats dict.
                if self.players:
                    for eachplayer in self.players:
                        for eachteam in match["info"]["players"]:
                            if eachplayer in match["info"]["players"][eachteam]:
                                self.result[eachplayer]["Caps"] += 1
                                if "result" in match["info"]["outcome"] and match["info"]["outcome"]['result'] == "draw":
                                    self.result[eachplayer]["Drawn"] += 1
                                if "winner" in match["info"]["outcome"] and eachteam == match["info"]["outcome"]["winner"]:
                                    self.result[eachplayer]["Won"] += 1

                if self.teams:
                    for eachteam in match["info"]["teams"]:
                        if eachteam not in self.teams:
                            continue
                        self.result[eachteam]["Games"] += 1
                        if "result" in match["info"]["outcome"] and match["info"]["outcome"]['result'] == "draw":
                            self.result[eachteam]["Drawn"] += 1
                        if "winner" in match["info"]["outcome"] and eachteam in match["info"]["outcome"]["winner"]:
                            self.result[match["info"]["outcome"]
                                        ["winner"]]["Won"] += 1

                # Open each innings in match
                for nthinnings, eachinnings in enumerate(match['innings']):
                    if "super_over" in eachinnings:
                        continue
                    if innings and (nthinnings + 1) not in innings:
                        continue
                    if "overs" not in eachinnings:
                        continue

                    # Open each over in innings
                    if self.players:
                        for eachplayer in self.players:
                            self.result[eachplayer]["inningsruns"] = []
                            self.result[eachplayer]["inningsballsfaced"] = 0
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
                    for eachover in eachinnings['overs']:
                        if betweenovers and (eachover['over'] < (betweenovers[0] - 1) or eachover['over'] > (betweenovers[1] - 1)):
                            continue
                        # Open each ball
                        for nth, eachball in enumerate(eachover['deliveries']):

                            # Player stats
                            if self.players:

                                # Player Batting stats
                                if eachball['batter'] in self.players and (not oppositionbowlers or eachball['bowler'] in oppositionbowlers):
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
                                # Non-striker outs
                                if "wickets" in eachball:
                                    for eachwicket in eachball["wickets"]:
                                        if eachball["non_striker"] in self.players and eachball['non_striker'] == eachwicket["player_out"] and not oppositionbowlers:
                                            self.result[eachball['non_striker']
                                                        ]["Outs"] += 1
                                            if eachwicket["kind"] == "run out":
                                                self.result[eachball['non_striker']
                                                            ]["Run Outs"] += 1

                                # include legbyes and byes.
                                if nth < 5:
                                    if eachball['batter'] in self.players:
                                        self.result[eachball['batter']
                                                    ]["totalstosopp"] += 1
                                        if eachball['runs']['batter'] == 1 or eachball['runs']['batter'] == 3:
                                            self.result[eachball['batter']
                                                        ]["totalstos"] += 1
                                    if eachball['bowler'] in self.players:
                                        self.result[eachball['bowler']
                                                    ]["totalstosgivenopp"] += 1
                                        if eachball['runs']['batter'] == 1 or eachball['runs']['batter'] == 3:
                                            self.result[eachball['bowler']
                                                        ]["totalstosgiven"] += 1
                                if nth == 5:
                                    if eachball['batter'] in self.players:
                                        self.result[eachball['batter']
                                                    ]["totalstosopp"] += 1
                                        if eachball['runs']['batter'] == 0 or eachball['runs']['batter'] == 2:
                                            self.result[eachball['batter']
                                                        ]["totalstos"] += 1
                                    if eachball['bowler'] in self.players:
                                        self.result[eachball['bowler']
                                                    ]["totalstosgivenopp"] += 1
                                        if eachball['runs']['batter'] == 0 or eachball['runs']['batter'] == 2:
                                            self.result[eachball['bowler']
                                                        ]["totalstosgiven"] += 1

                                # Player Bowling stats
                                if eachball['bowler'] in self.players and (
                                        not oppositionbatters or eachball['batter'] in oppositionbatters):
                                    self.result[eachball['bowler']
                                                ]["totalrunsgiven"] += eachball['runs']['batter']
                                    self.result[eachball['bowler']]["inningsrunsgiven"].append(
                                        eachball['runs']['batter'])
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
                                    if "extras" in eachball:
                                        if not ("wides" in eachball['extras'] or "noballs" in eachball['extras']):
                                            self.result[eachball['bowler']
                                                        ]["Balls Bowled"] += 1
                                            self.result[eachball['bowler']
                                                        ]["inningsballsbowled"] += 1
                                        if "wides" in eachball['extras']:
                                            self.result[eachball['bowler']
                                                        ]["totalrunsgiven"] += eachball['extras']['wides']
                                            self.result[eachball['bowler']
                                                        ]["totalextras"] += eachball['extras']['wides']
                                        if "noballs" in eachball['extras']:
                                            self.result[eachball['bowler']
                                                        ]["totalrunsgiven"] += eachball['extras']['noballs']
                                            self.result[eachball['bowler']
                                                        ]["totalextras"] += eachball['extras']['noballs']
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
                                            if eachwicket["kind"] == "caught":
                                                self.result[eachball['bowler']
                                                            ]["totalcaughts"] += 1
                                            if eachwicket["kind"] == "stumped":
                                                self.result[eachball['bowler']
                                                            ]["totalstumpeds"] += 1

                                # Non-striker outs and fielding stats
                                if "wickets" in eachball:
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
                            # Team stats
                            if self.teams:

                                # Team Batting stats maybe here I should have small section to gather innings score of team.
                                if eachinnings["team"] in self.teams:
                                    self.result[eachinnings["team"]]["inningsruns"].append(
                                        eachball['runs']['total'])
                                    self.result[eachinnings["team"]
                                                ]["Runs"] += eachball['runs']['total']
                                    if eachball['runs']['batter'] == 4:
                                        self.result[eachinnings["team"]]["Fours"] += 1
                                    if eachball['runs']['batter'] == 6:
                                        self.result[eachinnings["team"]]["Sixes"] += 1
                                    if eachball['runs']['total'] == 0:
                                        self.result[eachinnings["team"]
                                                    ]["Dot Balls"] += 1
                                    if "extras" not in eachball:
                                        self.result[eachinnings["team"]
                                                    ]["Balls Faced"] += 1
                                        self.result[eachinnings["team"]
                                                    ]["inningsballsfaced"] += 1
                                    if "extras" in eachball:
                                        if not ("wides" in eachball['extras'] or "noballs" in eachball['extras']):
                                            self.result[eachinnings["team"]
                                                        ]["Balls Faced"] += 1
                                            self.result[eachinnings["team"]
                                                        ]["inningsballsfaced"] += 1
                                    if "wickets" in eachball:
                                        for eachwicket in eachball["wickets"]:
                                            self.result[eachinnings["team"]
                                                        ]["Outs"] += 1
                                            self.result[eachinnings["team"]
                                                        ]["inningsouts"] += 1

                                # Team Bowling stats
                                for eachteam in match["info"]["teams"]:
                                    if eachteam in self.teams and eachteam not in eachinnings["team"]:
                                        self.result[eachteam]["inningsrunsgiven"].append(
                                            eachball['runs']['total'])
                                        self.result[eachteam]["totalrunsgiven"] += eachball['runs']['total']
                                        if eachball['runs']['batter'] == 4:
                                            self.result[eachteam]["totalfoursgiven"] += 1
                                        if eachball['runs']['batter'] == 6:
                                            self.result[eachteam]["totalsixesgiven"] += 1
                                        if eachball['runs']['total'] == 0:
                                            self.result[eachteam]["totaldotsbowled"] += 1
                                        if "extras" not in eachball:
                                            self.result[eachteam]["Balls Bowled"] += 1
                                            self.result[eachteam]["inningsballsbowled"] += 1
                                        if "extras" in eachball:
                                            if "wides" in eachball['extras']:
                                                self.result[eachteam]["totalextras"] += eachball['extras']['wides']
                                            if "noballs" in eachball['extras']:
                                                self.result[eachteam]["totalextras"] += eachball['extras']['noballs']
                                            if "byes" in eachball['extras']:
                                                self.result[eachteam]["Balls Bowled"] += 1
                                                self.result[eachteam]["inningsballsbowled"] += 1
                                                self.result[eachteam]["totalextras"] += eachball['extras']['byes']
                                            if "legbyes" in eachball['extras']:
                                                self.result[eachteam]["Balls Bowled"] += 1
                                                self.result[eachteam]["inningsballsbowled"] += 1
                                                self.result[eachteam]["totalextras"] += eachball['extras']['legbyes']
                                        if "wickets" in eachball:
                                            for eachwicket in eachball["wickets"]:
                                                self.result[eachteam]["inningswickets"] += 1
                                                self.result[eachteam]["Wickets"] += 1
                                                if eachwicket["kind"] == "caught":
                                                    self.result[eachteam]["totalcaughts"] += 1
                                                if eachwicket["kind"] == "stumped":
                                                    self.result[eachteam]["totalstumpeds"] += 1
                                                if eachwicket["kind"] == "run out":
                                                    self.result[eachteam]["totalrunouts"] += 1

                    # List of Player scores.
                    if self.players:
                        for eachplayer in self.result:
                            if self.result[eachplayer]["inningsballsfaced"] > 0:
                                self.result[eachplayer]["All Scores"].append(
                                    sum(self.result[eachplayer]["inningsruns"]))
                                self.result[eachplayer]["All Balls Faced"].append(
                                    self.result[eachplayer]["inningsballsfaced"])
                            if 4 in self.result[eachplayer]["inningsruns"] or 6 in self.result[eachplayer]["inningsruns"]:
                                self.result[eachplayer]["1stboundary"].append(statsprocessor.firstboundary(
                                    self.result[eachplayer]["inningsruns"]))
                            if self.result[eachplayer]["inningsballsbowled"] > 0:
                                self.result[eachplayer]["All Runsgiven"].append(
                                    sum(self.result[eachplayer]["inningsrunsgiven"]))
                                self.result[eachplayer]["All Wickets"].append(
                                    self.result[eachplayer]["inningswickets"])
                                self.result[eachplayer]["All Overs Bowled"].append(
                                    round(self.result[eachplayer]["inningsballsbowled"] / 6))
                    
                    # Team innings scores
                    if self.teams:
                        if eachinnings["team"] in self.teams:
                            self.result[eachinnings["team"]]["All Scores"].append(
                                sum(self.result[eachinnings["team"]]["inningsruns"]))
                            self.result[eachinnings["team"]]["All Outs"].append(
                                self.result[eachinnings["team"]]["inningsouts"])
                            self.result[eachinnings["team"]]["All Overs Faced"].append(
                                round(self.result[eachinnings["team"]]["inningsballsfaced"] / 6))
                            if nthinnings == 0:
                                self.result[eachinnings["team"]]["1st Innings Scores"].append(
                                    sum(self.result[eachinnings["team"]]["inningsruns"]))
                            if nthinnings == 1:
                                self.result[eachinnings["team"]]["2nd Innings Scores"].append(
                                    sum(self.result[eachinnings["team"]]["inningsruns"]))
                            if nthinnings == 2:
                                self.result[eachinnings["team"]]["3rd Innings Scores"].append(
                                    sum(self.result[eachinnings["team"]]["inningsruns"]))
                            if nthinnings == 3:
                                self.result[eachinnings["team"]]["4th Innings Scores"].append(
                                    sum(self.result[eachinnings["team"]]["inningsruns"]))
                        for eachteam in match["info"]["teams"]:
                            if eachteam in self.teams and eachteam not in eachinnings["team"]:
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

                        # Recording successfully defended and chased scores.
                        if 'result' not in match['info']['outcome'] and match['info']['outcome']["winner"] in self.teams:
                            if 'runs' in match['info']['outcome']['by']:
                                if "target" in match['innings'][1]:
                                    self.result[match['info']['outcome']["winner"]]["Defended Scores"].append(
                                        match['innings'][1]['target']['runs'] - 1)
                                if nthinnings == (len(match['innings']) - 1) and match['info']['outcome']["winner"] != eachinnings["team"]:
                                    self.result[match['info']['outcome']["winner"]]["Defended Scores"].append(
                                        (sum(
                                            self.result[match['info']['outcome']["winner"]]["inningsrunsgiven"]))
                                        + match['info']['outcome']['by']['runs'])
                                self.result[match['info']['outcome']["winner"]]["runmargins"].append(
                                    match['info']['outcome']['by']['runs'])
                            if 'wickets' in match['info']['outcome']['by']:
                                if "target" in match['innings'][1]:
                                    self.result[match['info']['outcome']["winner"]]["Chased Scores"].append(
                                        match['innings'][1]['target']['runs'])
                                    self.result[match['info']['outcome']["winner"]]["overschased"].append(
                                        round(self.result[match['info']['outcome']["winner"]]["inningsballsfaced"] / 6))
                                if nthinnings == (len(match['innings']) - 1) and match['info']['outcome']["winner"] == eachinnings["team"]:
                                    self.result[match['info']['outcome']["winner"]]["Chased Scores"].append(
                                        (sum(self.result[match['info']['outcome']["winner"]]["inningsruns"])))
                                    self.result[match['info']['outcome']["winner"]]["overschased"].append(
                                        round(self.result[match['info']['outcome']["winner"]]["inningsballsfaced"] / 6))
                                self.result[match['info']['outcome']["winner"]]["wicketmargins"].append(
                                    match['info']['outcome']['by']['wickets'])

                matchdata.close()
        matches.close()

        # Derived Stats
        if self.players:
            for eachplayer in self.result:
                if self.result[eachplayer]["Caps"] > 0:
                    self.result[eachplayer]["Win %"] = statsprocessor.ratio(self.result[eachplayer]["Won"],
                                                                            self.result[eachplayer]["Caps"],
                                                                            multiplier=100)

                if self.result[eachplayer]["Balls Faced"] > 0 and self.result[eachplayer]["Runs"] > 0:
                    self.result[eachplayer]["Avg First Boundary Ball"] = round(np.mean(self.result[eachplayer]["1stboundary"]))
                    self.result[eachplayer]["Strike Rate"] = statsprocessor.ratio(self.result[eachplayer]["Runs"],
                                                                                    self.result[eachplayer][
                                                                                        "Balls Faced"], multiplier=100)
                    self.result[eachplayer]["Boundary %"] = statsprocessor.ratio(
                        (self.result[eachplayer]["Fours"]
                        + self.result[eachplayer]["Sixes"]),
                        self.result[eachplayer]["Balls Faced"], multiplier=100)
                    self.result[eachplayer]["Dot Ball %"] = statsprocessor.ratio(self.result[eachplayer]["Dot Balls"],
                                                                                    self.result[eachplayer][
                                                                                        "Balls Faced"], multiplier=100)
                    self.result[eachplayer]["Strike Turnover %"] = statsprocessor.ratio(
                        self.result[eachplayer]["totalstos"], self.result[eachplayer]["totalstosopp"], multiplier=100)
                    self.result[eachplayer]["Strike Rate MeanAD"] = statsprocessor.madfromlist(
                        self.result[eachplayer]["All Scores"], self.result[eachplayer]["All Balls Faced"], stattype="percent")
                    self.result[eachplayer]["Score MeanAD"] = statsprocessor.mad(
                        self.result[eachplayer]["All Scores"])

                if self.result[eachplayer]["Outs"] > 0:
                    self.result[eachplayer]["Average"] = statsprocessor.ratio(self.result[eachplayer]["Runs"],
                                                                                self.result[eachplayer]["Outs"],
                                                                                multiplier=0)

                if self.result[eachplayer]["Balls Bowled"] > 0:
                    self.result[eachplayer]["Economy Rate"] = statsprocessor.ratio(
                        self.result[eachplayer]["totalrunsgiven"], self.result[eachplayer]["Balls Bowled"],
                        multiplier=6)
                    self.result[eachplayer]["Economy Rate MeanAD"] = statsprocessor.madfromlist(
                        self.result[eachplayer]["All Runsgiven"], self.result[eachplayer]["All Balls Faced"], stattype="perover")
                    self.result[eachplayer]["Dot Ball Bowled %"] = statsprocessor.ratio(
                        self.result[eachplayer]["totaldotballsbowled"], self.result[eachplayer]["Balls Bowled"],
                        multiplier=100)
                    self.result[eachplayer]["Boundary Given %"] = statsprocessor.ratio(
                        (self.result[eachplayer]["totalfoursgiven"]
                        + self.result[eachplayer]["totalsixesgiven"]),
                        self.result[eachplayer]["Balls Bowled"], multiplier=100)

                if self.result[eachplayer]["Wickets"] > 0:
                    self.result[eachplayer]["Bowling Avg"] = statsprocessor.ratio(
                        self.result[eachplayer]["totalrunsgiven"], self.result[eachplayer]["Wickets"], multiplier=0)
                    self.result[eachplayer]["Bowling SR"] = statsprocessor.ratio(
                        self.result[eachplayer]["Balls Bowled"], self.result[eachplayer]["Wickets"], multiplier=0)
        if self.players:
            df = pd.DataFrame(self.result)
            self.result = df.transpose()
            # return allplayerstatsdf
        elif self.teams:
            df = pd.DataFrame(self.result)
            self.result = df.transpose()
            # return allteamstatsdf
