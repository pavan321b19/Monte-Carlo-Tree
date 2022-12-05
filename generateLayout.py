import argparse
import os
import sys
import random
import numpy as np
from util import manhattanDistance
import time

def buildLayout(layout, numberWalkers, size, numberGhosts, type):
    """
    Takes numpy 2d array as input to build layout using random walkers.
    Position (0, 0) is the top left corner of a layout and position (h-1, w-1) is the
    bottom right corner.
    """
    height = layout.shape[0]
    width = layout.shape[1]
    minDistance = 1
    maxDistance = min(height, width) -2 # account for layout edges
    #maxDistance = min(7, max(height, width) -2) # account for layout edges
    
    # walkers' (starting position, distance to cover) initialization
    walkers = []
    h_positions = [i for i in range(1, height-2)]
    w_positions = [i for i in range(1, width-2)]
    if type == 'tunnels':
        for i in range(numberWalkers):
            if i == 0:
                number = random.choice(h_positions)
                if number % 2 == 0: # keep even position indices only
                    h_positions = [value for value in h_positions if value % 2 == 0]
                    w_positions = [value for value in w_positions if value % 2 == 0]
                else: # keep odd position indices only 
                    h_positions = [value for value in h_positions if value % 2 != 0]
                    w_positions = [value for value in w_positions if value % 2 != 0]
            # avoid edge positions and use only even or only odd row/column indices
            initPos = (random.choice(h_positions), random.choice(w_positions))
            initDist = random.randint(minDistance, maxDistance//2)*2 # move even amount of distances only
            walkers.append( [initPos, initDist] )
    else:
        for i in range(numberWalkers):
            initPos = (random.randint(1, height-2), random.randint(1, width-2)) # avoid edge positions
            initDist = random.randint(minDistance, maxDistance)
            walkers.append( [initPos, initDist] )
        
    # walker direction movements defined here; takes position tuples as arguments
    def up(pos):
        return (pos[0]-1, pos[1])
    def down(pos):
        return (pos[0]+1, pos[1])
    def left(pos):
        return (pos[0], pos[1]-1)
    def right(pos):
        return (pos[0], pos[1]+1)
    directions = [up, down, left, right] # list of movement functions
    
    total = sum(sum(layout)) - 2*(height+width) + 4
    total_ = total
    stop_condition = 0.5*total if type == 'tunnels' else 0.4*total
    #stop_condition = 0.33*total if type == 'tunnels' else 0.25*total
    
    # FOOD
    # tunnels: stopping condition is >= 50% of map (excluding edges) is filled with food/pills
    # spatial: stopping condition is >= 60% of map (excluding edges) is filled with food/pills
    time_start, time_limit = time.time(), 2. # in case while loop does not end
    while total_ > stop_condition:
        for i, (p,d) in enumerate(walkers):
            pos, dist = p, d
            direction = random.choice(directions) # randomly choose a movement direction
            if type == 'tunnels':
                # ensures that walker only travels in a direction where it will move an even amount
                t_dist = None
                if direction == up: t_dist = manhattanDistance(pos, (0, pos[1])) # distances to directional edge
                elif direction == down: t_dist = manhattanDistance(pos, (height-1, pos[1])) 
                elif direction == left: t_dist = manhattanDistance(pos, (pos[0], 0)) 
                elif direction == right: t_dist = manhattanDistance(pos, (pos[0], width-1))
                if t_dist <= dist:
                    if t_dist % 2 == 0: # check if even number distance to edge 
                        while t_dist <= dist:
                            dist -= 2 
                    else: # odd number distance to edge 
                        pass
            while True:
                layout[pos] = 0 # replace current (wall) spot with food spot
                next = direction(pos)
                # break if next position is an edge
                if next[0] == 0 or next[0] == height-1 or next[1] == 0 or next[1] == width-1:
                    break
                dist -= 1
                if dist < 0: # break after creating the number of food spots 
                    break
                pos = next
            walkers[i][0] = list(walkers[i][0])
            walkers[i][0] = tuple([pos[0],pos[1]]) # change walker's start position
          
        total_ = sum(sum(layout)) - 2*(height+width) + 4
        if type == 'tunnels': # re-initialize walker distances and positions
            walkers = [[pos, random.randint(minDistance, maxDistance//2)*2] for pos, _ in walkers] # move even amount of distances
        else:
            # re-randomize walker distances after each iteration
            walkers = [[pos, random.randint(minDistance, maxDistance)] for pos, _ in walkers]
        if time.time() - time_start > time_limit:
            break
        
    # PILLS
    # 2 pills in small, 3 in medium, 4 in large; place them in corners/quadrants
    pillCount = 0
    if size == 'small': pillCount = 2
    elif size == 'medium': pillCount = 3
    elif size == 'large': pillCount = 4
    # upper right, left, bottom right, left
    corners = ['upr', 'upl', 'botr', 'botl']
    for _ in range(pillCount):
        corner_index = random.randint(0, len(corners)-1)
        corner = corners.pop(corner_index)
        pillPos, c_index, r_index = None, None, None
        if corner == 'upr' or corner == 'upl': # start from top non-edge row
            r_index = 1
            cIndices = np.where(layout[r_index,:] == 0)[0]
            while len(cIndices) == 0: # if row is all walls
                r_index += 1
                cIndices = np.where(layout[r_index,:] == 0)[0]
            c_index = cIndices[-1] if corner == 'upr' else cIndices[0]
        elif corner == 'botr' or corner == 'botl': # start from bottom non-edge row
            r_index = -2
            cIndices = np.where(layout[r_index,:] == 0)[0]
            while len(cIndices) == 0: # if row is all walls
                r_index -= 1
                cIndices = np.where(layout[r_index,:] == 0)[0]
            c_index = cIndices[-1] if corner == 'botr' else cIndices[0]
        pillPos = (r_index, c_index)
        layout[pillPos] = 2
    
    # PACMAN
    openPositions = np.where(layout == 0)
    # place pacman in a random spot
    index = random.randint(0, len(openPositions[0])-1)
    pacmanPos = (openPositions[0][index], openPositions[1][index])
    layout[pacmanPos] = 3
    
    # GHOSTS
    openPositions = np.where(layout == 0)
    # place ghost(s) in a random spot (preferably at some minimum distance away from pacman)
    minimum = min(height, width) // 2 # too large may not work for smaller layouts
    #minimum = max(height, width) // 2.5
    for _ in range(numberGhosts):
        dist = 0
        ghostPos = None
        time_start, time_limit = time.time(), 2. # in case while loop does not end
        while dist < minimum:
            index = random.randint(0, len(openPositions[0])-1)
            ghostPos = (openPositions[0][index], openPositions[1][index])
            dist = manhattanDistance(ghostPos, pacmanPos)
            if time.time() - time_start > time_limit:
                break
        layout[ghostPos] = -1
        openPositions = np.where(layout == 0)
    
    return layout

def generateLayout(argv):
    """
    Processes the command used to generate a Pacman layout from the command line.
    """
    usageStr = """
    EXAMPLES:   (1) python generateLayout.py -n 30 -s large
                    (creates 30 large layouts)
                (2) python generateLayout.py -s medium -g 3
                    (creates 9 medium layouts with 3 ghosts each)
    """
    parser = argparse.ArgumentParser(description=usageStr)
    
    parser.add_argument('-n', '--number', default=9, type=int, help='number of layouts to generate')
    parser.add_argument('-s', '--size', default='medium', help='specify the size of the generated layouts; choose between small, medium, large')
    parser.add_argument('-g', '--ghosts', default=2, type=int, help='number of ghosts in layouts')
    parser.add_argument('-t', '--type', default='spatial', help='specify the type of layouts generated; choose between spatial or tunnels')
    parser.add_argument('-w', '--walkers', default=4, type=int,
                        help='number of walkers to use')

    # print usage if no arguments provided
    if len(argv) == 0:
        parser.print_usage()
        return
    
    args = parser.parse_args(argv)
    # check validity of some of the arguments
    if args.number < 1:
        raise argparse.ArgumentTypeError('Number of layouts has to be greater than 0!')
    if args.walkers < 1:
        raise argparse.ArgumentTypeError('Number of walkers has to be greater than 0!')
    if args.size not in ['small', 'medium', 'large']:
        raise argparse.ArgumentTypeError('Invalid layout size provided!')
    if args.ghosts < 1:
        raise argparse.ArgumentTypeError('Number of ghosts has to be greater than 0!')
    if args.type not in ['spatial', 'tunnels']:
        raise argparse.ArgumentTypeError('Invalid layout type provided!')
        
    # create folder for generated maps
    path = 'layouts/gen_' + args.size
    if not os.path.exists(path):
        os.makedirs(path)
    
    # map containing layout icons
    layout_map = {
        0 : '.', # food
        1 : '%', # wall
        2 : 'o', # pill
        3 : 'P', # pacman
        -1 : 'G' # ghost
    }
    # arbitrarily set min and max dimensions for layouts
    small_min = 8
    small_max = 12
    medium_min = 14
    medium_max = 16
    large_min = 20
    large_max = 24
    min_ = eval(args.size+'_min')
    max_ = eval(args.size+'_max')
    
    # create layouts here
    created_count = 0
    while created_count < args.number:
        height = random.randint(min_, max_)
        width = random.randint(min_, max_)
        layout = np.ones((height, width)) # initialized 2d array with all wall spots
        layout = buildLayout(layout, args.walkers, args.size, args.ghosts, args.type) # using crawlers to build layout
        
        with open(f'layouts/gen_{args.size}/{args.size}{created_count}_{args.type}.lay', 'w') as f:
            for i in range(height):
                row = layout[i,:].tolist()
                row = [*map(layout_map.get, row)]
                f.write(''.join(row)+'\n')
            f.close()
        
        created_count += 1
    
    print(f'\nSuccessfully created {args.number} {args.size} layout(s) of type \'{args.type}\'!')
    print(f'Newly created layouts are found in: ./layouts/gen_{args.size}')
    return 


if __name__ == '__main__':
    args = sys.argv[1:]
    generateLayout(args)
    





