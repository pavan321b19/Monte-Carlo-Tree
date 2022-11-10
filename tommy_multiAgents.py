# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import math
from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"

        distToClosestFood = min(
            [math.inf] + [manhattanDistance(newPos, (x, y)) for (x, y) in newFood.asList()])

        distToClosestAngryGhost = min([math.inf] + [manhattanDistance(newPos, ghostState.getPosition())
                                                    for ghostState in newGhostStates if ghostState.scaredTimer == 0])

        if distToClosestAngryGhost <= 1:
            return -math.inf

        score = -len(newFood.asList()) + 1/distToClosestFood

        return score
def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"

        def minimax(state, depth, agentIndex):
            if state.isWin() or state.isLose() or depth == 0:
                return (None, self.evaluationFunction(state))
            next_agent = (agentIndex + 1) % state.getNumAgents()
            if next_agent == 0:
                depth -= 1
            selector = max if agentIndex == 0 else min
            best_action = None
            best_score = -math.inf if agentIndex == 0 else math.inf
            for action in state.getLegalActions(agentIndex):
                (_, score) = minimax(state.generateSuccessor(agentIndex, action), depth, next_agent)
                if selector(score, best_score) == score:
                    best_action = action
                    best_score = score
            return (best_action, best_score)
        
        return minimax(gameState, self.depth, 0)[0]
class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"

        def minimax(state, depth, agentIndex, alpha, beta):
            if state.isWin() or state.isLose() or depth == 0:
                return (None, self.evaluationFunction(state))
            next_agent = (agentIndex + 1) % state.getNumAgents()
            if next_agent == 0:
                depth -= 1
            selector = max if agentIndex == 0 else min
            best_action = None
            best_score = -math.inf if agentIndex == 0 else math.inf
            for action in state.getLegalActions(agentIndex):
                (_, score) = minimax(state.generateSuccessor(
                    agentIndex, action), depth, next_agent, alpha, beta)
                if selector(score, best_score) == score:
                    best_action = action
                    best_score = score
                if agentIndex == 0:
                    if score > beta:
                        return (action, score)
                    alpha = max(alpha, score)
                else:
                    if score < alpha:
                        return (action, score)
                    beta = min(beta, score)
            return (best_action, best_score)

        return minimax(gameState, self.depth, 0, -math.inf, math.inf)[0]

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"

        def expectimax(state, depth, agentIndex):
            if state.isWin() or state.isLose() or depth == 0:
                return (None, self.evaluationFunction(state))
            next_agent = (agentIndex + 1) % state.getNumAgents()
            if next_agent == 0:
                depth -= 1
            result_action = None
            result_score = -math.inf if agentIndex == 0 else 0
            for action in state.getLegalActions(agentIndex):
                (_, score) = expectimax(state.generateSuccessor(
                    agentIndex, action), depth, next_agent)
                if agentIndex == 0:
                    if max(score, result_score) == score:
                        result_action = action
                        result_score = score
                else:
                    result_score += (score / len(state.getLegalActions(agentIndex)))
                
            return (result_action, result_score)

        return expectimax(gameState, self.depth, 0)[0]

