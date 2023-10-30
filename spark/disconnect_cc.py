####### checking the connectivity of a subgraph after the removal of certain types of edges
# suppose graph g contains many small connected components. 
# There are two types of edges: A and B. For each connected components, 
# if there is B edge, this code checks if after removing B edge(s), 
# will this make one connect components into multiple connect components

from pyspark.sql.functions import col

# Calculate the initial connected components
components = g.connectedComponents()

# For each connected component:
unique_components = components.select('component').distinct().collect()
for comp in unique_components:
    # Filter the subgraph corresponding to this component
    comp_id = comp['component']
    subgraph_vertices = components.filter(col('component') == comp_id)
    subgraph_edges = g.edges.join(subgraph_vertices, g.edges.src == subgraph_vertices.id, 'inner')

    # Check if the subgraph has 'B' type edges
    if subgraph_edges.filter(col('relationship') == 'B').count() > 0:
        # Remove 'B' edges and check the connected components of the subgraph
        subgraph_without_B_edges = subgraph_edges.filter(col('relationship') != 'B')
        subgraph = GraphFrame(subgraph_vertices, subgraph_without_B_edges)
        
        new_components = subgraph.connectedComponents()
        
        # If the number of unique components increases after removing 'B' edges, 
        # then those edges were crucial for connectivity
        if new_components.select('component').distinct().count() > 1:
            print(f"Component {comp_id} will be disconnected by removing 'B' edges")
