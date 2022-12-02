# This class creates the underlying tree structure utilized by the MCTSAgent that
# directly influences its decision making process. Relevant class functions such as
# creating children for nodes are added here.

import itertools
from enum import Enum

class Tactic(Enum):
	SURVIVAL = 1
	PILL = 2
	GHOST = 3
class MCTNode():
    
    # provides an ID per node
    id = itertools.count()
    
    def __init__(self, position=None, actions=None):
        self.children = []
        self.parent = None

        self.position = position
        
        self.visits = 0
        self.rewards = {Tactic.SURVIVAL: 0., Tactic.PILL: 0., Tactic.GHOST: 0.}  # Tactics based scores
        
        self.actions = actions # list of actions taken to get to this node from the last node
        self.id = next(MCTNode.id)
    
    def addChild(self, child):
        self.children.append(child)
        child.parent = self
    
    # print out node's relations
    def print_relations(self, depth=0):
        print('    '*depth + 'Node ' + str(self.id), end='')
        if self.parent == None:
            print(', Parent None')
        else:
            print(', Parent ' + str(self.parent.id))
        for child in self.children:
            child.print_relations(depth+1)
            
    # print out node's statistics
    def print_stats(self, depth=0, limit=0):
        if depth <= limit:
            print('    '*depth + 'Node ' + str(self.id), ' actions ' + str(self.actions), ' visits ' + str(self.visits), ' rewards ' + str(self.rewards))
            for child in self.children:
                child.print_stats(depth=depth+1, limit=limit)
        else:
            pass

    def apply_discount(self, discount):
        # Apply discount to the pill and survival score, and set ghost score to 0
        self.rewards[Tactic.PILL] *= discount
        self.rewards[Tactic.SURVIVAL] *= discount
        self.rewards[Tactic.GHOST] = 0
        # Apply discount to the visits
        self.visits *= discount
        for child in self.children:
            child.apply_discount(discount)

    def mean_rewards(self):
        # Return the mean rewards for each tactic
        return {tactic: reward/self.visits if self.visits > 0 else 0 for tactic, reward in self.rewards.items()}

    def maximum_mean_reward(self):
        # Return the maximum mean for each reward type from the children
        # If there are no children, or all children have 0 visits, return the current node's rewards
        if sum([child.visits for child in self.children]) == 0:
            return self.mean_rewards()
        # Get the maximum mean reward for each tactic from the children
        # Each tactic has its own maximum mean reward
        return {tactic: max([child.mean_rewards()[tactic] for child in self.children]) for tactic in self.rewards.keys()}

    def get_value(self, tactic):
        # Return the value of the node for the given tactic
        best_rewards = self.maximum_mean_reward()
        if tactic == Tactic.GHOST:
            return best_rewards[Tactic.GHOST] * best_rewards[Tactic.SURVIVAL]
        elif tactic == Tactic.PILL:
            return best_rewards[Tactic.PILL] * best_rewards[Tactic.SURVIVAL]
        elif tactic == Tactic.SURVIVAL:
            return best_rewards[Tactic.SURVIVAL]

    def copy(self):
        # Return a copy of the node
        new_node = MCTNode(self.position, self.actions)
        new_node.visits = self.visits
        new_node.rewards = self.rewards
        for child in self.children:
            new_node.addChild(child.copy())
        return new_node

if __name__ == '__main__':
    root = MCTNode()
    one = MCTNode()
    two = MCTNode()
    three = MCTNode()
    four = MCTNode()
    
    root.addChild(one)
    root.addChild(two)
    one.addChild(three)
    two.addChild(four)
    
    root.print_relations()
    
    root.removeDescendants()
    one = None
    two = None
    three = None
    four = None
    
    try:
        root.print_relations()
        one.print_relations()
    except:
        print('Cannot print relations. Node does not exist.')
    
    
    