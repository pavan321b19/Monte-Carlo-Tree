import math
import time
import random
from mctNode import MCTNode

from game import Agent

class MCTSAgent(Agent):
    """
    A MCTS agent's decision making is implemented with a decision tree, and it also involves some randomness. Every time an action is chosen, it simulates the rest of the game to help evaluate the actions chosen. It is expected for the agent to simulate the game numerous times in order to evaluate its decisions.
    
    The mechanism or main steps of MCTS are implemented here: Selection, Expansion, Simulation, Backpropagation.
    """
    
    def __init__(self):
        self.root = MCTNode(None) # root node of tree used for MCTS
        self.threshold = 10 # minimum number of times each child is visited before using UCT to choose
        self.time_limit = 1 # time limit to choose action in seconds

    def getAction(self, gameState):
        """
        Returns the next action the agent will take
        """
        start = time.time()
        while time.time() - start < self.time_limit:
            leaf_node = self.select(gameState)
            actions = self.get_actions(leaf_node)
            result = self.simulate(gameState, actions)
            self.backpropagate(leaf_node, result)

        # Update the root node
        self.root = self.best_child(self.root)

        best_action = self.root.action

        # Update root for tree reuse

        self.root.parent = None
        self.root.action = None

        # Return the best action
        return best_action

    # Selection: selects the next leaf node to simulate
    def select(self, gameState):
        node = self.root
        while True:
            legalMoves = gameState.getLegalActions()
            # reaching a leaf, expand randomly
            if len(node.children) < len(legalMoves): # if len(node.children) == 0:
                # unvisited actions
                # each child is a node with an action
                #node.children is an array of nodes
                unvisited = [action for action in legalMoves if not any(child.action == action for child in node.children)]
                action = random.choice(unvisited)
                return self.expand(node, action)
            else:
                if node.visits < self.threshold:
                    node = random.choice(node.children)
                else:
                    node = self.best_child(node)
            gameState = gameState.generatePacmanSuccessor(node.action)
         
        # score = successorGameState.getScore()
        # 
        # # Choose one of the best actions
        # scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        # bestScore = max(scores)
        # bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        # chosenIndex = random.choice(bestIndices) # Pick randomly among the best
    
    # Expansion: expand agent's tree after selection occurs
    def expand(self, node, action):
        # first check if child exists or not
        for child in node.children:
            if child.action == action:
                return
        child = MCTNode(action)
        node.addChild(child)
        return child
    
    # Simulation: after expansion let the agent play out randomly or by some method
    def simulate(self, gameState, actions):
        # start game with self.actions from gamestate
        # randomly choose actions until game ends or using an evaluation function of sorts
        # return win/loss

        while not gameState.isWin() and not gameState.isLose():
            legalMoves = gameState.getLegalActions()
            action = None
            if len(actions) > 0:
                # Choose the next predetermined action
                action = actions.pop(0)
            if not action in legalMoves:
                # Choose a random action
                action = random.choice(legalMoves)
            
            gameState = gameState.generatePacmanSuccessor(action)

        return gameState.isWin()
        
    # Backpropagation: update tree nodes' statistics
    def backpropagate(self, node, result): # backpropagate(self, simulation):
        # self.leaf.update(simulation.isWin())
        # self.leaf.update(gameState.isWin())
        
        while True:
            node.visits += 1
            
            if result:
                node.win += 1
            else:
                node.loss += 1
            
            # reached root node
            if node.id == self.root.id:
                break
        
            node = node.parent

    def best_child(self, node):
        """
        Returns the best child of a node
        """
        return max(node.children, key=lambda child: self.uct_score(child))

    def uct_score(self, node):
        """
        Returns the UCT score of a node
        """
        # UCT score = winratio + c* sqrt( ln(parent total) / (node total)
        win_ratio = node.win / (node.win + node.loss)
        c = math.sqrt(2)
        explore = math.sqrt(math.log(node.parent.visits) / (node.visits))
        return win_ratio + (c * explore)

    def get_actions(self, node):
        # Traverse the tree starting from node upwards to the root constructing a sequence of actions
        actions = []
        while node.parent is not None:
            actions.append(node.action)
            node = node.parent
        actions.reverse()
        return actions
    

    
    
    
    
    
    
    
    
