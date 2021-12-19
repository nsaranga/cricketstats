# cricketstats
A python module which gets team and player statistics from the [cricsheet.org](https://cricsheet.org/) database for data analysis and analytics projects in cricket.

If you have any questions about the module you can contact me on [Twitter](https://www.twitter.com/humesfinger/), email me at [nsaranga@hotmail.com](mailto:nsaranga@hotmail.com). If you have any bugs to report or features to suggest you can use raise ticket on the issues tab in github. If you want to know more about why I decide to write it you can find blog post [here](https://nsaranga.github.io/cricket/2021/12/19/TheAimOfCricketstats.html).

Some tips/warnings: 
1. There will be bugs as this is my first python project. I'm still learning the language and programming in general.
2. At its core the script is as good as the data, so output will depend on how quickly the data is updated on cricsheet and its accuracy.
3. I recommend downloading and using the "all_json.zip" from cricsheet as the database.
4. The first time you run this script it will take about 30-40 seconds because it is indexing file names, after that each search should take 6-7 seconds to complete. This of course will vary based on your CPU.

## What can this script do?
This is essentially a module you can import into any python script to collect statistics from cricsheet json files.

This script can find team and player statistics along any of the following parameters: date interval, match type, overs interval, innings, opposition players, opposition teams, venue, event, match result, batting position and more.

The script can then find the following stats for players and teams: games played, wins played in, draws played in, win %, Innings played in, Scores/Figures in each innings, Runs, Fours, Sixes, Outs(with breakdown of all kinds of dismissal), Wickets taken (with breakdown of all kinds of dismissal), catches taken as fielder, Strike Turnover %, Batting and Bowling strike rate, average, economy rate, Batting and Bowling Boundary %, Batting and Bowling Dot ball %, Score and Strike rate mean absolute deviation, net run rate, net boundary %, Successfully Defended and Chased scores, and more.

As shown in the example.py file using "print(search1.result.columns)" will print all the available stats for a particular search.

## How to:
 All you need to do is import cricketstats in any python script create a search object, call the "stats()" function with the necessary arguments for that search object and run the script through python3. The output of the function is a Pandas DataFrame that can be printed, analysed using pandas methods or served as the input to plotting methods like matplotlib.

To understand how to use the module you can use the "example.py" which provides a simple example.

## To Do:
1. Clean up stats independent of checks with stats dependent on checks.
2. Command-line wrapper
3. Web wrapper
4. Reverse look up of teams and players by stats.
5. Quick way to collect "all teams" or "all players" stats eg. if players or teams is blank then I should look at all players and all teams? or when "all teams" and "all players is included.
6. Arbitrary Keyword Arguments for function?
7. Expected runs model? basically sum of weighted average of runs per ball * average innings length. something along th lines of pythagorean thing.
8. Index more things?, so they can serve as lists for seeing what teams there are in a comp. Venues by country also put in checks when values are null.
9. Let us know all the possibilities we can expect within result method for plotting (ie. loc?)
10. Arguments via a dict? dicts should be defined in a separate file
11. eachball will read better as this(?)ball (same for eachwicket and others)
12. match - case in multiple if test for the same variable
13. Release as PyPi module that can be installed via pip