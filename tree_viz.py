from graphviz import Digraph

class Tree:
    def __init__(self, key, left=None, right=None):
        self.key = key
        self.left = left
        self.right = right

def visualize_tree(tree):
    if tree is None:
        return "Nothing in the tree!"
    graph = Digraph('binary_tree')
    graph.attr('node', shape='box')  # this line sets the node shape to box
    _add_to_graphviz(graph, tree)
    return graph

def _add_to_graphviz(graph, tree, parent_id=None, label=None):
    if tree is None:
        return
    tree_id = hash(tree)
    graph.node(str(tree_id), str(tree.key))
    if parent_id is not None:
        graph.edge(str(parent_id), str(tree_id), label=label, fontsize='10') # specify fontsize here
    _add_to_graphviz(graph, tree.left, tree_id, label='left')
    _add_to_graphviz(graph, tree.right, tree_id, label='right')

# Create a tree
# Create a more complex tree
t = Tree('A',
         Tree('B', 
              Tree('D', Tree('H'), Tree('I')), 
              Tree('E', Tree('J'))),
         Tree('C',
              Tree('F', Tree('K')),
              Tree('G', None, Tree('M'))))

# Visualize the tree
dot = visualize_tree(t)
dot.view()


# Visualize the tree
dot = visualize_tree(t)
dot.view()
