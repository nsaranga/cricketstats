import pandas as pd, matplotlib.pyplot as plt, getstats


Ozbowlers = ["PJ Cummins", "JR Hazlewood", "MA Starc", "JA Richardson", "A Zampa", "AC Agar", "NT Ellis", "MP Stoinis",
             "MR Marsh", "MJ Swepson", "MG Neser","NM Lyon", "CD Green"]
Ozbatters = ["DA Warner", "SPD Smith", "MR Marsh", "GJ Maxwell", "MP Stoinis", "MS Wade", "JP Inglis", "M Labuschagne", "UT Khawaja", "TM Head", "MS Harris", "CD Green", "TD Paine"]
playerscompresult = getstats.getstats("/home/saranga/Documents/cricketstatsproject/data/all/", (2021, 4, 1), (2021, 12, 1), betweenovers=[1, 60], players=Ozbatters, matchtype=["MDM", "Test"])

# gettats arguments.  sex=[], teams=[], opposition=[], venue=[], event=[], matchtype=[], matchresult=""


# Stats Comparison

df = pd.DataFrame(playerscompresult)
playerscompresultdf = df.transpose()
# df.to_csv("./pandasoutput.csv")

# playerscompresultdf["All Scores"]=playerscompresultdf["All Scores"].astype(float)
# print(playerscompresultdf.loc["Australia", ["Chased Scores", "overschased"]])
# print(playerscompresultdf["All Scores"])
# playerscompresultdf.explode("All Scores")

# print(playerscompresultdf.sort_values(by="Boundary Given %", ascending=False)[["Boundary Given %", "Dot Ball Bowled %", "Balls Bowled"]])
# df.style.set_table_attributes("style='display:inline'").set_caption('Caption table')
print(playerscompresultdf[["Average", "Boundary %", "Strike Rate","Strike Rate MeanAD","Balls Faced"]])

# print(playerscompresultdf.loc["SPD Smith","Average"])
# print(playerscompresultdf[["Boundary Given %", "Economy Rate","Economy Rate MeanAD"]])

# Plotting

# df=playerscompresultdf.loc["Australia", "All Scores"]

# playerscompresultdf.loc["Australia", "All Scores"].plot(kind="hist", fontsize=8)
# plt.scatter(x=playerscompresultdf.loc["Australia", "All Scores"], y=playerscompresultdf.loc["Australia", "All Outs"],)

# playerscompresultdf.sort_values(by="Boundary Given %", ascending=False)[["Boundary Given %", "Dot Ball Bowled %", "Balls Bowled"]].plot(kind="bar", rot=15, fontsize=8, secondary_y="Balls Bowled")

# playerscompresultdf.sort_values(by="Boundary %", ascending=False)[["Boundary %", "Dot Ball %", "Balls Faced"]].plot(kind="bar", rot=15, fontsize=8, secondary_y="Balls Faced", title="Overs 1-20 in all T20s since start of 2018")
# plt.grid(axis = 'y')
plt.legend()
# plt.title("source: cricsheet.org", fontsize=10)
plt.show()
