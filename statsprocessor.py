import pandas as pd


# Stats Processor functions

def ratio(stat1, stat2, multiplier=None):
    stat = None
    if multiplier:
        stat = round(((stat1 / stat2) * multiplier), 2)
    if not multiplier:
        stat = round((stat1 / stat2), 2)
    return stat


def madfromlist(statlist1, statlist2, stattype=False):
    data = []
    for eachlist in zip(statlist1, statlist2):
        if stattype == "percent":
            percent = ratio(eachlist[0], eachlist[1], multiplier=100)
            data.append(percent)
        if stattype == "perover":
            perover = ratio(eachlist[0], eachlist[1], multiplier=6)
            data.append(perover)
    df = pd.DataFrame(data)
    stat = df[0].mad()
    return round(stat, 2)


def mad(statlist):
    df = pd.DataFrame(statlist)
    stat = df.mad()
    return round(stat, 2)


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
