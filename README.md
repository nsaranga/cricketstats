# getcricketstats
A python script which gets team and player statistics from the [cricsheet.org](https://cricsheet.org/) database for data analysis.

## How to:
This is essentially a module you can import into any python script to collect statistics from cricsheet json files. All you need to do is import getstats in any python script create a search object, call the "getstats()" function with the necessary arguments for that search object and run the script through python3. The output of the function is a pandas dataframe that can be printed, analysed using pandas methods or served as the input to plotting methods like matplotlib.

To understand how to use the module you can use the "example.py" which provides simple example.


## To Do:
1. Command-line wrapper
2. Web wrapper
3. Reverse look up of teams and players by stats.
4. Scores by batting position
5. Superover stats.
6. ???
