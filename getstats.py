import glob
import json
import statsprocessor
import time
import pandas as pd
import os
import zipfile
import index


def getstats(database, fromtime, totime, betweenovers=[], players=[], teams=[], innings=[], sex=[], playerteams=[], oppositionbatters=[], oppositionbowlers=[], oppositionteams=[], venue=[], event=[], matchtype=[], matchresult=""):
    if players:
        allplayerstats = {}
        for eachplayer in players:
            allplayerstats[eachplayer] = {"Caps": 0, "Won": 0, "Drawn": 0, "All Scores": [], "All Balls Faced": [],
                                          "inningsruns": [], "inningsballsfaced": 0, "Runs": 0, "Fours": 0, "Sixes": 0,
                                          "Dot Balls": 0, "Outs": 0, "Balls Faced": 0, "totalstos": 0,
                                          "totalstosopp": 0, "All Runsgiven": [], "All Wickets": [],
                                          "All Overs Bowled": [], "inningsrunsgiven": [], "inningsballsbowled": 0,
                                          "inningswickets": 0, "totalrunsgiven": 0, "totalfoursgiven": 0,
                                          "totalsixesgiven": 0, "Wickets": 0, "Balls Bowled": 0, "totalextras": 0,
                                          "totaldotballsbowled": 0, "totalbowleds": 0, "totallbws": 0,
                                          "totalhitwickets": 0, "totalcaughts": 0, "totalstumpeds": 0,
                                          "totalstosgiven": 0, "totalstosgivenopp": 0, "totalcatches": 0,
                                          "totalrunouts": 0, "totalstumpings": 0}
    if teams:
        allteamstats = {}
        for eachteam in teams:
            allteamstats[eachteam] = {"Games": 0, "Won": 0, "Drawn": 0, "All Scores": [], "All Outs": [],
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
    if os.path.getmtime(database) > os.path.getmtime("./index.py"):
        matchindex = {'Test': [], 'MDM': [], 'ODI': [],
                      'ODM': [], 'T20': [], 'IT20': []}
        for eachfile in filelist:
            if ".json" not in eachfile:
                continue
            matchdata = matches.open(eachfile)
            match = json.load(matchdata)
            matchindex[match["info"]["match_type"]].append(eachfile)
            matchdata.close
        file = open("./index.py", "w")
        file.write("matchindex = " + repr(matchindex))
        file.close

    for eachmatchtype in matchtype:
        for eachfile in index.matchindex[eachmatchtype]:
            matchdata = matches.open(eachfile)
            # for eachfile in glob.glob(f"{database}*.json"):
            # print(eachfile)
            # change to a "with open(filename) as matchdata" so it is closed even if there is an error in code?
            # matchdata = open(eachfile)
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
            if matchresult and matchresult in match['info']['outcome'](
                    match['info']['outcome']["winner"] not in teams or match['info']['outcome'][
                        "winner"] not in playerteams):
                continue

            # Players and Teams Check
            if (teams and (match["info"]["teams"][0] not in teams and match["info"]["teams"][1] not in teams)) and (
                    players and not any(
                    eachplayer in players for eachplayer in match['info']['registry']['people'].keys())):
                continue

            # Caps and Wins record
            # rewrite for test match draw and ties, and add these to stats dict.
            if players:
                for eachplayer in players:
                    for eachteam in match["info"]["players"]:
                        if eachplayer in match["info"]["players"][eachteam]:
                            allplayerstats[eachplayer]["Caps"] += 1
                            if "result" in match["info"]["outcome"] and match["info"]["outcome"]['result'] == "draw":
                                allplayerstats[eachplayer]["Drawn"] += 1
                            if "winner" in match["info"]["outcome"] and eachteam == match["info"]["outcome"]["winner"]:
                                allplayerstats[eachplayer]["Won"] += 1

            if teams:
                for eachteam in match["info"]["teams"]:
                    if eachteam not in teams:
                        continue
                    allteamstats[eachteam]["Games"] += 1
                    if "result" in match["info"]["outcome"] and match["info"]["outcome"]['result'] == "draw":
                        allteamstats[eachteam]["Drawn"] += 1
                    if "winner" in match["info"]["outcome"] and eachteam in match["info"]["outcome"]["winner"]:
                        allteamstats[match["info"]["outcome"]
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
                if players:
                    for eachplayer in players:
                        allplayerstats[eachplayer]["inningsruns"] = []
                        allplayerstats[eachplayer]["inningsballsfaced"] = 0
                        allplayerstats[eachplayer]["inningsrunsgiven"] = []
                        allplayerstats[eachplayer]["inningsballsbowled"] = 0
                        allplayerstats[eachplayer]["inningswickets"] = 0
                if teams:
                    for eachteam in teams:
                        allteamstats[eachteam]["inningsouts"] = 0
                        allteamstats[eachteam]["inningsruns"] = []
                        allteamstats[eachteam]["inningsballsfaced"] = 0
                        allteamstats[eachteam]["inningswickets"] = 0
                        allteamstats[eachteam]["inningsrunsgiven"] = []
                        allteamstats[eachteam]["inningsballsbowled"] = 0
                for eachover in eachinnings['overs']:
                    if betweenovers and (eachover['over'] < (betweenovers[0] - 1) or eachover['over'] > (betweenovers[1] - 1)):
                        continue
                    # Open each ball
                    for nth, eachball in enumerate(eachover['deliveries']):

                        # Player Batting stats
                        if eachball['batter'] in players and (
                                not oppositionbowlers or eachball['bowler'] in oppositionbowlers):
                            allplayerstats[eachball['batter']
                                           ]["Runs"] += eachball['runs']['batter']
                            allplayerstats[eachball['batter']]["inningsruns"].append(
                                eachball['runs']['batter'])
                            if eachball['runs']['batter'] == 4:
                                allplayerstats[eachball['batter']
                                               ]["Fours"] += 1
                            if eachball['runs']['batter'] == 6:
                                allplayerstats[eachball['batter']
                                               ]["Sixes"] += 1
                            if eachball['runs']['total'] == 0:
                                allplayerstats[eachball['batter']
                                               ]["Dot Balls"] += 1
                            if "extras" not in eachball:
                                allplayerstats[eachball['batter']
                                               ]["Balls Faced"] += 1
                                allplayerstats[eachball['batter']
                                               ]["inningsballsfaced"] += 1
                            if "extras" in eachball:
                                if not ("wides" in eachball['extras'] or "noballs" in eachball['extras']):
                                    allplayerstats[eachball['batter']
                                                   ]["Balls Faced"] += 1
                                    allplayerstats[eachball['batter']
                                                   ]["inningsballsfaced"] += 1
                            if "wickets" in eachball:
                                for eachwicket in eachball["wickets"]:
                                    if eachball['batter'] == eachwicket["player_out"]:
                                        allplayerstats[eachball['batter']
                                                       ]["Outs"] += 1
                        # include legbyes and byes.
                        if nth < 5:
                            if eachball['batter'] in players:
                                allplayerstats[eachball['batter']
                                               ]["totalstosopp"] += 1
                                if eachball['runs']['batter'] == 1 or eachball['runs']['batter'] == 3:
                                    allplayerstats[eachball['batter']
                                                   ]["totalstos"] += 1
                            if eachball['bowler'] in players:
                                allplayerstats[eachball['bowler']
                                               ]["totalstosgivenopp"] += 1
                                if eachball['runs']['batter'] == 1 or eachball['runs']['batter'] == 3:
                                    allplayerstats[eachball['bowler']
                                                   ]["totalstosgiven"] += 1
                        if nth == 5:
                            if eachball['batter'] in players:
                                allplayerstats[eachball['batter']
                                               ]["totalstosopp"] += 1
                                if eachball['runs']['batter'] == 0 or eachball['runs']['batter'] == 2:
                                    allplayerstats[eachball['batter']
                                                   ]["totalstos"] += 1
                            if eachball['bowler'] in players:
                                allplayerstats[eachball['bowler']
                                               ]["totalstosgivenopp"] += 1
                                if eachball['runs']['batter'] == 0 or eachball['runs']['batter'] == 2:
                                    allplayerstats[eachball['bowler']
                                                   ]["totalstosgiven"] += 1

                        # Player Bowling stats
                        if eachball['bowler'] in players and (
                                not oppositionbatters or eachball['batter'] in oppositionbatters):
                            allplayerstats[eachball['bowler']
                                           ]["totalrunsgiven"] += eachball['runs']['batter']
                            allplayerstats[eachball['bowler']]["inningsrunsgiven"].append(
                                eachball['runs']['batter'])
                            if eachball['runs']['batter'] == 4:
                                allplayerstats[eachball['bowler']
                                               ]["totalfoursgiven"] += 1
                            if eachball['runs']['batter'] == 6:
                                allplayerstats[eachball['bowler']
                                               ]["totalsixesgiven"] += 1
                            if eachball['runs']['total'] == 0:
                                allplayerstats[eachball['bowler']
                                               ]["totaldotballsbowled"] += 1
                            if "extras" not in eachball:
                                allplayerstats[eachball['bowler']
                                               ]["Balls Bowled"] += 1
                                allplayerstats[eachball['bowler']
                                               ]["inningsballsbowled"] += 1
                            if "extras" in eachball:
                                if not ("wides" in eachball['extras'] or "noballs" in eachball['extras']):
                                    allplayerstats[eachball['bowler']
                                                   ]["Balls Bowled"] += 1
                                    allplayerstats[eachball['bowler']
                                                   ]["inningsballsbowled"] += 1
                                if "wides" in eachball['extras']:
                                    allplayerstats[eachball['bowler']
                                                   ]["totalrunsgiven"] += eachball['extras']['wides']
                                    allplayerstats[eachball['bowler']
                                                   ]["totalextras"] += eachball['extras']['wides']
                                if "noballs" in eachball['extras']:
                                    allplayerstats[eachball['bowler']
                                                   ]["totalrunsgiven"] += eachball['extras']['noballs']
                                    allplayerstats[eachball['bowler']
                                                   ]["totalextras"] += eachball['extras']['noballs']
                            if "wickets" in eachball:
                                for eachwicket in eachball["wickets"]:
                                    if any([eachwicket["kind"] == "bowled", eachwicket["kind"] == "lbw",
                                            eachwicket["kind"] == "hit wicket", eachwicket["kind"] == "caught",
                                            eachwicket["kind"] == "stumped"]):
                                        allplayerstats[eachball['bowler']
                                                       ]["Wickets"] += 1
                                        allplayerstats[eachball['bowler']
                                                       ]["inningswickets"] += 1
                                    if eachwicket["kind"] == "bowled":
                                        allplayerstats[eachball['bowler']
                                                       ]["totalbowleds"] += 1
                                    if eachwicket["kind"] == "lbw":
                                        allplayerstats[eachball['bowler']
                                                       ]["totallbws"] += 1
                                    if eachwicket["kind"] == "hit wicket":
                                        allplayerstats[eachball['bowler']
                                                       ]["totalhitwickets"] += 1
                                    if eachwicket["kind"] == "caught":
                                        allplayerstats[eachball['bowler']
                                                       ]["totalcaughts"] += 1
                                    if eachwicket["kind"] == "stumped":
                                        allplayerstats[eachball['bowler']
                                                       ]["totalstumpeds"] += 1

                        # Team Batting stats maybe here I should have small section to gather innings score of team.
                        if eachinnings["team"] in teams:
                            allteamstats[eachinnings["team"]]["inningsruns"].append(
                                eachball['runs']['total'])
                            allteamstats[eachinnings["team"]
                                         ]["Runs"] += eachball['runs']['total']
                            if eachball['runs']['batter'] == 4:
                                allteamstats[eachinnings["team"]]["Fours"] += 1
                            if eachball['runs']['batter'] == 6:
                                allteamstats[eachinnings["team"]]["Sixes"] += 1
                            if eachball['runs']['total'] == 0:
                                allteamstats[eachinnings["team"]
                                             ]["Dot Balls"] += 1
                            if "extras" not in eachball:
                                allteamstats[eachinnings["team"]
                                             ]["Balls Faced"] += 1
                                allteamstats[eachinnings["team"]
                                             ]["inningsballsfaced"] += 1
                            if "extras" in eachball:
                                if not ("wides" in eachball['extras'] or "noballs" in eachball['extras']):
                                    allteamstats[eachinnings["team"]
                                                 ]["Balls Faced"] += 1
                                    allteamstats[eachinnings["team"]
                                                 ]["inningsballsfaced"] += 1
                            if "wickets" in eachball:
                                for eachwicket in eachball["wickets"]:
                                    allteamstats[eachinnings["team"]
                                                 ]["Outs"] += 1
                                    allteamstats[eachinnings["team"]
                                                 ]["inningsouts"] += 1

                        # Team Bowling stats
                        for eachteam in match["info"]["teams"]:
                            if eachteam in teams and eachteam not in eachinnings["team"]:
                                allteamstats[eachteam]["inningsrunsgiven"].append(
                                    eachball['runs']['total'])
                                allteamstats[eachteam]["totalrunsgiven"] += eachball['runs']['total']
                                if eachball['runs']['batter'] == 4:
                                    allteamstats[eachteam]["totalfoursgiven"] += 1
                                if eachball['runs']['batter'] == 6:
                                    allteamstats[eachteam]["totalsixesgiven"] += 1
                                if eachball['runs']['total'] == 0:
                                    allteamstats[eachteam]["totaldotsbowled"] += 1
                                if "extras" not in eachball:
                                    allteamstats[eachteam]["Balls Bowled"] += 1
                                    allteamstats[eachteam]["inningsballsbowled"] += 1
                                if "extras" in eachball:
                                    if "wides" in eachball['extras']:
                                        allteamstats[eachteam]["totalextras"] += eachball['extras']['wides']
                                    if "noballs" in eachball['extras']:
                                        allteamstats[eachteam]["totalextras"] += eachball['extras']['noballs']
                                    if "byes" in eachball['extras']:
                                        allteamstats[eachteam]["Balls Bowled"] += 1
                                        allteamstats[eachteam]["inningsballsbowled"] += 1
                                        allteamstats[eachteam]["totalextras"] += eachball['extras']['byes']
                                    if "legbyes" in eachball['extras']:
                                        allteamstats[eachteam]["Balls Bowled"] += 1
                                        allteamstats[eachteam]["inningsballsbowled"] += 1
                                        allteamstats[eachteam]["totalextras"] += eachball['extras']['legbyes']
                                if "wickets" in eachball:
                                    for eachwicket in eachball["wickets"]:
                                        allteamstats[eachteam]["inningswickets"] += 1
                                        allteamstats[eachteam]["Wickets"] += 1
                                        if eachwicket["kind"] == "caught":
                                            allteamstats[eachteam]["totalcaughts"] += 1
                                        if eachwicket["kind"] == "stumped":
                                            allteamstats[eachteam]["totalstumpeds"] += 1
                                        if eachwicket["kind"] == "run out":
                                            allteamstats[eachteam]["totalrunouts"] += 1

                        # Non-striker outs and fielding stats
                        if "wickets" in eachball:
                            for eachwicket in eachball["wickets"]:
                                if eachball["non_striker"] in players and eachball['non_striker'] == eachwicket["player_out"]:
                                    allplayerstats[eachball['non_striker']
                                                   ]["Outs"] += 1

                                if "fielders" in eachwicket:
                                    for eachfielder in eachwicket["fielders"]:
                                        if "name" not in eachfielder:
                                            continue
                                        if eachfielder["name"] in players:
                                            if eachwicket["kind"] == "caught":
                                                allplayerstats[eachfielder["name"]
                                                               ]["totalcatches"] += 1
                                            if eachwicket["kind"] == "stumped":
                                                allplayerstats[eachfielder["name"]
                                                               ]["totalstumpings"] += 1
                                            if eachwicket["kind"] == "run out":
                                                allplayerstats[eachfielder["name"]
                                                               ]["totalrunouts"] += 1
                # List of Team scores.
                if eachinnings["team"] in teams:
                    allteamstats[eachinnings["team"]]["All Scores"].append(
                        sum(allteamstats[eachinnings["team"]]["inningsruns"]))
                    allteamstats[eachinnings["team"]]["All Outs"].append(
                        allteamstats[eachinnings["team"]]["inningsouts"])
                    allteamstats[eachinnings["team"]]["All Overs Faced"].append(
                        round(allteamstats[eachinnings["team"]]["inningsballsfaced"] / 6))
                    if nthinnings == 0:
                        allteamstats[eachinnings["team"]]["1st Innings Scores"].append(
                            sum(allteamstats[eachinnings["team"]]["inningsruns"]))
                    if nthinnings == 1:
                        allteamstats[eachinnings["team"]]["2nd Innings Scores"].append(
                            sum(allteamstats[eachinnings["team"]]["inningsruns"]))
                    if nthinnings == 2:
                        allteamstats[eachinnings["team"]]["3rd Innings Scores"].append(
                            sum(allteamstats[eachinnings["team"]]["inningsruns"]))
                    if nthinnings == 3:
                        allteamstats[eachinnings["team"]]["4th Innings Scores"].append(
                            sum(allteamstats[eachinnings["team"]]["inningsruns"]))
                for eachteam in match["info"]["teams"]:
                    if eachteam in teams and eachteam not in eachinnings["team"]:
                        allteamstats[eachteam]["All Runsgiven"].append(
                            sum(allteamstats[eachteam]["inningsrunsgiven"]))
                        allteamstats[eachteam]["All Wickets"].append(
                            allteamstats[eachteam]["inningswickets"])
                        allteamstats[eachteam]["All Overs Bowled"].append(
                            round(allteamstats[eachteam]["inningsballsbowled"] / 6))
                        if nthinnings == 0:
                            allteamstats[eachteam]["1st Innings Wickets"].append(
                                allteamstats[eachteam]["inningswickets"])
                        if nthinnings == 1:
                            allteamstats[eachteam]["2nd Innings Wickets"].append(
                                allteamstats[eachteam]["inningswickets"])
                        if nthinnings == 2:
                            allteamstats[eachteam]["3rd Innings Wickets"].append(
                                allteamstats[eachteam]["inningswickets"])
                        if nthinnings == 3:
                            allteamstats[eachteam]["4th Innings Wickets"].append(
                                allteamstats[eachteam]["inningswickets"])

                if players:
                    for eachplayer in allplayerstats:
                        if allplayerstats[eachplayer]["inningsballsfaced"] > 0:
                            allplayerstats[eachplayer]["All Scores"].append(
                                sum(allplayerstats[eachplayer]["inningsruns"]))
                            allplayerstats[eachplayer]["All Balls Faced"].append(
                                allplayerstats[eachplayer]["inningsballsfaced"])
                        if allplayerstats[eachplayer]["inningsballsbowled"] > 0:
                            allplayerstats[eachplayer]["All Runsgiven"].append(
                                sum(allplayerstats[eachplayer]["inningsrunsgiven"]))
                            allplayerstats[eachplayer]["All Wickets"].append(
                                allplayerstats[eachplayer]["inningswickets"])
                            allplayerstats[eachplayer]["All Overs Bowled"].append(
                                round(allplayerstats[eachplayer]["inningsballsbowled"] / 6))

                # Recording successfully defended and chased scores.
                if 'result' not in match['info']['outcome'] and match['info']['outcome']["winner"] in teams:
                    if 'runs' in match['info']['outcome']['by']:
                        if "target" in match['innings'][1]:
                            allteamstats[match['info']['outcome']["winner"]]["Defended Scores"].append(
                                match['innings'][1]['target']['runs'] - 1)
                        if nthinnings == (len(match['innings']) - 1) and match['info']['outcome']["winner"] != eachinnings["team"]:
                            allteamstats[match['info']['outcome']["winner"]]["Defended Scores"].append(
                                (sum(
                                    allteamstats[match['info']['outcome']["winner"]]["inningsrunsgiven"]))
                                + match['info']['outcome']['by']['runs'])
                        allteamstats[match['info']['outcome']["winner"]]["runmargins"].append(
                            match['info']['outcome']['by']['runs'])
                    if 'wickets' in match['info']['outcome']['by']:
                        if "target" in match['innings'][1]:
                            allteamstats[match['info']['outcome']["winner"]]["Chased Scores"].append(
                                match['innings'][1]['target']['runs'])
                            allteamstats[match['info']['outcome']["winner"]]["overschased"].append(
                                round(allteamstats[match['info']['outcome']["winner"]]["inningsballsfaced"] / 6))
                        if nthinnings == (len(match['innings']) - 1) and match['info']['outcome']["winner"] == eachinnings["team"]:
                            allteamstats[match['info']['outcome']["winner"]]["Chased Scores"].append(
                                (sum(allteamstats[match['info']['outcome']["winner"]]["inningsruns"])))
                            allteamstats[match['info']['outcome']["winner"]]["overschased"].append(
                                round(allteamstats[match['info']['outcome']["winner"]]["inningsballsfaced"] / 6))
                        allteamstats[match['info']['outcome']["winner"]]["wicketmargins"].append(
                            match['info']['outcome']['by']['wickets'])

            matchdata.close()
    matches.close()

    # Derived Stats
    if players:
        for eachplayer in allplayerstats:
            if allplayerstats[eachplayer]["Caps"] > 0:
                allplayerstats[eachplayer]["Win %"] = statsprocessor.ratio(allplayerstats[eachplayer]["Won"],
                                                                           allplayerstats[eachplayer]["Caps"],
                                                                           multiplier=100)

            if allplayerstats[eachplayer]["Balls Faced"] > 0 and allplayerstats[eachplayer]["Runs"] > 0:
                allplayerstats[eachplayer]["Strike Rate"] = statsprocessor.ratio(allplayerstats[eachplayer]["Runs"],
                                                                                 allplayerstats[eachplayer][
                                                                                     "Balls Faced"], multiplier=100)
                allplayerstats[eachplayer]["Boundary %"] = statsprocessor.ratio(
                    (allplayerstats[eachplayer]["Fours"]
                     + allplayerstats[eachplayer]["Sixes"]),
                    allplayerstats[eachplayer]["Balls Faced"], multiplier=100)
                allplayerstats[eachplayer]["Dot Ball %"] = statsprocessor.ratio(allplayerstats[eachplayer]["Dot Balls"],
                                                                                allplayerstats[eachplayer][
                                                                                    "Balls Faced"], multiplier=100)
                allplayerstats[eachplayer]["Strike Turnover %"] = statsprocessor.ratio(
                    allplayerstats[eachplayer]["totalstos"], allplayerstats[eachplayer]["totalstosopp"], multiplier=100)
                allplayerstats[eachplayer]["Strike Rate MeanAD"] = statsprocessor.madfromlist(
                    allplayerstats[eachplayer]["All Scores"], allplayerstats[eachplayer]["All Balls Faced"], stattype="percent")

            if allplayerstats[eachplayer]["Outs"] > 0:
                allplayerstats[eachplayer]["Average"] = statsprocessor.ratio(allplayerstats[eachplayer]["Runs"],
                                                                             allplayerstats[eachplayer]["Outs"],
                                                                             multiplier=0)

            if allplayerstats[eachplayer]["Balls Bowled"] > 0:
                allplayerstats[eachplayer]["Economy Rate"] = statsprocessor.ratio(
                    allplayerstats[eachplayer]["totalrunsgiven"], allplayerstats[eachplayer]["Balls Bowled"],
                    multiplier=6)
                allplayerstats[eachplayer]["Economy Rate MeanAD"] = statsprocessor.madfromlist(
                    allplayerstats[eachplayer]["All Runsgiven"], allplayerstats[eachplayer]["All Balls Faced"], stattype="perover")
                allplayerstats[eachplayer]["Dot Ball Bowled %"] = statsprocessor.ratio(
                    allplayerstats[eachplayer]["totaldotballsbowled"], allplayerstats[eachplayer]["Balls Bowled"],
                    multiplier=100)
                allplayerstats[eachplayer]["Boundary Given %"] = statsprocessor.ratio(
                    (allplayerstats[eachplayer]["totalfoursgiven"]
                     + allplayerstats[eachplayer]["totalsixesgiven"]),
                    allplayerstats[eachplayer]["Balls Bowled"], multiplier=100)

            if allplayerstats[eachplayer]["Wickets"] > 0:
                allplayerstats[eachplayer]["Bowling Avg"] = statsprocessor.ratio(
                    allplayerstats[eachplayer]["totalrunsgiven"], allplayerstats[eachplayer]["Wickets"], multiplier=0)
                allplayerstats[eachplayer]["Bowling SR"] = statsprocessor.ratio(
                    allplayerstats[eachplayer]["Balls Bowled"], allplayerstats[eachplayer]["Wickets"], multiplier=0)
    if players:
        df = pd.DataFrame(allplayerstats)
        allplayerstatsdf = df.transpose()
        return allplayerstatsdf
    elif teams:
        df = pd.DataFrame(allteamstats)
        allteamstatsdf = df.transpose()
        return allteamstatsdf
