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
import json

import pandas as pd
import math
import requests
from bs4 import BeautifulSoup

def index(playerdatabase):
    currentdir = os.path.dirname(os.path.abspath(__file__))
    try:
        playerindexfile = open(f"{currentdir}/playerindex.json")
        players = json.load(playerindexfile)
        # players = playerindex.players
        playerlist = pd.read_csv(playerdatabase)
        for eachplayer in playerlist["name"]:
            if (eachplayer in players["Batting"]["Right hand"] or eachplayer in players["Batting"]["Left hand"]) and (eachplayer in players["Bowling"]["Right arm pace"] or eachplayer in players["Bowling"]["Left arm pace"] or eachplayer in players["Bowling"]["Right arm Off break"] or eachplayer in players["Bowling"]["Right arm Leg break"] or eachplayer in players["Bowling"]["Left arm orthodox"] or eachplayer in players["Bowling"]["Left arm wrist spin"]) or eachplayer in players["Umpire"]:
                continue
            playerdata = playerlist.loc[playerlist["name"]==f"{eachplayer}", ["key_cricinfo"]]
            if math.isnan(playerdata.at[playerdata.index[0], "key_cricinfo"]):
                continue
            playerid = math.floor(playerdata.at[playerdata.index[0], "key_cricinfo"])
            print(eachplayer + ", "+ f"https://www.espncricinfo.com/*/content/player/{playerid}.html")
            webpage = requests.get(f"https://www.espncricinfo.com/*/content/player/{playerid}.html")
            playerpage = BeautifulSoup(webpage.content, "html.parser")
            main = playerpage.find(id="main-container")
            if main is None:
                continue
            playerinfo = main.find_all("h5", class_="player-card-description gray-900")
            for element in playerinfo:
                # Batting
                if "Right hand bat" in element.text:
                    players["Batting"]["Right hand"].append(eachplayer)            
                if "Left hand bat" in element.text:
                    players["Batting"]["Left hand"].append(eachplayer)
                
                # Bowling
                if "Right arm fast" in element.text or "Right arm fast medium" in element.text  or "Right arm medium" in element.text:
                    players["Bowling"]["Right arm pace"].append(eachplayer)
                if "Left arm fast" in element.text or "Left arm fast medium" in element.text  or "Left arm medium" in element.text:
                    players["Bowling"]["Left arm pace"].append(eachplayer)

                if "offbreak" in element.text:
                    players["Bowling"]["Right arm Off break"].append(eachplayer)
                if "Legbreak" in element.text:
                    players["Bowling"]["Right arm Leg break"].append(eachplayer)
                if "Slow left arm orthodox" in element.text:
                    players["Bowling"]["Left arm orthodox"].append(eachplayer)
                if "Left arm wrist spin" in element.text or "Left-arm googly" in element.text:
                    players["Bowling"]["Left arm wrist spin"].append(eachplayer)
                
                # Umpire
                if "Umpire" in element.text:
                    players["Umpire"].append(eachplayer)

                if "Right hand bat" not in element.text and "Left hand bat" not in element.text and "Right arm fast" not in element.text and "Right arm fast medium" not in element.text  and "Right arm medium" not in element.text and "Left arm fast" not in element.text and "Left arm fast medium" not in element.text  and "Left arm medium" not in element.text and "Legbreak" not in element.text and "Slow left arm orthodox" not in element.text and "Left arm wrist spin" not in element.text and "Left-arm googly" not in element.text:
                    players["Unknown"].append(eachplayer)
                playerindexfile.close()
    finally:
        file = open(f"{currentdir}/playerindex.json", "w")
        file.write(json.dumps(players))
        file.close