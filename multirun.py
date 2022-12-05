from itertools import repeat
import multiprocessing as mp
from pacman import *
from contextlib import redirect_stdout
import csv, math, datetime, random
from functools import partial


def readCommandExtended(argv):
    """
    Processes the command used to run pacman from the command line.
    """
    from optparse import OptionParser
    usageStr = """
    USAGE:      python pacman.py <options>
    EXAMPLES:   (1) python pacman.py
                    - starts an interactive game
                (2) python pacman.py --layout smallClassic --zoom 2
                OR  python pacman.py -l smallClassic -z 2
                    - starts an interactive game on a smaller board, zoomed in
    """
    parser = OptionParser(usageStr)

    parser.add_option('-n', '--numGames', dest='numGames', type='int',
                      help=default('the number of GAMES to play'), metavar='GAMES', default=1)
    parser.add_option('-l', '--layout', dest='layout',
                      help=default(
                          'the LAYOUT_FILE from which to load the map layout'),
                      metavar='LAYOUT_FILE', default='mediumClassic')
    parser.add_option('-p', '--pacman', dest='pacman',
                      help=default(
                          'the agent TYPE in the pacmanAgents module to use'),
                      metavar='TYPE', default='KeyboardAgent')
    parser.add_option('-t', '--textGraphics', action='store_true', dest='textGraphics',
                      help='Display output as text only', default=False)
    parser.add_option('-q', '--quietTextGraphics', action='store_true', dest='quietGraphics',
                      help='Generate minimal output and no graphics', default=False)
    parser.add_option('-g', '--ghosts', dest='ghost',
                      help=default(
                          'the ghost agent TYPE in the ghostAgents module to use'),
                      metavar='TYPE', default='RandomGhost')
    parser.add_option('-k', '--numghosts', type='int', dest='numGhosts',
                      help=default('The maximum number of ghosts to use'), default=4)
    parser.add_option('-z', '--zoom', type='float', dest='zoom',
                      help=default('Zoom the size of the graphics window'), default=1.0)
    parser.add_option('-f', '--fixRandomSeed', action='store_true', dest='fixRandomSeed',
                      help='Fixes the random seed to always play the same game', default=False)
    parser.add_option('-r', '--recordActions', action='store_true', dest='record',
                      help='Writes game histories to a file (named by the time they were played)', default=False)
    parser.add_option('--replay', dest='gameToReplay',
                      help='A recorded game file (pickle) to replay', default=None)
    parser.add_option('-a', '--agentArgs', dest='agentArgs',
                      help='Comma separated values sent to agent. e.g. "opt1=val1,opt2,opt3=val3"')
    parser.add_option('-x', '--numTraining', dest='numTraining', type='int',
                      help=default('How many episodes are training (suppresses output)'), default=0)
    parser.add_option('--frameTime', dest='frameTime', type='float',
                      help=default('Time to delay between frames; <0 means keyboard'), default=0.1)
    parser.add_option('-c', '--catchExceptions', action='store_true', dest='catchExceptions',
                      help='Turns on exception handling and timeouts during games', default=False)
    parser.add_option('--timeout', dest='timeout', type='int',
                      help=default('Maximum length of time an agent can spend computing in a single game'), default=30)
    parser.add_option('--maxMoves', dest='maxMoves', type='int',
                      help=default('Maximum number of moves a game can go on for before losing by default'), default=None)

    options, otherjunk = parser.parse_args(argv)
    if len(otherjunk) != 0:
        raise Exception('Command line input not understood: ' + str(otherjunk))
    args = dict()

    # Fix the random seed
    if options.fixRandomSeed:
        random.seed('cs188')

    # Choose a layout
    args['layout'] = layout.getLayout(options.layout)
    if args['layout'] == None:
        raise Exception("The layout " + options.layout + " cannot be found")

    # Choose a Pacman agent
    noKeyboard = options.gameToReplay == None and (
        options.textGraphics or options.quietGraphics)
    pacmanType = loadAgent(options.pacman, noKeyboard)
    agentOpts = parseAgentArgs(options.agentArgs)
    if options.numTraining > 0:
        args['numTraining'] = options.numTraining
        if 'numTraining' not in agentOpts:
            agentOpts['numTraining'] = options.numTraining
    pacman = pacmanType(**agentOpts)  # Instantiate Pacman with agentArgs
    args['pacman'] = pacman

    # Don't display training games
    if 'numTrain' in agentOpts:
        options.numQuiet = int(agentOpts['numTrain'])
        options.numIgnore = int(agentOpts['numTrain'])

    # Choose a ghost agent
    ghostType = loadAgent(options.ghost, noKeyboard)
    args['ghosts'] = [ghostType(i+1) for i in range(options.numGhosts)]

    # Choose a display format
    if options.quietGraphics:
        import textDisplay
        args['display'] = textDisplay.NullGraphics()
    elif options.textGraphics:
        import textDisplay
        textDisplay.SLEEP_TIME = options.frameTime
        args['display'] = textDisplay.PacmanGraphics()
    else:
        import graphicsDisplay
        args['display'] = graphicsDisplay.PacmanGraphics(
            options.zoom, frameTime=options.frameTime)
    args['numGames'] = options.numGames
    args['record'] = options.record
    args['catchExceptions'] = options.catchExceptions
    args['timeout'] = options.timeout
    args['maxMoves'] = options.maxMoves

    # Special case: recorded games don't use the runGames method or args structure
    if options.gameToReplay != None:
        print('Replaying recorded game %s.' % options.gameToReplay)
        import pickle
        f = open(options.gameToReplay)
        try:
            recorded = pickle.load(f)
        finally:
            f.close()
        recorded['display'] = args['display']
        replayGame(**recorded)
        sys.exit(0)

    return options, agentOpts, args

