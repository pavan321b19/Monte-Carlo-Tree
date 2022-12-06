
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

## Running Evaluation

##T-test
T-test script is available in T-Tests.ipynb file. 
pip install scipy
pip install matplotlib
pip install numpy
pip install pandas

T-test pulls all the results from the final_results.xlsx file which has all the run results. 

Run T-test.py file using the command : python ttest.py

Command line displays the scores generated for Minimax, Expectimax and MCTS Agents
It also displays the P values for combinations of Minimax, Expectimax and MCTS Agents

Plots are displayed for P-Values, Scores comparision, Win Ratio comoarision and Average Number of Moves. All the plots are saved in figures folder in the project.



