import matplotlib.pyplot as plt
import networkx as nx

class Tree:
    def __init__(self, key, left=None, right=None):
        self.key = key
        self.left = left
        self.right = right

def inorder_layout(tree):
    pos = {}
    def traverse(node, depth=0, pos=pos):
        if node.left:
            traverse(node.left, depth + 1)
        pos[node.key] = (len(pos), -depth)  # horizontal position is number of nodes visited so far
        if node.right:
            traverse(node.right, depth + 1)
    traverse(tree)
    return pos

def build_graph(tree):
    edges = []
    labels = {}
    def traverse(node):
        nonlocal edges, labels
        if node is None:
            return
        if node.left:
            edges.append((node.key, node.left.key))
            labels[(node.key, node.left.key)] = 'yes'
            traverse(node.left)
        if node.right:
            edges.append((node.key, node.right.key))
            labels[(node.key, node.right.key)] = 'not'
            traverse(node.right)
    traverse(tree)
    return edges, labels

# construct a more complicated tree for demonstration
t = Tree('A not match',
         Tree('B not match', Tree('D not match', Tree('H match'), Tree('I match')), Tree('E match', Tree('J match'))),
         Tree('C match', Tree('F match', Tree('K match')), Tree('G match', Tree('L match'),Tree('MD match', Tree('MH match'), Tree('MI match')))))

edges, edge_labels = build_graph(t)
pos = inorder_layout(t)

G = nx.DiGraph()
G.add_edges_from(edges)
plt.figure(figsize=(10, 10))
nx.draw(G, pos, with_labels=True, arrows=False, node_size=3000, node_color='white', font_weight='bold', linewidths=2.0)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
plt.show()
