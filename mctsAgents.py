import math
import time
import random
from util import manhattanDistance
from MCTNode import MCTNode

from game import Agent, Directions

class MCTSAgent(Agent):
    """
    A MCTS agent's decision making is implemented with a decision tree, and it also involves some randomness. Every time an action is chosen, it simulates the rest of the game to help evaluate the actions chosen. It is expected for the agent to simulate the game numerous times in order to evaluate its decisions.
    
    The mechanism or main steps of MCTS are implemented here: Selection, Expansion, Simulation, Backpropagation.
    """
    
    def __init__(self):
        self.root = MCTNode(None) # root node of tree used for MCTS
        self.time_limit = 0.05 # time limit to choose action in seconds
        
        self.simcount = 500 # number of simulations to run
        self.threshold = self.simcount / 20 # minimum number of times each child is visited before using UCT to choose
        self.prevAction = None # holds previous action

    
    def runMCTS(self, gameState, simulationCount):
        """
        Builds the entire tree for a state after simulating a certain amount of times.
        The more simulations run, the larger the depth of the resulting tree and values
        should more likely converge.
        """
        count = 0
        while count < simulationCount:
            leaf_node = self.select(gameState)
            if isinstance(leaf_node, tuple): # won or lost
                result = True if leaf_node[0] else False
                self.backpropagate(leaf_node[1], result)
            else:
                actions = self.get_actions(leaf_node)
                # result = self.simulate(gameState, actions)
                result = self.simulate(gameState, actions, stop='action')
                self.backpropagate(leaf_node, result)
            count += 1
    def getAction(self, gameState):
        """
        Returns the next action the agent will take. self.simcount amount of simulations
        are run to choose each successive action.
        """
        self.runMCTS(gameState, self.simcount)
        # Update the root node and clean restart to find successive action
        self.root.print_stats(limit=2)
        
        temp = self.root
        self.root = self.best_child(temp)
        
        # print results
        # self.root.print_stats(limit=0)
        # temp.print_stats(depth=1,limit=2)
        print('\n')
        
        self.root.removeRelations()
        action = self.root.action
        self.root.resetStats()
        del temp
        
        self.prevAction = action
        return action
        
    # def getAction(self, gameState):
    #     """
    #     Returns the next action the agent will take
    #     """
    #     start = time.time()
    #     while time.time() - start < self.time_limit:
    #         leaf_node = self.select(gameState)
    #         actions = self.get_actions(leaf_node)
    #         result = self.simulate(gameState, actions)
    #         self.backpropagate(leaf_node, result)
    # 
    #     # Update the root node
    #     self.root = self.best_child(self.root)
    # 
    #     best_action = self.root.action
    # 
    #     # Update root for tree reuse
    # 
    #     self.root.parent = None
    #     self.root.action = None
    # 
    #     # Return the best action
    #     return best_action

    # Selection
    def select(self, gameState): # gameState argument passed is the game's initial state
        """
        Finds and selects the next node to expand and then returns the
        expanded node.
        """
        node = self.root
        while True:
            # influences score of node if game state results in terminal during selection
            if gameState.isLose():
                node.score -= 2
                return (False, node)
            if gameState.isWin():
                node.score += 2
                return (True, node)
            
            legalMoves = gameState.getLegalActions()
            # reaching a leaf, expand randomly while not all actions have been visited
            if len(node.children) < len(legalMoves):
                # prioritize unvisited actions first
                unvisited = [action for action in legalMoves if not any(child.action == action for child in node.children)]
                action = random.choice(unvisited)
                return self.expand(node, action)
            else:
                # continue random selection unless all children have been visited more than threshold
                if any(child.visits < self.threshold for child in node.children):
                    select = []
                    for i, child in enumerate(node.children):
                        if child.visits < self.threshold: select.append(i)
                    node = node.children[random.choice(select)]
                else:
                    # node = best
                    node = max(node.children, key=lambda child: child.score)
            gameState = gameState.generatePacmanSuccessor(node.action)
    
    # Expansion
    def expand(self, node, action):
        """
        Expands the tree, updates visit values here, and returns the expanded node
        """
        child = MCTNode(action)
        node.addChild(child)
        return child
    
    # Simulation
    def simulate(self, gameState, actions, stop='time'):
        """
        After expansion, let the agent play out randomly or by some method.
        The simulation stops once a time limit is reached, number of actions limit
        is reached, or if game state becomes a terminal beforehand.
        """
        action = None
        # set a time limit for simulation
        if stop == 'time':
            start = time.time()
            while time.time() - start < self.time_limit and not gameState.isWin() and not gameState.isLose():
                legalMoves = gameState.getLegalActions()
                if len(actions) > 0:
                    # Choose the next predetermined action
                    action = actions.pop(0)
                if len(actions) == 0 or not action in legalMoves: # simulated actions here
                    # Choose a random action 
                    # action = random.choice(legalMoves)
                    
                    # Use high score evaluation function to select next move
                    # action = self.highScoreFunction(gameState, legalMoves)
                    
                    # Use project 2 evaluation function to select next move
                    acts = [(act, self.evalFunction(gameState, act)) for act in legalMoves]
                    action = max(acts, key=lambda x:x[1])[0]
                gameState = gameState.generatePacmanSuccessor(action)
            # print(gameState.isWin())
            # print(gameState.isLose())
            # print(gameState.getScore())
            # print('\n')
            if gameState.isLose():
                return False # count as loss
            else:
                return True # count as win
        # set a simulated actions limit
        elif stop == 'action': 
            sim_results = []
            while len(sim_results) < 10 and not gameState.isWin() and not gameState.isLose():
                legalMoves = gameState.getLegalActions()
                if len(actions) > 0:
                    # Choose the next predetermined action
                    action = actions.pop(0)
                if len(actions) == 0 or not action in legalMoves: # simulated actions here
                    # Choose a random action 
                    # action = random.choice(legalMoves)
                    
                    # Use high score evaluation function to select next move
                    # action = self.highScoreFunction(gameState, legalMoves)
                    
                    # Use project 2 evaluation function to select next move
                    acts = [(act, self.evalFunction(gameState, act)) for act in legalMoves]
                    action = max(acts, key=lambda x:x[1])[0]
                gameState = gameState.generatePacmanSuccessor(action)
                sim_results.append(gameState.getScore())
            # print(gameState.isWin())
            # print(gameState.isLose())
            # print(gameState.getScore())
            # print('\n')
            average = sum(sim_results) / len(sim_results)
            if gameState.isLose() or gameState.getScore() < average:
                return False # count as loss
            if gameState.isWin() or gameState.getScore() > average:
                return True # count as win
            
    # Backpropagation
    def backpropagate(self, node, result):
        """
        All the nodes in the tree that are involved in the simulation have
        their statistics updated afterwards.
        """
        leaf = node
        while True: # update stats
            node.visits += 1
            if result:
                node.win += 1
            else:
                node.loss += 1
            
            # reached root node
            if node.id == self.root.id:
                break
            node = node.parent
            
        node = leaf    
        while True: # update UCT scores
            # get max child score
            if len(node.children) != 0:
                node.score = self.best_child(node).score
            else: # leaf
                node.score = self.uct_score(node)
                
            # reached root node
            if node.id == self.root.id:
                break
            node = node.parent
    
    def uct_score(self, node):
        """
        Updates and returns the UCT score of a node
        """
        # UCT score = winratio + c* sqrt( ln(parent total) / (node total)
        win_ratio = node.win / (node.win + node.loss)
        c = math.sqrt(2)
        explore = math.sqrt(math.log((node.parent.visits) / (node.visits)))
        
        node.score = win_ratio + (c * explore)
        # penalize stop actions
        if node.action == Directions.STOP:
            node.score *= 0.5
        # # penalize moving back and forth
        # if self.prevAction != None and self.prevAction != Directions.STOP and node.action == self.prevOpposite(self.prevAction):
        #     node.score *= 0.75
        return node.score
        
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
        while node.id != self.root.id:
            actions.append(node.action)
            node = node.parent
        actions.reverse()
        return actions
    
    def highScoreFunction(self, currentGameState, actions):
        """
        For simulation: evaluation function that returns action that results in 
        highest successor game state score.
        """
        successorScores = [(action, currentGameState.generatePacmanSuccessor(action).getScore()) for action in actions]
        return max(successorScores, key=lambda x:x[1])[0]
        
    def evalFunction(self, currentGameState, action):
        """
        For simulation: Project 2 evaluation function for choosing the best next 
        action chosen actions' sequence is empty.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        # get closest food distance value, i.e. smaller is better
        foodScore = 0
        foods = [manhattanDistance(newPos, foodpos) for foodpos in newFood.asList()]
        if foods: foodScore = min(foods)
        else: foodScore = 1

        # get ghost(s) distance value, i.e. larger is better
        ghostScore = 0
        if len(newGhostStates) > 1: 
            ghostScore = sum([manhattanDistance(newPos, ghost.configuration.pos) for ghost in newGhostStates])
        else: 
            ghostScore = manhattanDistance(newPos, newGhostStates[0].configuration.pos)

        # establish inverse relationship between ghost and food scores
        # i.e. (big ghost score / small food score) is much better than (small ghost score / big food score)
        # return successorGameState.getScore() + (ghostScore / (0.25*foodScore)) #- stopPenalty
        return (ghostScore / len(newGhostStates)) / (foodScore / 2)

    
    
    
    
    
    
    
    