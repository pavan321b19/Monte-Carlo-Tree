import math
import time
import random
from util import manhattanDistance, Counter
from MCTNode import MCTNode, Tactic
from PacmanTree import PacmanTree
from pacman import GhostRules, COLLISION_TOLERANCE, SCARED_TIME
from ghostAgents import RandomGhost

from game import Agent, Directions

DEBUG = False

def debug(*args):
    if DEBUG:
        print(*args)

class MCTSAgent(Agent):
    """
    A MCTS agent's decision making is implemented with a decision tree, and it also involves some randomness. Every time an action is chosen, it simulates the rest of the game to help evaluate the actions chosen. It is expected for the agent to simulate the game numerous times in order to evaluate its decisions.
    
    The mechanism or main steps of MCTS are implemented here: Selection, Expansion, Simulation, Backpropagation.

    Based heavily off of this paper: https://ieeexplore.ieee.org/document/6731713/metrics#metrics
    """
    
    def __init__(self):

        # Configurable parameters, in order of most important to least important

        self.time_limit = 0.25 # time limit to choose action in seconds
        self.simulation_duration = 40 # number of timesteps to simulate in each simulation

        self.survival_threshold = 0.6 # minimum survival score to consider a child on first pass
        self.threshold = 15 # number of times all children must be visited before choosing best child
        
        self.should_reuse = True # whether to reuse old tree
        self.timestep_discount = 0.6 # discount factor for timestep if reuse is enabled

        self.should_use_simulation_strategy = True # whether to use simulation strategy
        self.use_long_term_goals = True # whether to use long term goals
        self.use_tactics = True # whether to use tactics like ghost hunting or pill hunting
        
        self.simulated_ghost_agent = RandomGhost(1) # Only change if you want to use a different ghost agent
        
        # self.action_limit = 10

        # Don't change these

        self.tree = None
        self.prev_state = None # previous state of game
        self.num_pills = 0 # number of pills at start of game
        self.tactic = Tactic.SURVIVAL  # tactic to use for evaluation

    def reuse_tree(self, gameState):
        # Check if we ate a power pellet
        if self.should_reuse:
            if self.prev_state != None:
                prev_capsules = self.prev_state.getCapsules()
                curr_capsules = gameState.getCapsules()
                if len(prev_capsules) > len(curr_capsules):
                    # Don't reuse old tree, start from scratch
                    self.tree.reset(gameState)
                    return
                if sum(gameState.data._eaten) > 0:
                    # Don't reuse old tree, start from scratch
                    self.tree.reset(gameState)
                    return
            else:
                self.tree.reset(gameState)
                return

            self.tree.update(gameState)
        else:
            self.tree.reset(gameState)
    
    def runMCTS(self, gameState):
        """
        Builds the entire tree for a state after simulating a certain amount of times.
        The more simulations run, the larger the depth of the resulting tree and values
        should more likely converge.
        """
        start_time = time.time()
        num_simulations = 0
        num_survived = 0
        num_selected = Counter()
        while time.time() - start_time < self.time_limit:
            self.tactic = self.get_tactic(gameState, num_survived / num_simulations if num_simulations > 0 else 0)
            leaf_node = self.select()
            actions = self.get_actions(leaf_node)
            num_selected[actions[0]] += 1
            (sim_result, relevant_node) = self.simulate(gameState.deepCopy(), actions, leaf_node)
            result = self.evaluate(*sim_result)
            num_simulations += 1
            if result[0] == 1:
                num_survived += 1
            self.backpropagate(relevant_node, result)

        self.tactic = self.get_tactic(gameState, num_survived / num_simulations if num_simulations > 0 else 0)
        
        debug(num_selected)
            
    def getAction(self, gameState):
        """
        Returns the next action the agent will take. self.simcount amount of simulations
        are run to choose each successive action.
        """
        if self.tree == None:
            self.tree = PacmanTree(gameState)
            self.num_pills = gameState.getNumFood()
        self.reuse_tree(gameState)
        self.runMCTS(gameState)
        # print results
        if DEBUG:
            self.tree.root.print_stats(limit=2)
            debug('\n')
        for child in self.tree.root.children:
            debug(child.actions[0], child.visits,
                  child.get_value(self.tactic), self.tactic)
        self.prev_state = gameState

        if self.use_tactics:
            ordered_tactics = [self.tactic, Tactic.GHOST, Tactic.PILL, Tactic.SURVIVAL]

            for tactic in ordered_tactics:
                filtered_children = []
                for child in self.tree.root.children:
                    if child.get_value(tactic) > 0 and child.get_value(Tactic.SURVIVAL) > self.survival_threshold:
                        filtered_children.append(child)
                if len(filtered_children) > 0:
                    best_child = max(filtered_children, key=lambda x: x.get_value(tactic))
                    self.tactic = tactic
                    action = best_child.actions[0]
                    debug('Action:', action, 'Tactic:', tactic)
                    return action
        action = max(self.tree.root.children,
                     key=lambda x: x.get_value(Tactic.SURVIVAL)).actions[0]
        debug('Action:', action, 'Tactic:', Tactic.SURVIVAL)
        return action


    def get_tactic(self, gameState, survival_rate):
        """
        Returns the tactic to use for evaluation.
        """

        if not self.use_tactics:
            return Tactic.SURVIVAL

        if survival_rate < self.survival_threshold:
            return Tactic.SURVIVAL

        pos = gameState.getPacmanPosition()

        # Check if there are edible ghosts in the range of pacman
        for ghost in gameState.getGhostStates():
            if ghost.scaredTimer > 0 and manhattanDistance(gameState.getPacmanPosition(), ghost.getPosition()) < ghost.scaredTimer:
                # Get the distance to the ghost
                (ghost_x, ghost_y) = ghost.getPosition()
                ghost_x = math.floor(
                    ghost_x) if ghost_x < pos[0] else math.ceil(ghost_x)
                ghost_y = math.floor(
                    ghost_y) if ghost_y < pos[1] else math.ceil(ghost_y)
                ghost_pos = (ghost_x, ghost_y)
                distance, actions = self.tree.maze_distance(
                    gameState.getPacmanPosition(), ghost_pos)
                # Check if the ghost is reachable
                if distance < ghost.scaredTimer:
                    return Tactic.GHOST
        
        return Tactic.PILL


    # Selection
    def select(self): # gameState argument passed is the game's initial state
        """
        Finds and selects the next node to expand and then returns the
        expanded node.
        """
        node = self.tree.root
        while True:
            successors = self.tree.get_successors(node)
            
            # only allow reversing direction if the node is root
            if node != self.tree.root and len(successors) > 1:
                successors = [successor for successor in successors if successor[1][0] != self.opposite(node.actions[-1])]

            # if len(self.get_actions(node)) > self.action_limit:
            #     return node

            if len(node.children) < len(successors):
                # prioritize unvisited junctions first
                unvisited = [successor for successor in successors if all(successor[0] != child.position or successor[1][0] != child.actions[0] for child in node.children)]
                successor = random.choice(unvisited)
                return self.expand(node, successor)
            else:
                # continue random selection unless all children have been visited more than threshold
                if any(child.visits < self.threshold for child in node.children):
                    node = random.choice(node.children)
                else:
                    node = self.best_child(node)
    
    # Expansion
    def expand(self, node, successor):
        """
        Expands the tree, updates visit values here, and returns the expanded node
        """
        pos, actions = successor
        child = MCTNode(pos, actions)
        node.addChild(child)
        return child
    
    # Simulation
    def simulate(self, gameState, actions, leaf_node):
        """
        After expansion, let the agent play out randomly or by some method.
        The simulation stops once a certain amount of timesteps have passed or
        we reach a terminal state.
        """

        ghost_eaten_remaining_time = 0
        is_selection = True
        ate_capsule = False
        prev_state = None
        last_junction_state = None
        num_food = gameState.getNumFood()
        for i in range(self.simulation_duration):
            # Early termination if we reach a terminal state
            if gameState.isWin():
                break
            if gameState.isLose():
                # if last_junction_state != None and is_selection:
                #     gameState = last_junction_state
                #     is_selection = False
                #     continue
                # elif last_junction_state == None:
                #     gameState = prev_state
                #     last_junction_state = gameState
                #     is_selection = False
                #     continue
                break

            if is_selection and self.tree.is_junction(gameState.getPacmanPosition()):
                last_junction_state = gameState

            # Check if we ate a ghost
            if sum(gameState.data._eaten) > 0 and prev_state != None:
                ghost_eaten_remaining_time += sum(prev_state.getGhostState(i).scaredTimer for i in range(1, gameState.getNumAgents()-1) if gameState.data._eaten[i])
                is_selection = False


            # Check if we ate a power pellet
            if prev_state and len(gameState.getCapsules()) < len(prev_state.getCapsules()):
                # Check if any ghosts were edible in the previous state
                edible_time = sum(prev_state.getGhostState(i).scaredTimer for i in range(1, gameState.getNumAgents()-1))
                if edible_time > 0:
                    # Terminate immediately
                    break
                is_selection = False
                ate_capsule = True


            legalMoves = gameState.getLegalActions()
            if is_selection and len(actions) > 0:
                # Choose the next predetermined action
                action = actions.pop(0)
            else:
                action = None
            if not action in legalMoves:  # simulated actions here
                is_selection = False
                if self.should_use_simulation_strategy:
                    action = self.simulation_strategy(gameState)
                else:
                    action = random.choice(legalMoves)

            try:
                prev_state = gameState
                gameState = gameState.generateSuccessor(0, action, copy=False)
                for i in range(1, gameState.getNumAgents()-1):
                    if gameState.isLose() or gameState.isWin():
                        break
                    self.simulated_ghost_agent.index = i
                    gameState = gameState.generateSuccessor(i, self.simulated_ghost_agent.getAction(gameState), copy=False)
            except Exception as e:
                debug(e)
                debug(gameState)
                debug(action)
                debug(actions)
                debug(legalMoves)
                raise e

        leaf_to_update = leaf_node

        # last_junction_state = gameState

        # while last_junction_state != None:
        #     if leaf_to_update.position == last_junction_state.getPacmanPosition():
        #         break
        #     if leaf_to_update.parent == None:
        #         leaf_to_update = leaf_node
        #         break
        #     leaf_to_update = leaf_to_update.parent

        return (gameState, ghost_eaten_remaining_time, num_food - gameState.getNumFood(), ate_capsule), leaf_to_update

    def evaluate(self, gameState, ghost_eaten_remaining_time, num_food_eaten, ate_capsule):
        """
        Returns the evaluation of the state
        
        There are three rewards:

        The survival reward is the reward for staying alive. It is 1 if Pacman is alive or won the game, and 0 if Pacman lost the game.
        The pill reward is the reward for eating pills. It is the number of pills eaten, normalized by the number of pills at the start of the game.
        The ghost reward is the reward for eating ghosts. It is the number of ghosts eaten, normalized by the total edible time at the start of the simulation.
        """

        survival_reward = 1 if not gameState.isLose() else 0
        pill_reward = (num_food_eaten / self.num_pills) if self.num_pills > 0 else 0
        ghost_reward = ghost_eaten_remaining_time / SCARED_TIME

        if self.use_long_term_goals:
            if ate_capsule:
                if ghost_reward >= 0.5:
                    pill_reward += ghost_reward
                else:
                    pill_reward = 0

        return (survival_reward, pill_reward, ghost_reward)


            
    # Backpropagation
    def backpropagate(self, node, result):
        """
        All the nodes in the tree that are involved in the simulation have
        their statistics updated afterwards.
        """

        while True: # update stats
            node.visits += 1
            node.rewards[Tactic.SURVIVAL] += result[0]
            node.rewards[Tactic.PILL] += result[1]
            node.rewards[Tactic.GHOST] += result[2]
            
            if node == self.tree.root:
                return

            node = node.parent
        

    def uct_score(self, node):
        """
        Updates and returns the UCT score of a node
        """
        score = node.get_value(self.tactic)
        c = math.sqrt(2)
        explore = math.sqrt(math.log((node.parent.visits)) / (node.visits))
        
        return score + (c * explore)
        
    def best_child(self, node, option='max'):
        """
        Returns the best child of a node
        """
        if option == 'max':
            return max(node.children, key=lambda child: self.uct_score(child))
        elif option == 'visits':
            return max(node.children, key=lambda child: child.visits)
    
    def get_actions(self, node):
        """
        Returns sequence of actions to start simulation with
        """
        # Traverse the tree starting from node upwards to the root constructing a sequence of actions
        actions = []
        while node != self.tree.root:
            actions.extend(reversed(node.actions))
            node = node.parent
        actions.reverse()
        return actions
    
    def opposite(self, action):
        """
        Returns the opposite action of the previous action
        """
        return Directions.REVERSE[action]
        
    def simulation_strategy(self, currentGameState):
        """
        Moves made by Pac-Man are prioritized based on safety and possible reward. When more than one move has the highest priority, a move is chosen at random. Before discussing the strategy in detail, the concept of a safe move must first be defined. A safe move is any move that leads to an edge which:

        has no nonedible ghost on it moving in Pac-Man's direction;

        whose next junction is safe, i.e., in any case, Pac-Man will reach the next junction before a nonedible ghost.

        During playout, Pac-Man moves according to the following set of rules. If Pac-Man is at a junction, the following rules apply, sorted by priority.

        If there are reachable edible ghosts, i.e., the traveling time it takes to reach a ghost is smaller than its edible time remaining, then select a safe move that follows along the shortest path to the nearest edible ghost.

        If a safe move leads to an edge that is not cleared, i.e., contains any number of pills, it is performed.

        If all safe edges are cleared, select a random move leading to a safe edge.

        If no safe moves are available, a random move is selected.

        If Pac-Man is on an edge, she can either choose to maintain her current course or reverse it. The following rules consider the cases when Pac-Man is allowed to reverse:

        there is a nonedible ghost heading for Pac-Man on the current path;

        a power pill was eaten; in this case, the move that leads to the closest edible ghost is selected.

        In any other case, Pac-Man continues forward along the current edge. Note that if Pac-Man previously chose to reverse on the current edge, she may not reverse again until she reaches a junction. Moreover, to improve the performance of playouts, checking the first condition is only performed if the last move made at a junction was based on an unsafe decision.
        """

        pos = currentGameState.getPacmanPosition()
        is_junction = self.tree.is_junction(currentGameState.getPacmanPosition())

        food = currentGameState.getFood()
        capsules = currentGameState.getCapsules()

        unscared_ghost_positions = [ghost.getPosition() for ghost in currentGameState.getGhostStates() if not ghost.scaredTimer > 0]
        scared_ghost_positions = [ghost.getPosition() for ghost in currentGameState.getGhostStates() if ghost.scaredTimer > 0]

        if is_junction:
            # Find the safe moves
            successors = self.tree.successors(currentGameState.getPacmanPosition())
            safe_moves = []
            safe_successors = []
            for end_pos, actions in successors:
                current_pos = pos
                path = []
                is_safe = True
                action_index = 0
                while current_pos != end_pos:
                    if any(GhostRules.canKill(current_pos, ghost_pos) for ghost_pos in unscared_ghost_positions):
                        is_safe = False
                        break
                    path.append(current_pos)
                    current_pos = self.tree.next_position(current_pos, actions[action_index])
                    action_index += 1
                if is_safe:
                    # Check if any ghost can reach the junction before Pacman
                    for ghost in currentGameState.getGhostStates():
                        if ghost.scaredTimer < len(actions) + COLLISION_TOLERANCE and manhattanDistance(ghost.getPosition(), end_pos) <= len(actions) + COLLISION_TOLERANCE:
                            # Round ghost position x and y to integers, towards the direction that minimizes the manhattan distance
                            (ghost_x, ghost_y) = ghost.getPosition()
                            ghost_x = math.floor(ghost_x) if ghost_x > end_pos[0] else math.ceil(ghost_x)
                            ghost_y = math.floor(ghost_y) if ghost_y > end_pos[1] else math.ceil(ghost_y)
                            ghost_pos = (ghost_x, ghost_y)
                            if self.tree.maze_distance(ghost_pos, end_pos)[0] <= len(actions) <= len(actions) + COLLISION_TOLERANCE:
                                is_safe = False
                                break
                if is_safe:
                    safe_moves.append(actions[0])
                    safe_successors.append((end_pos, actions, path))

            # Check if there are reachable edible ghosts
            edible_ghosts = []
            for ghost in currentGameState.getGhostStates():
                if ghost.scaredTimer > 0 and manhattanDistance(currentGameState.getPacmanPosition(), ghost.getPosition()) < ghost.scaredTimer:
                    # Get the distance to the ghost
                    distance, actions = self.tree.maze_distance(currentGameState.getPacmanPosition(), ghost.getPosition())
                    # Check if the ghost is reachable
                    if distance < ghost.scaredTimer and (len(actions) == 0 or actions[0] in safe_moves):
                        edible_ghosts.append((distance, actions[0]))
            if len(edible_ghosts) > 0:
                # Get the closest edible ghost
                closest_ghost = min(edible_ghosts, key=lambda x: x[0])
                # Get the action that leads to the closest edible ghost
                return closest_ghost[1]

            # Check if there are any pills along the paths to the successor junctions
            for pos, actions, path in safe_successors:
                for next_pos in path:
                    if food[next_pos[0]][next_pos[1]] or next_pos in capsules:
                        return actions[0]

            # If all safe edges are cleared, select a random move leading to a safe edge
            if len(safe_successors) > 0:
                useful_moves = [successor[1][0] for successor in safe_successors if len(self.tree.get_legal_actions(successor[0])) > 1]
                if len(useful_moves) > 0:
                    return random.choice(useful_moves)
                return random.choice(safe_moves)
            
            # If no safe moves are available, a random move is selected
            return random.choice(self.tree.get_legal_actions(currentGameState.getPacmanPosition()))

        else:
            # If there is a non edible ghost on the current path, reverse
            current_pos = pos
            action = currentGameState.getPacmanState().configuration.direction
            while not self.tree.is_junction(current_pos) and len(self.tree.get_legal_actions(current_pos)) > 1:
                # Get the available direction to move that is not the reverse of the previous move
                action = [direction for direction in self.tree.get_legal_actions(current_pos) if direction != self.opposite(action)][0]
                current_pos = self.tree.next_position(current_pos, action)
                dangerous_ghosts = [ghost for ghost in currentGameState.getGhostStates() if ghost.scaredTimer == 0]
                for ghost in dangerous_ghosts:
                    if GhostRules.canKill(current_pos, ghost.getPosition()) and ghost.configuration.direction == self.opposite(action):
                        opposite_direction = self.opposite(currentGameState.getPacmanState().configuration.direction)
                        if opposite_direction in self.tree.get_legal_actions(pos):
                            return opposite_direction
                        else:
                            debug("This should never happen!!")
                            return self.tree.get_legal_actions(pos)[0]
                if current_pos in currentGameState.getCapsules():
                    break
            if len(self.tree.get_legal_actions(pos)) > 1:
                return [direction for direction in self.tree.get_legal_actions(pos) if direction != self.opposite(currentGameState.getPacmanState().configuration.direction)][0]
            return self.tree.get_legal_actions(pos)[0]
