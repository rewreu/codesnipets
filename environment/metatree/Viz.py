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
def print_tree(tree, node=0, indent=""):
    depth = tree.depth
    # Check if node index corresponds to a leaf.
    if node >= (2**depth - 1):
        leaf_idx = node - (2**depth - 1)
        # Convert tensor to list for a clear multi-class display.
        leaf_values = tree.leaf_node_labels[leaf_idx].squeeze().tolist()
        formatted_leaf = "[" + ", ".join(f"{v:.2f}" for v in leaf_values) + "]"
        print(indent + f"Leaf: {formatted_leaf}")
    else:
        feature_idx = tree.auto_dims[node].argmax().item()
        threshold = tree.auto_thresholds[node].item()
        print(indent + f"Node {node}: X[{feature_idx}] < {threshold:.3f}?")
        # Print True branch
        print(indent + "  True ->")
        print_tree(tree, 2 * node + 1, indent + "    ")
        # Print False branch
        print(indent + "  False ->")
        print_tree(tree, 2 * node + 2, indent + "    ")

# Example usage:
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


import graphviz

def visualize_decision_tree(tree):
    """
    Visualizes a custom DecisionTree instance using Graphviz.
    
    Assumptions:
      - tree.auto_dims is a list of tensors for internal (decision) nodes.
      - tree.auto_thresholds is a list of tensors for internal nodes.
      - tree.leaf_node_labels is a list of leaf node predictions (as tensors).
      - The binary tree structure follows: for a node at index i,
          left child is at 2*i + 1 and right child at 2*i + 2.
      - For multi-class outputs, each leaf holds a vector (e.g., probability distribution).
    """
    depth = tree.depth
    dot = graphviz.Digraph()

    # Add internal (decision) nodes: indices 0 to (2**depth - 2)
    for i in range(2**depth - 1):
        # Use the argmax of the tensor from auto_dims as a representative feature index.
        feature_idx = tree.auto_dims[i].argmax().item()
        threshold = tree.auto_thresholds[i].item()
        label = f"X[{feature_idx}] < {threshold:.3f}?"
        dot.node(str(i), label)

    # Add leaf nodes: indices from 2**depth - 1 to 2**(depth+1) - 2
    for i in range(2**depth - 1, 2**(depth+1) - 1):
        leaf_idx = i - (2**depth - 1)
        leaf_tensor = tree.leaf_node_labels[leaf_idx]
        # Squeeze to remove extra dimensions and convert to a list
        leaf_values = leaf_tensor.squeeze().tolist()
        # If there's only one value, ensure it's in list form
        if not isinstance(leaf_values, list):
            leaf_values = [leaf_values]
        # Format each value to two decimal places
        formatted_leaf = "[" + ", ".join(f"{v:.2f}" for v in leaf_values) + "]"
        dot.node(str(i), f"Leaf: {formatted_leaf}")

    # Add edges from each decision node to its left (True) and right (False) children
    for i in range(2**depth - 1):
        left = 2 * i + 1
        right = 2 * i + 2
        dot.edge(str(i), str(left), label="True")
        dot.edge(str(i), str(right), label="False")

    return dot

# Example usage:
# viz = visualize_decision_tree(your_decision_tree)
# viz.render("tree_visualization", format="png", view=True)


import graphviz

def visualize_decision_tree(tree, split_threshold=3):
    """
    Visualizes a custom DecisionTree instance using Graphviz.

    Parameters:
      - tree: an instance of your DecisionTree.
      - split_threshold: if the number of values in a leaf exceeds this, split into two lines.
      
    Assumptions:
      - tree.auto_dims is a list of tensors for internal (decision) nodes.
      - tree.auto_thresholds is a list of tensors for internal nodes.
      - tree.leaf_node_labels is a list of leaf node predictions (as tensors).
      - The binary tree structure follows: for a node at index i,
          left child is at 2*i + 1 and right child at 2*i + 2.
      - For multi-class outputs, each leaf holds a vector (e.g., probability distribution).
    """
    depth = tree.depth
    dot = graphviz.Digraph()

    # Add internal (decision) nodes: indices 0 to (2**depth - 2)
    for i in range(2**depth - 1):
        feature_idx = tree.auto_dims[i].argmax().item()
        threshold = tree.auto_thresholds[i].item()
        label = f"X[{feature_idx}] < {threshold:.3f}?"
        dot.node(str(i), label)

    # Add leaf nodes: indices from 2**depth - 1 to 2**(depth+1) - 2
    for i in range(2**depth - 1, 2**(depth+1) - 1):
        leaf_idx = i - (2**depth - 1)
        leaf_tensor = tree.leaf_node_labels[leaf_idx]
        leaf_values = leaf_tensor.squeeze().tolist()
        if not isinstance(leaf_values, list):
            leaf_values = [leaf_values]

        # If there are more than split_threshold values, split into two lines.
        if len(leaf_values) > split_threshold:
            half = len(leaf_values) // 2 + len(leaf_values) % 2
            first_line = ", ".join(f"{v:.2f}" for v in leaf_values[:half])
            second_line = ", ".join(f"{v:.2f}" for v in leaf_values[half:])
            formatted_leaf = f"[{first_line}]\n[{second_line}]"
        else:
            formatted_leaf = "[" + ", ".join(f"{v:.2f}" for v in leaf_values) + "]"
            
        dot.node(str(i), f"Leaf:\n{formatted_leaf}")

    # Add edges for internal nodes.
    for i in range(2**depth - 1):
        left = 2 * i + 1
        right = 2 * i + 2
        dot.edge(str(i), str(left), label="True")
        dot.edge(str(i), str(right), label="False")

    return dot

