import math
from util import manhattanDistance
from game import Directions
import random, util
import MCTNode

from game import Agent

class MCTSAgent(Agent):
    """
    A MCTS agent's decision making is implemented with a decision tree, and it also involves some randomness. Every time an action is chosen, it simulates the rest of the game to help evaluate the actions chosen. It is expected for the agent to simulate the game numerous times in order to evaluate its decisions.
    
    The mechanism or main steps of MCTS are implemented here: Selection, Expansion, Simulation, Backpropagation.
    """
    
    def __init__(self):
        self.root = MCTNode(None) # root node of tree used
        self.leaf = None # holds most recently expanded node
        self.threshold = 10 # minimum number of times each child is visited before using UCT to choose
        
        self.actions = [] # sequence of chosen actions for simulation

    # Selection: selection process for agent's next action
    def selectAction(self, gameState):
        self.actions.clear() # clear current action sequence for next simulation
        node = self.root
        while True:
            if node.action != None:
                self.actions.append(node.action)
            legalMoves = gameState.getLegalActions()
            # reaching a leaf, expand randomly
            if len(node.children) < len(legalMoves): # if len(node.children) == 0:
                rand = random.randint(0, len(legalMoves)-1)
                expandTree(node, legalMoves[rand])
                return legalMoves[rand]
            else:
                # if all children's visits less than threshold, randomly select amongst them
                if all(child.visits < self.threshold for child in node.children):
                    rand = random.randint(0, len(node.children)-1)
                    node = node.children[rand]
                else:
                    children = [(child, child.score) for child in node.children]
                    node = max(children, key=lambda x:x[1])[0]
            gameState = gameState.generatePacmanSuccessor(node.action)
         
        # score = successorGameState.getScore()
        # 
        # # Choose one of the best actions
        # scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        # bestScore = max(scores)
        # bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        # chosenIndex = random.choice(bestIndices) # Pick randomly among the best
    
    # Expansion: expand agent's tree after selection occurs
    def expandTree(self, node, action):
        # first check if child exists or not
        for child in node.children:
            if child.action == action:
                self.leaf = child
                break
        else:
            expand = MCTNode(action)
            node.addChild(expand)
            self.leaf = expand
    
    # Simulation: after expansion let the agent play out randomly or by some method
    def simulateActions(self):
        # start game with self.actions
        # randomly choose actions until game ends or using an evaluation function of sorts
        # return win/loss
        pass
        
    # Backpropagation: update tree nodes' statistics (UCT scores are updated here too)
    def backpropagate(self, gameState): # backpropagate(self, simulation):
        # self.leaf.update(simulation.isWin())
        # self.leaf.update(gameState.isWin())
        
        node = self.leaf
        # result = simulation.isWin()
        while True:
            node.visits += 1
            
            if result:
                node.win += 1
            else:
                node.loss += 1
            
            # reached root node
            if node.id == self.root.id:
                break
            
            # UCT score = winratio + c* sqrt( ln(parent total) / (node total) )
            win_ratio = node.win / (node.win + node.loss)
            c = math.sqrt(2)
            explore = math.sqrt(math.log(node.parent.visits + 1) / (node.visits))
            self.score = win_ration + c* explore
        
            node = node.parent
    

    
    
    
    
    
    
    
    