def runGamesFast(layout, pacman, ghosts, display, numGames, record, numTraining=0, catchExceptions=False, timeout=30, maxMoves=None):
    import __main__
    import textDisplay
    __main__.__dict__['_display'] = display

    rules = ClassicGameRules(timeout)
    games = []

    for i in range(numGames):
        gameDisplay = textDisplay.NullGraphics()
        rules.quiet = True
        game = rules.newGame(layout, pacman, ghosts,
                             gameDisplay, True, catchExceptions, maxMoves)
        game.run()
        games.append(game)

    scores = [game.state.getScore() for game in games]
    wins = [game.state.isWin() for game in games]
    winRate = wins.count(True) / float(len(wins))
    numMoves = [game.numMoves for game in games]

    return scores, wins, winRate, numMoves

def simulateWithArgs(arguments):
    start_time = time.time()
    args = arguments.split()
    options, agentOps, args = readCommandExtended(args)  # Get game components based on input
    pacman_type = options.pacman
    ghost_type = options.ghost
    layout = options.layout
    scores, wins, winRate, numMoves = runGamesFast(**args)
    average_score = sum(scores) / len(scores)
    # Convert array of booleans to array of strings with Win for True and Loss for False
    wins = ['Win' if win else 'Loss' for win in wins]
    # Join into comma separated string
    wins = ', '.join(wins)
    # Set to "N/A" if not found in agentOps
    num_simulations = agentOps['num_simulations'] if 'num_simulations' in agentOps else 'N/A'
    simulation_length = agentOps['simulation_length'] if 'simulation_length' in agentOps else 'N/A'
    depth = agentOps['depth'] if 'depth' in agentOps else 'N/A'
    num_ghosts = options.numGhosts
    tree_reuse = agentOps['tree_reuse'] if 'tree_reuse' in agentOps else 'N/A'
    command = 'python pacman.py ' + arguments
    return [
        pacman_type,
        ghost_type,
        layout,
        average_score,
        ', '.join(map(str, scores)), 
        winRate,
        wins, 
        len(scores),
        simulation_length, 
        depth, 
        num_ghosts, 
        tree_reuse, 
        command,
        sum(numMoves) / len(numMoves),
        time.time() - start_time
    ]

def createArgumentsList():
    directories = ['layouts/gen_small', 'layouts/gen_medium', 'layouts/gen_large']
    pacman_types = ['MinimaxAgent', 'ExpectimaxAgent', 'MCTSAgent']
    ghost_types = ['RandomGhost', 'DirectionalGhost']
    num_ghosts = [2, 4]
    # Only applicable to MCTSAgent
    #simulation_lengths = [10, 20, 30]
    simulation_lengths = [20]
    # Only applicable to MinimaxAgent and ExpectimaxAgent
    #depths = [3, 4, 5]
    depths = [2]
    
    arguments_list = []

    for directory in directories:
        # Iterate through all layouts in directory
        for layout in os.listdir(directory):
            for pacman_type in pacman_types:
                for ghost_type in ghost_types:
                    for num_ghost in num_ghosts:
                        # Only applicable to MCTSAgent
                        if pacman_type == 'MCTSAgent':
                            for simulation_length in simulation_lengths:
                                arguments = '-q -n 2 --maxMoves 1500 --layout ' + directory + '/' + layout + ' --pacman ' + pacman_type + ' --ghost ' + ghost_type + ' --numghosts ' + str(num_ghost) + ' --agentArgs simulation_length=' + str(simulation_length) + ',should_reuse=True,ghost_type=' + ghost_type
                                arguments_list.append(arguments)
                        # Only applicable to MinimaxAgent and ExpectimaxAgent
                        elif pacman_type == 'MinimaxAgent' or pacman_type == 'ExpectimaxAgent':
                            for depth in depths:
                                arguments = '-q -n 1 --maxMoves 1500 --layout ' + directory + '/' + layout + ' --pacman ' + pacman_type + ' --ghost ' + ghost_type + ' --numghosts ' + str(num_ghost) + ' --agentArgs depth=' + str(depth)
                                arguments_list.append(arguments)
                        else:
                            arguments = '-q -n 1 --maxMoves 1500 --layout ' + directory + '/' + layout + ' --pacman ' + pacman_type + ' --ghost ' + ghost_type + ' --numghosts ' + str(num_ghost)
                            arguments_list.append(arguments)
    
    return arguments_list

