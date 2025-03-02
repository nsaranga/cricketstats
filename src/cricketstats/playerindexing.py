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

# def playersearch(player):
#     currentdir = os.path.dirname(os.path.abspath(__file__))
#     playerindexfile = open(f"{currentdir}/playerindex.json")
#     playerindex = json.load(playerindexfile)
#     result = {"Player":[],"Batting":[],"Bowling":[]}
#     for eachlist in playerindex["Batting"]:
#         for eachitem in playerindex["Batting"][eachlist]:
#             if player in eachitem and eachitem not in result["Player"]:
#                 result["Player"].append(eachitem)
#                 result["Batting"].append(eachlist)
#     playerfound=False
#     for eachplayer in result["Player"]:
#         result["Bowling"].append(None)
#         for eachlist in playerindex["Bowling"]:
#         #for eachitem in playerindex["Bowling"][eachlist]:
#             if eachplayer in playerindex["Bowling"][eachlist]:
#                 result["Bowling"][result["Player"].index(eachplayer)]=eachlist
#     print(len(result["Player"]))
#     print(len(result["Batting"]))
#     print(len(result["Bowling"]))
#     df = pd.DataFrame(result)
#     return df

def index(playerdatabase,playerindexfile=None):
    if playerindexfile==None:
        currentdir = os.path.dirname(os.path.abspath(__file__))
        if os.path.exists(f"{currentdir}/playerindex.json"):
            indexfile = open(f"{currentdir}/playerindex.json")
            playerindex = json.load(indexfile)
        else:
            playerindex = {}
        
        playerlist = pd.read_csv(playerdatabase)
        newplayers = {}
        #{"Batting":None,"Bowling":None,"Umpire":"No"}
    if playerindexfile!=None:
        playerlist = pd.read_csv(playerdatabase)
        indexfile = open(playerindexfile)
        playerindex = json.load(indexfile)
        newplayers = {}
        #"Player":[],"Batting":[],"Bowling":[],"Umpire":"No"}
    try:
        for eachplayer in playerlist["name"]:
            if eachplayer in playerindex.keys() and playerindex[eachplayer]["Batting"]!=None and playerindex[eachplayer]["Bowling"]!=None:
                continue

            #playerdata = playerlist.loc[playerlist["name"]==f"{eachplayer}", ["key_cricinfo"]]
            if pd.isna(playerlist.at[playerlist.loc[playerlist["name"]==f"{eachplayer}"].index[0], "key_cricinfo"]):
                continue
            playerid = math.floor(playerlist.at[playerlist.loc[playerlist["name"]==f"{eachplayer}"].index[0], "key_cricinfo"])
            print(eachplayer + ", "+ f"https://www.espncricinfo.com/*/content/player/{playerid}.html")
            webpage = requests.get(f"https://www.espncricinfo.com/*/content/player/{playerid}.html",headers={"User-Agent":"Mozilla/5.0"})
            playerpage = BeautifulSoup(webpage.content, "html.parser")
            playerinfo = playerpage.find(id="main-container")
            if playerinfo is None:
                continue
            # playerinfo = main.find_all("h5", class_="player-card-description gray-900")
            allinfo =playerinfo.find(string="Full Name").find_parent().find_parent().find_parent()
            if eachplayer not in playerindex.keys() and ("Batting Style" in allinfo.text or "Bowling Style" in allinfo.text or "Umpire" in allinfo.text):
                playerindex[eachplayer]={"Batting":None,"Bowling":None,"Umpire":None}
                # print('player not in index')

            # Batting            
            if "Batting Style" in allinfo.text and playerindex[eachplayer]["Batting"]==None:
                if "Right hand Bat" in allinfo.text:
                    playerindex[eachplayer]["Batting"]="Right hand"
                if "Left hand Bat" in allinfo.text:
                    playerindex[eachplayer]["Batting"]="Left hand"

            # Bowling
            if "Bowling Style" in allinfo.text and playerindex[eachplayer]["Bowling"]==None:
                if ("Right arm Fast" in allinfo.text or "Right arm Fast medium" in allinfo.text  or "Right arm Medium" in allinfo.text):
                    playerindex[eachplayer]["Bowling"]="Right arm pace"
                if ("Left arm Fast" in allinfo.text or "Left arm Fast medium" in allinfo.text  or "Left arm Medium" in allinfo.text):
                    playerindex[eachplayer]["Bowling"]="Left arm pace"

                if "Offbreak" in allinfo.text:
                    playerindex[eachplayer]["Bowling"]="Right arm off break"
                if "Legbreak" in allinfo.text:
                    playerindex[eachplayer]["Bowling"]="Right arm leg break"
                    
                if "Slow Left arm Orthodox" in allinfo.text:
                    playerindex[eachplayer]["Bowling"]="Left arm orthodox"

                if ("Left arm Wrist spin" in allinfo.text or "Left-arm googly" in allinfo.text):
                    playerindex[eachplayer]["Bowling"]="Left arm wrist spin"

            # Umpire
            if "Umpire" in allinfo.text and (playerindex[eachplayer]["Umpire"]==None or playerindex[eachplayer]["Umpire"]=="No"):
                playerindex[eachplayer]["Umpire"]="Yes"

            # for element in playerinfo:
            #     if eachplayer not in playerindex.keys() and ("Right hand Bat" in element.text or "Left hand Bat" in element.text or "Umpire" in element.text):
            #         playerindex[eachplayer]={"Batting":None,"Bowling":None,"Umpire":None}
            #         print('player not in index')

            #     # Batting
            #     if "Right hand Bat" in element.text and playerindex[eachplayer]["Batting"]==None:
            #         playerindex[eachplayer]["Batting"]="Right hand bat"

            #     if "Left hand Bat" in element.text and playerindex[eachplayer]["Batting"]==None:
            #         playerindex[eachplayer]["Batting"]="Left hand bat"
                
            #     # Bowling
            #     if ("Right arm Fast" in element.text or "Right arm Fast medium" in element.text  or "Right arm Medium" in element.text) and playerindex[eachplayer]["Bowling"]==None:
            #         playerindex[eachplayer]["Bowling"]="Right arm pace"

            #     if ("Left arm Fast" in element.text or "Left arm Fast medium" in element.text  or "Left arm Medium" in element.text) and playerindex[eachplayer]["Bowling"]==None:
            #         playerindex[eachplayer]["Bowling"]="Left arm pace"

            #     if "Offbreak" in element.text and playerindex[eachplayer]["Bowling"]==None:
            #         playerindex[eachplayer]["Bowling"]="Right arm off break"
            #     if "Legbreak" in element.text and playerindex[eachplayer]["Bowling"]==None:
            #         playerindex[eachplayer]["Bowling"]="Right arm leg break"
                    
            #     if "Slow Left arm Orthodox" in element.text and playerindex[eachplayer]["Bowling"]==None:
            #         playerindex[eachplayer]["Bowling"]="Left arm orthodox"

            #     if ("Left arm Wrist spin" in element.text or "Left-arm googly" in element.text) and playerindex[eachplayer]["Bowling"]==None:
            #         playerindex[eachplayer]["Bowling"]="Left arm wrist spin"
            #     # Umpire
            #     if "Umpire" in element.text and (playerindex[eachplayer]["Umpire"]==None or playerindex[eachplayer]["Umpire"]=="No"):
            #         playerindex[eachplayer]["Umpire"]="Yes"
    finally:
        if os.path.exists(f"{currentdir}/playerindex.json"):
            indexfile.close()
        if playerindexfile==None:
            # print(playerindex)
            file = open(f"{currentdir}/playerindex.json", "w")
            file.write(json.dumps(playerindex))
            file.close()
        if playerindexfile!=None:
            file = open(playerindexfile, "w")
            file.write(json.dumps(playerindex))
            file.close()
    
