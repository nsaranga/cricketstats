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
