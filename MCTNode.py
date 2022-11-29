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
        
        self.visits = 0
        self.win = 0 # how many games ended as wins going through this node
        self.loss = 0 # how many games ended as losses going through this node
        self.score = 0. # UCT based score
        
        self.action = action # root holds none, otherwise holds pacman's action
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
            print('    '*depth + 'Node ' + str(self.id), ' action ' + str(self.action), ' visits ' + str(self.visits), ' score ' + str(self.score))
            for child in self.children:
                child.print_stats(depth=depth+1, limit=limit)
        else:
            pass
            
    # clear the node and descendants of their stats and relationships (except action)
    def reset(self):
        for child in self.children:
            child.reset()
        self.children.clear()
        self.parent = None
        
        self.visits = 0
        self.win = 0
        self.loss = 0
        self.score = 0.

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
    
    
    