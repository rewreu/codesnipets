

### 1: Graph Setup and Initial Exploration

* Understand the dataset (attributes: name, phones, addresses, zipcodes, IP, emails).
* Load and clean the data; remove duplicates.
* Build initial graph (using NetworkX or similar).
* Initial visualization of the graph (basic layouts).

### 2: Connected Component (CC) Analysis

* Identify and extract connected components.
* Define criteria and filter trivial CCs (pairs, complete graphs, single-attribute).
* Visualize representative examples of filtered vs. meaningful CCs.

### 3: Graph Metrics and Centrality

* Calculate key centrality measures (degree, closeness, betweenness, eigenvector).
* Identify and interpret influential customers based on these metrics.
* Present initial findings and implications.

### 4: Community Detection and Clustering

* Apply community detection algorithms (Louvain, Label Propagation).
* Cluster nodes using embeddings (e.g., node2vec embeddings + K-means or DBSCAN).
* Visualize detected communities and interpret attribute commonalities.

### 5: Node Embeddings and Representation Learning

* Generate embeddings (node2vec, DeepWalk, or Graph Autoencoders).
* Explore different embedding hyperparameters.
* Visualize embeddings (2D projections: PCA or t-SNE).

### 6: Link Prediction (Self-supervised)

* Implement simple graph autoencoder (GAE/VGAE) for link prediction.
* Evaluate model via edge masking and reconstruction accuracy.
* Identify potential hidden or missing links between customers.

### 7: Anomaly Detection and Advanced Analysis

* Identify anomalous or unusual nodes (using isolation forests, autoencoders, or structural metrics).
* Profile anomalous cases and investigate potential reasons.
* Summarize insights and present key anomalies.

### 8: Final Analysis, Documentation, and Presentation

* Summarize all findings (metrics, communities, embeddings, link predictions, anomalies).
* Prepare visualizations and a comprehensive final report.
* Present final results, insights, and suggested actions.

---

**Each should conclude with:**

* Brief progress summary
* Short presentation of results/findings
* Clearly outlined next steps for the following 
