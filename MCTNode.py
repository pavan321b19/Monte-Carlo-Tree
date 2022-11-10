# This class creates the underlying tree structure utilized by the MCTSAgent that
# directly influences its decision making process. The mechanism or main steps of
# MCTS are implemented here: Selection, Expansion, Simulation, Backpropagation.

import itertools

class MCTNode():
    
    # provides an ID per node
    id = itertools.count()
    
    def __init__(self, utility=None):
        self.children = []
        self.parent = None
        
        self.utility = utility
        self.visited = 1.
        self.win = 0 # how many games ended as wins going through this node
        self.loss = 0 # how many games ended as losses going through this node
        
        self.action = None # one of pacman's actions
        self.id = next(MCTNode.id)
    
    def addChild(self, child):
        self.children.append(child)
        child.parent = self
    
    # Backpropagates up tree and updates each MC tree node's statistic 
    def update(node, result):
        while True:
            node.visited += 1.

            if result:
                node.win += 1
            else:
                node.loss += 1

            # self.utility += utility
            node.utility /= node.visited

            # reached root node
            if node.parent == None: break
            node = node.parent
    
    # print out node's parent and children
    def print_relations(self):
        if self.parent != None:
            print('Node ' + str(self.id) + '\'s parent is ' + str(self.parent.id))
            print('Node ' + str(self.id) + '\'s children are: ')
        else:
            print('Root node has children: ')
        if len(self.children) == 0:
            print('\tNONE')
        else:
            print(', '.join(str(child.id) for child in self.children))

if __name__ == '__main__':
    root = MCTNode()
    one = MCTNode()
    two = MCTNode()
    
    root.addChild(one)
    root.addChild(two)
    
    root.print_relations()
    two.print_relations()
    
    
    
    