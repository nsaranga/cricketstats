# cricketstats
A python module which gets team and player statistics from the [cricsheet.org](https://cricsheet.org/) database for data analysis and analytics projects in cricket.

**If you want to try this module out [CLICK HERE](https://cricanalyst.anivaasi.net/) to use a web implementation of it by Sudarshan Narayana**

If you have any questions about the module you can contact me on [Twitter](https://www.twitter.com/humesfinger/), email me at [nsaranga@hotmail.com](mailto:nsaranga@hotmail.com). If you have any bugs to report or features to suggest you can use raise ticket on the issues tab in github. If you want to know more about why I decided to write it you can find a blog post [here](https://nsaranga.github.io/cricket/2021/12/19/TheAimOfCricketstats/), and if you want to know more about what the module can actually you do you can read another blog post [here](https://nsaranga.github.io/cricket/2021/12/24/WhatCanCricketstatsDo/) 

Some tips/warnings: 
1. Python packages this module requires: datetime, json, time, pandas, os, zipfile, numpy, math, importlib, matplotlib
2. There will be bugs as this is my first python project. I'm still learning the language and programming in general.
3. At its core the script is as good as the data, so output will depend on how quickly the data is updated on cricsheet and its accuracy.
4. I recommend downloading and using the "all_json.zip" from cricsheet as the database.
5. The first time you run this script it will take about 30-40 seconds because it is indexing file names, after that each search should take 6-7 seconds to complete. This of course will vary based on your CPU.

## What can this module do?
### Features:
- Analyse players/teams across finegrained parameters.
- Analyse matchups of player/team against particular players/teams or a group eg. by bowling style, batter handedness.
- Analyse the progression players/team performance across innings.
- Analyse distributions of stats according to innings, to create predictive models of player and team performance.
- Analyse the game itself according to all players or teams in given time period, match type (ie. a reverse lookup)

This is essentially a module you can import into any python script to collect statistics from cricsheet json files.

This script can find team and player statistics along any of the following parameters: date interval, match type, overs interval, innings, opposition players, opposition teams, venue, event, match result, batting position and more.

The script can then find the following stats for players and teams: games played, wins played in, draws played in, win %, Innings played in, Scores/Figures in each innings, Runs, Fours, Sixes, Outs(with breakdown of all kinds of dismissal), Wickets taken (with breakdown of all kinds of dismissal), catches taken as fielder, Strike Turnover %, Batting and Bowling strike rate, average, economy rate, Batting and Bowling Boundary %, Batting and Bowling Dot ball %, Score and Strike rate mean absolute deviation, net run rate, net boundary %, Successfully Defended and Chased scores, and more.

Also using the in built-in playerindex you can find matchup data for a player against certain types of batters (eg. Right or Left Hand) and bowlers (eg. Right arm pace, Left arm pace, Right arm Off break, Right arm Leg break, Left arm orthodox and Left arm wrist spin).

As shown in the example.py file using "print(search1.result.columns)" will print all the available stats for a particular search.

## How do you use this module?:
 All you need to do is import cricketstats in any python script create a search object, call the "stats()" function with the necessary arguments for that search object and run the script through python3. The output of the function is a Pandas DataFrame that can be printed, analysed using pandas methods or served as the input to plotting methods like matplotlib.

To understand how to use the module you can use the "example.py" which provides a simple example.

## To Do:
- Clean up stats independent of checks with stats dependent on checks.
- Command-line wrapper
- Expected runs model? Basically sum of weighted average of runs per ball * average innings length. Something along the lines of pythagorean thing.
- Index more things?, so they can serve as lists for seeing what teams there are in a comp. Venues by country also put in checks when values are null.
- Let us know all the possibilities we can expect within result method for plotting (ie. loc?)
- Arguments via a dict? dicts should be defined in a separate file
- eachball will read better as this(?)ball (same for eachwicket and others)
- Use "matchcase" in multiple if-conditions for the same variable
- Release as PyPi module that can be installed via pip