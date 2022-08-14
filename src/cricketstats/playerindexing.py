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
        #indexfile = open(f"{currentdir}/playerindex.csv")
        playerindex= pd.read_csv(f"{currentdir}/playerindex.csv")
        playerlist = pd.read_csv(playerdatabase)
        newplayers = {"Player":[],"Batting":[],"Bowling":[],"Umpire":[]}
    else:
        playerlist = pd.read_csv(playerdatabase)
        playerindex= pd.read_csv(playerindexfile)
        newplayers = {"Player":[],"Batting":[],"Bowling":[],"Umpire":[]}
    try:
        for eachplayer in playerlist["name"]:
            if eachplayer in playerindex["Player"] and pd.notna(playerindex.at[playerindex.loc[playerindex["Player"]==eachplayer].index[0],"Batting"]) and pd.notna(playerindex.at[playerindex.loc[playerindex["Player"]==eachplayer].index[0],"Bowling"]):
                continue

            #playerdata = playerlist.loc[playerlist["name"]==f"{eachplayer}", ["key_cricinfo"]]
            if pd.isna(playerlist.at[playerlist.loc[playerlist["name"]==f"{eachplayer}"].index[0], "key_cricinfo"]):
                continue
            playerid = math.floor(playerlist.at[playerlist.loc[playerlist["name"]==f"{eachplayer}"].index[0], "key_cricinfo"])
            print(eachplayer + ", "+ f"https://www.espncricinfo.com/*/content/player/{playerid}.html")
            webpage = requests.get(f"https://www.espncricinfo.com/*/content/player/{playerid}.html")
            playerpage = BeautifulSoup(webpage.content, "html.parser")
            main = playerpage.find(id="main-container")
            if main is None:
                continue
            playerinfo = main.find_all("h5", class_="player-card-description gray-900")
            for element in playerinfo:
                if eachplayer not in playerindex["Player"] and ("Right hand bat" in element.text or "Left hand bat" in element.text or "Umpire" in element.text):
                    newplayers["Player"].append(eachplayer)
                    newplayers["Batting"].append(None)
                    newplayers["Bowling"].append(None)
                    newplayers["Umpire"].append("No")
                    

                # Batting
                if "Right hand bat" in element.text:
                    if eachplayer in playerindex["Player"] and pd.isna(playerindex.at[playerindex.loc[playerindex["Player"]==eachplayer].index[0],"Batting"]):
                        playerindex.at[playerindex.loc[playerindex["Player"]==eachplayer].index[0],"Batting"]="Right hand"
                    if eachplayer not in playerindex["Player"]:
                        newplayers["Batting"][newplayers["Player"].index(eachplayer)]="Right hand"

                if "Left hand bat" in element.text:
                    if eachplayer in playerindex["Player"] and pd.isna(playerindex.at[playerindex.loc[playerindex["Player"]==eachplayer].index[0],"Batting"]):
                        playerindex.at[playerindex.loc[playerindex["Player"]==eachplayer].index[0],"Batting"]="Left hand"
                    if eachplayer not in playerindex["Player"]:
                        newplayers["Batting"][newplayers["Player"].index(eachplayer)]="Left hand"
                
                # Bowling
                if "Right arm fast" in element.text or "Right arm fast medium" in element.text  or "Right arm medium" in element.text:
                    if eachplayer in playerindex["Player"] and pd.isna(playerindex.at[playerindex.loc[playerindex["Player"]==eachplayer].index[0],"Bowling"]):
                        playerindex.at[playerindex.loc[playerindex["Player"]==eachplayer].index[0],"Bowling"]="Right arm pace"

                    if eachplayer not in playerindex["Player"]:
                        newplayers["Bowling"][newplayers["Player"].index(eachplayer)]="Right arm pace"
                if "Left arm fast" in element.text or "Left arm fast medium" in element.text  or "Left arm medium" in element.text:
                    if eachplayer in playerindex["Player"] and pd.isna(playerindex.at[playerindex.loc[playerindex["Player"]==eachplayer].index[0],"Bowling"]):
                        playerindex.at[playerindex.loc[playerindex["Player"]==eachplayer].index[0],"Bowling"]="Left arm pace"
                    if eachplayer not in playerindex["Player"]:
                        newplayers["Bowling"][newplayers["Player"].index(eachplayer)]="Left arm pace"

                if "offbreak" in element.text:
                    
                    if eachplayer in playerindex["Player"] and pd.isna(playerindex.at[playerindex.loc[playerindex["Player"]==eachplayer].index[0],"Bowling"]):
                        playerindex.at[playerindex.loc[playerindex["Player"]==eachplayer].index[0],"Bowling"]="Right arm off break"
                    if eachplayer not in playerindex["Player"]:
                        newplayers["Bowling"][newplayers["Player"].index(eachplayer)]="Right arm off break"
                if "Legbreak" in element.text:
                    if eachplayer in playerindex["Player"] and pd.isna(playerindex.at[playerindex.loc[playerindex["Player"]==eachplayer].index[0],"Bowling"]):
                        playerindex.at[playerindex.loc[playerindex["Player"]==eachplayer].index[0],"Bowling"]="Right arm leg break"
                    if eachplayer not in playerindex["Player"]:
                        newplayers["Bowling"][newplayers["Player"].index(eachplayer)]="Right arm leg break"
                    
                if "Slow left arm orthodox" in element.text:
                    if eachplayer in playerindex["Player"] and pd.isna(playerindex.at[playerindex.loc[playerindex["Player"]==eachplayer].index[0],"Bowling"]):
                        playerindex.at[playerindex.loc[playerindex["Player"]==eachplayer].index[0],"Bowling"]="Left arm orthodox"
                    if eachplayer not in playerindex["Player"]:
                        newplayers["Bowling"][newplayers["Player"].index(eachplayer)]="Left arm orthodox"
                    #newplayers["Bowling"]["Left arm orthodox"].append(eachplayer)

                if "Left arm wrist spin" in element.text or "Left-arm googly" in element.text:
                    #newplayers["Bowling"]["Left arm wrist spin"].append(eachplayer)
                    if eachplayer in playerindex["Player"] and pd.isna(playerindex.at[playerindex.loc[playerindex["Player"]==eachplayer].index[0],"Bowling"]):
                        playerindex.at[playerindex.loc[playerindex["Player"]==eachplayer].index[0],"Bowling"]="Left arm wrist spin"
                    if eachplayer not in playerindex["Player"]:
                        newplayers["Bowling"][newplayers["Player"].index(eachplayer)]="Left arm wrist spin"
                # Umpire
                if "Umpire" in element.text:
                    #newplayers["Umpire"].append(eachplayer)
                    if eachplayer in playerindex["Player"] and playerindex.at[playerindex.loc[playerindex["Player"]==eachplayer].index[0],"Umpire"]==False:
                        playerindex.at[playerindex.loc[playerindex["Player"]==eachplayer].index[0],"Umpire"]="Yes"
                    if eachplayer not in playerindex["Player"]:
                        newplayers["Umpire"][newplayers["Player"].index(eachplayer)]="Yes"

    finally:
        newplayersdf = pd.DataFrame(newplayers)
        df=pd.concat([playerindex,newplayersdf],ignore_index=True)
        if playerindexfile==None:
            df.to_csv(f"{currentdir}/playerindex.csv",index=False)
        if playerindexfile!=None:
            df.to_csv(playerindexfile,index=False)