def worker(arguments, queue):
    csv_cells = simulateWithArgs(arguments)
    queue.put(csv_cells)
        
def star_helper(func, args):
    return func(*args)

def main():
    arguments_list = createArgumentsList()
    num_per_agent = {
        'MinimaxAgent': len(arguments_list) / 3,
        'ExpectimaxAgent': len(arguments_list) / 3,
        'MCTSAgent': len(arguments_list) / 3,
    }
    # Randomly shuffle the arguments list so that partial results are not biased towards the beginning of the list
    random.shuffle(arguments_list)
    print(f"Running {len(arguments_list)} simulations")
    num_processes = round(mp.cpu_count() // 2)
    start_time = time.time()
    # New dict with same keys as num_per_agent but with values of 0
    completed_per_agent = {key: 0 for key in num_per_agent}
    time_per_agent = {key: 0 for key in num_per_agent}
    num_completed = {}
    with open('results.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter='|')
        writer.writerow([
            'Pacman Agent',
            'Ghost Agent',
            'Layout',
            'Average Score',
            'Scores',
            'Win Rate',
            'Record',
            'Number of Iterations',
            'Simulation Length',
            'Depth',
            'Number of Ghosts',
            'Tree Reuse',
            'Command',
            'Average Number of Moves',
            'Time Taken'
        ])
        file.flush()
        with mp.Pool(num_processes) as pool:
            #pool.imap_unordered(worker, arguments_list, chunksize=4)
            for item in pool.imap_unordered(simulateWithArgs, arguments_list, chunksize=1):
                writer.writerow(item)
                file.flush()
                elapsed_time = time.time() - start_time
                simulation_time = item[-1]

                # Calculate a smart estimate of the time remaining
                # Each agent type has a different average time to run
                # Each agent will be run num_per_agent[agent_type] times

                agent_type = item[0]
                completed_per_agent[agent_type] += 1
                time_per_agent[agent_type] += simulation_time

                # Calculate the average time per agent type

                average_time_per_agent = {key: time_per_agent[key] / (
                    completed_per_agent[key]) for key in time_per_agent if completed_per_agent[key] > 0}

                estimated_time_remaining_per_agent = {key: (
                    num_per_agent[key] - completed_per_agent[key]) * average_time_per_agent[key] for key in average_time_per_agent}

                # Account for parallelization
                estimated_time_remaining_per_agent = {
                    key: estimated_time_remaining_per_agent[key] / num_processes for key in estimated_time_remaining_per_agent}

                # Calculate the weighted average estimate of time remaining by how many times each agent type still needs to be run

                estimated_time_remaining = sum(
                    estimated_time_remaining_per_agent.values())

                num_completed = sum(completed_per_agent.values())
                num_rows = sum(num_per_agent.values())

                # Use datetime.timedelta to format the time remaining into hours, minutes, and seconds
                estimated_time_remaining = str(datetime.timedelta(
                    seconds=round(estimated_time_remaining)))
                print(
                    f"Completed {num_completed} of {num_rows} simulations ({num_completed / num_rows * 100:.2f}%) in {str(datetime.timedelta(seconds=round(elapsed_time)))}. Estimated time remaining: {estimated_time_remaining}")
                print("Remaining agents:")
                for key in completed_per_agent:
                    if completed_per_agent[key] != 0 and completed_per_agent[key] != num_per_agent[key]:
                        print(f"\t{key}: {completed_per_agent[key]} of {num_per_agent[key]} ({completed_per_agent[key] / num_per_agent[key] * 100:.2f}%)" + " | Estimated time left: " + str(
                            datetime.timedelta(seconds=round(estimated_time_remaining_per_agent[key]))) + " | Average: " + str(datetime.timedelta(seconds=round(average_time_per_agent[key]))))



if __name__ == '__main__':
    main()
