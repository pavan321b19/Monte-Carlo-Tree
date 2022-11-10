import math
from util import manhattanDistance
from game import Directions
import random, util
import MCTNode

from game import Agent

class MCTSAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """
    
    def __init__(self):
        self.root = MCTNode() # root node of tree used
        self.leaf = None # holds most recently expanded node
    
    # Selection: upper Confidence Bound selection process for agent's next action
    def selectAction(self, gameState):
        # legalMoves = gameState.getLegalActions()
        # 
        # # Choose one of the best actions
        # scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        # bestScore = max(scores)
        # bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        # chosenIndex = random.choice(bestIndices) # Pick randomly among the best
        # 
        # "Add more of your code here if you want to"
        # 
        # return legalMoves[chosenIndex]
        pass
    
    # Expansion: expand agent's tree after selection occurs
    def expandTree(self, gameState):
        # insert...
        # self.leaf = inserted node
        pass
    
    # Simulation: after expansion let the agent play out randomly or by some method
    def simulateActions(self, gameState):
        # legalMoves = gameState.getLegalActions()
        # randomMove = randomly select from legalMoves
        # return randomMove
        pass
        
    # backpropagation to update tree statistics
    def backpropagate(self, gameState):
        # MCTNode.update(self.leaf, gameState.isWin())
        pass
    

    
    
    
    
    
    
    
    