# Example usage:
# viz = visualize_decision_tree(your_decision_tree)
# viz.render("tree_visualization", format="png", view=True)

import graphviz

def visualize_decision_tree(tree, vertical_threshold=10):
    """
    Visualizes a custom DecisionTree instance using Graphviz.

    Parameters:
      - tree: an instance of your DecisionTree.
      - vertical_threshold: if the number of values in a leaf is >= this threshold,
                            each element will be printed on its own line.

    Assumptions:
      - tree.auto_dims is a list of tensors for internal (decision) nodes.
      - tree.auto_thresholds is a list of tensors for internal nodes.
      - tree.leaf_node_labels is a list of leaf node predictions (as tensors).
      - The binary tree structure follows: for a node at index i,
          left child is at 2*i + 1 and right child at 2*i + 2.
      - For multi-class outputs, each leaf holds a vector (e.g., probability distribution).
    """
    depth = tree.depth
    dot = graphviz.Digraph()

    # Add internal (decision) nodes: indices 0 to (2**depth - 2)
    for i in range(2**depth - 1):
        feature_idx = tree.auto_dims[i].argmax().item()
        threshold = tree.auto_thresholds[i].item()
        label = f"X[{feature_idx}] < {threshold:.3f}?"
        dot.node(str(i), label)

    # Add leaf nodes: indices from 2**depth - 1 to 2**(depth+1) - 2
    for i in range(2**depth - 1, 2**(depth+1) - 1):
        leaf_idx = i - (2**depth - 1)
        leaf_tensor = tree.leaf_node_labels[leaf_idx]
        leaf_values = leaf_tensor.squeeze().tolist()
        if not isinstance(leaf_values, list):
            leaf_values = [leaf_values]
        
        # If the number of elements is >= vertical_threshold, show each on a separate line.
        if len(leaf_values) >= vertical_threshold:
            formatted_leaf = "\n".join(f"{v:.2f}" for v in leaf_values)
        else:
            formatted_leaf = "[" + ", ".join(f"{v:.2f}" for v in leaf_values) + "]"
            
        dot.node(str(i), f"Leaf:\n{formatted_leaf}")

    # Add edges for internal nodes.
    for i in range(2**depth - 1):
        left = 2 * i + 1
        right = 2 * i + 2
        dot.edge(str(i), str(left), label="True")
        dot.edge(str(i), str(right), label="False")

    return dot

# Example usage:
# viz = visualize_decision_tree(your_decision_tree)
# viz.render("tree_visualization", format="png", view=True)


import graphviz

def visualize_decision_tree(tree, vertical_threshold=10, leaf_fontsize="8"):
    """
    Visualizes a custom DecisionTree instance using Graphviz.

    Parameters:
      - tree: an instance of your DecisionTree.
      - vertical_threshold: if the number of values in a leaf is >= this threshold,
                            each element will be printed on its own line.
      - leaf_fontsize: the font size (as a string) to use for leaf node text.

    Assumptions:
      - tree.auto_dims is a list of tensors for internal (decision) nodes.
      - tree.auto_thresholds is a list of tensors for internal nodes.
      - tree.leaf_node_labels is a list of leaf node predictions (as tensors).
      - The binary tree structure follows: for a node at index i,
          left child is at 2*i + 1 and right child at 2*i + 2.
      - For multi-class outputs, each leaf holds a vector (e.g., probability distribution).
    """
    depth = tree.depth
    dot = graphviz.Digraph()

    # Add internal (decision) nodes: indices 0 to (2**depth - 2)
    for i in range(2**depth - 1):
        feature_idx = tree.auto_dims[i].argmax().item()
        threshold = tree.auto_thresholds[i].item()
        label = f"X[{feature_idx}] < {threshold:.3f}?"
        dot.node(str(i), label)

    # Add leaf nodes: indices from 2**depth - 1 to 2**(depth+1) - 2
    for i in range(2**depth - 1, 2**(depth+1) - 1):
        leaf_idx = i - (2**depth - 1)
        leaf_tensor = tree.leaf_node_labels[leaf_idx]
        leaf_values = leaf_tensor.squeeze().tolist()
        if not isinstance(leaf_values, list):
            leaf_values = [leaf_values]
        
        # Format the leaf text vertically if the vector is long enough.
        if len(leaf_values) >= vertical_threshold:
            formatted_leaf = "\n".join(f"{v:.2f}" for v in leaf_values)
        else:
            formatted_leaf = "[" + ", ".join(f"{v:.2f}" for v in leaf_values) + "]"
            
        # Set a smaller font size for leaf nodes.
        dot.node(str(i), f"Leaf:\n{formatted_leaf}", fontsize=leaf_fontsize)

    # Add edges from each decision node to its left (True) and right (False) children.
    for i in range(2**depth - 1):
        left = 2 * i + 1
        right = 2 * i + 2
        dot.edge(str(i), str(left), label="True")
        dot.edge(str(i), str(right), label="False")

    return dot

# Example usage:
# viz = visualize_decision_tree(your_decision_tree)
# viz.render("tree_visualization", format="png", view=True)
