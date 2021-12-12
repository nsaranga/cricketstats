# getcricketstats
A python script which gets team and player statistics from the [cricsheet.org](https://cricsheet.org/) database for data analysis.

## How to:
This is essentially a module you can import into any python script to collect statistics from cricsheet json files. All you need to do is import getstats in any python script create a search object, call the "getstats()" function with the necessary arguments for that search object and run the script through python3. The output of the function is a pandas dataframe that can be printed, analysed using pandas methods or served as the input to plotting methods like matplotlib.

To understand how to use the module you can use the "example.py" which provides simple example.

## To Do:
1. need ot clean up constant stats with stats dependnet on checks.
2. Command-line wrapper
3. Web wrapper
4. Reverse look up of teams and players by stats.
5. Quick way to collect "all teams" or "all players" stats eg. if players or teams is blank then I should look at all players and all teams? or when "all teams" and "all players is included.
6. Arbitrary Keyword Arguments for function?
7. Expected runs model? basically sum of weighted average of runs per ball * average innings length. something along th lines of pythagorean thing.
8. index more things?, so they can serve as lists for seeing what teams there are in a comp. Venues by country also put in checks when values are null.
9. Let us know all the possibilities we can expect within result method for plotting (ie. loc?)
10. arguments via a dict? dicts should be defined in a separate file
11. eachball will read better as this(?)ball (same for eachwicket and others)
12. match - case in multiple if test for the same variable