# MCTS Agent
By Richard Cao, Thomas Blunt, Pavan Srinivas Narayana, and Asfiya Shaik

## Initial Setup
We use Python 3.10.
```bash
# Requirements
pip install numpy scipy pandas matplotlib
```
## Generating Layouts

The script used to generate layouts is *generateLayout.py*. Its usage is:

*python generateLayout.py [-h] [-n NUMBER] [-s SIZE] [-g GHOSTS] [-t TYPE] [-w WALKERS]*
- *-n* specifies the total number of layouts to generate; defaults to 9
- *-s* specifies the size of all the generated layouts (small, medium, large); defaults to medium
- *-g* specifies the number of ghosts in each generated layout; defaults to 2
- *-t* specifies the type of layout (spatial, tunnels); defaults to spatial
- *-w* specifies the number of random walkers used to generate layouts; defaults to 4

The following sequence of commands generate a total of 60 layouts, where 20 are small, 20 are medium, and 20 are large, and all have 3 ghosts and are of type spatial:

1. *python generateLayout.py -n 20 -s small -g 3 -t spatial*
2. *python generateLayout.py -n 20 -s medium -g 3 -t spatial*
3. *python generateLayout.py -n 20 -s large -g 3 -t spatial*

The names of the generated layouts will follow the format *small0_spatial.lay*, numbered from 0 to NUMBER-1. They will be located in the corresponding directories based on SIZE:
- *layouts/gen_small*
- *layouts/gen_medium*
- *layouts/gen_large*

## Generating Test Data

### Manually:
At any time, you can run the MCTS agent by executing
```bash
python pacman.py -p MCTSAgent
```
Any specific agent arguments can be applied by appending `-a` and then a list of comma separated parameter assignments:
```bash
python pacman.py -p MCTSAgent -a simulation_length=40,num_simulations=100
```
You can find more agent arguments inside the `__init__` method of MCTSAgent in mctsAgents.py.

### Bulk Data for Evaluation:
After the layouts are generated, run the parallel testing script to generate the test data:
```bash
python run_parallel_tests.py
# Results are saved to results.csv
```
This file can be edited to adjust the range of parameters tested. The current state of the file is the parameters we tested with for our results.

> Warning: This takes a very, very long time. On an Intel Core i9-13900k, this took about 2 hours of 100% usage at base configuration to simulate all 960 runs. If attempting to recreate the results data yourself, I would recommend editing the script to consider fewer permutations, or removing some layouts from the gen_* directories.


## Running Evaluation

### T-test
The t-test script is available in ttest.py

T-test pulls all the results from the final_results.xlsx file which has all the run results. 

>This requires you to convert results.csv into an Excel spreadsheet if you want to generate your own data. This can be done by creating a new spreadsheet then navigating to Data > From Text/CSV, and then saving as a spreadsheet.

Run T-test.py file using the command : python ttest.py

Command line displays the scores generated for Minimax, Expectimax and MCTS Agents.

It also displays the P values for combinations of Minimax, Expectimax and MCTS Agents.

Plots are displayed for P-Values, Scores comparision, Win Ratio comparision and Average Number of Moves. All the plots are saved in the ./figures folder in the project.



