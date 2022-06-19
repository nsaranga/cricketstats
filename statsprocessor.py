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

# Stats Processor functions

def ratio(stat1, stat2, multiplier=None):
    stat = None
    if multiplier and stat2 != 0:
        stat = round(((stat1 / stat2) * multiplier), 2)
    if not multiplier and stat2 != 0:
        stat = round((stat1 / stat2), 2)
    return stat


# def madfromratio(statlist1, statlist2, multiplier=None):
#     data = []
#     for eachlist in zip(statlist1, statlist2):
#         statratio = ratio(eachlist[0], eachlist[1], multiplier=multiplier)
#         data.append(statratio)
#     df = pd.DataFrame(data)
#     stat = df[0].mad()
#     return round(stat, 2)


# def mad(statlist):
#     data = statlist
#     df = pd.DataFrame(data)
#     stat = df[0].mad()
#     return round(stat, 2)


def firstboundary(shotlist):
    four = None
    six = None
    if 4 in shotlist:
        four = (shotlist.index(4)+1)
    if 6 in shotlist:
        six = (shotlist.index(6)+1)
    if four and not six:
        return four
    if not four and six:
        return six
    if four and six:
        if four <= six:
            return four
        elif six <= four:
            return six
    if not four and not six:
        return 0

def dotballseries(balllist):
    dotballs = []
    dotballlist = []
    dotballseries = []
    for nth, eachball in enumerate(balllist):
        if eachball == 0:
            dotballs.append(eachball)
            if nth == (len(balllist) - 1):
                dotballlist.append(dotballs)
        if eachball != 0 and dotballs:
            dotballlist.append(dotballs)
            dotballs = []

    for eachlist in dotballlist:
        dotballseries.append(len(eachlist))
    return dotballseries
