def print_tree(tree, node=0, indent=""):
    depth = tree.depth
    # Determine if node index corresponds to a leaf.
    if node >= (2**depth - 1):
        leaf_idx = node - (2**depth - 1)
        print(indent + f"Leaf: {tree.leaf_node_labels[leaf_idx]}")
    else:
        feature_idx = tree.auto_dims[node].argmax().item()
        threshold = tree.auto_thresholds[node].item()
        print(indent + f"Node {node}: X[{feature_idx}] < {threshold:.3f}?")
        # Print True branch
        print(indent + "  True ->")
        print_tree(tree, 2*node+1, indent + "    ")
        # Print False branch
        print(indent + "  False ->")
        print_tree(tree, 2*node+2, indent + "    ")

# Usage example:
# print_tree(your_decision_tree)

import graphviz

def visualize_decision_tree(tree):
    """
    Visualizes a custom DecisionTree instance using Graphviz.
    Assumes:
      - tree.auto_dims is a list of tensors for internal nodes,
      - tree.auto_thresholds is a list of tensors for internal nodes,
      - tree.leaf_node_labels is a list of leaf node predictions.
      - The binary tree structure follows: for node i, left child is 2*i+1, right child is 2*i+2.
    """
    depth = tree.depth
    dot = graphviz.Digraph()
    
    # Add internal nodes: indices 0 to (2**depth - 2) (total 2**depth - 1 nodes)
    for i in range(2**depth - 1):
        # Extract a representative feature index and threshold value.
        # Here we assume auto_dims[i] is a tensor; we take the argmax value as the feature index.
        feature_idx = tree.auto_dims[i].argmax().item()
        threshold = tree.auto_thresholds[i].item()
        label = f"X[{feature_idx}] < {threshold:.3f}"
        dot.node(str(i), label)
    
    # Add leaf nodes: indices from 2**depth - 1 to 2**(depth+1) - 2
    for i in range(2**depth - 1, 2**(depth+1) - 1):
        # Map to leaf index in leaf_node_labels list.
        leaf_idx = i - (2**depth - 1)
        # For visualization, you might want to convert the tensor to a list or value.
        leaf_label = tree.leaf_node_labels[leaf_idx]
        dot.node(str(i), f"Leaf: {leaf_label}")
    
    # Add edges for internal nodes
    for i in range(2**depth - 1):
        left = 2*i + 1
        right = 2*i + 2
        dot.edge(str(i), str(left), label="True")
        dot.edge(str(i), str(right), label="False")
    
    return dot

# Usage example:
# viz = visualize_decision_tree(your_decision_tree)
# viz.render("tree_visualization", format="png", view=True)
