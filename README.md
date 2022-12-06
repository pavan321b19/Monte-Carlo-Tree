
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


