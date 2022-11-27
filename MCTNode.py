# This class creates the underlying tree structure utilized by the MCTSAgent that
# directly influences its decision making process. Relevant class functions such as
# creating children for nodes are added here.

import itertools

class MCTNode():
    
    # provides an ID per node
    id = itertools.count()
    
    def __init__(self, action=None):
        self.children = []
        self.parent = None
        
        self.score = 0. # UCT evaluation based score
        self.visits = 0
        self.win = 0 # how many games ended as wins going through this node
        self.loss = 0 # how many games ended as losses going through this node
        
        self.action = action # root holds none, otherwise holds pacman's action
        self.id = next(MCTNode.id)
    
    def addChild(self, child):
        self.children.append(child)
        child.parent = self
    
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
    
    
    
    