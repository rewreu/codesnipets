from pyspark.sql import SparkSession
from graphframes import GraphFrame

spark = SparkSession.builder.appName("GraphFramesExample").getOrCreate()

# Define vertices (nodes)
vertices = spark.createDataFrame([
    ("A", "Alice"),
    ("B", "Bob"),
    ("C", "Charlie"),
    ("D", "David"),
    ("E", "Eve"),
    ("F", "Frank")
], ["id", "name"])

# Define edges (connections between nodes)
edges = spark.createDataFrame([
    ("A", "B"), ("B", "C"),  # A-B-C forms one component
    ("D", "E"), ("E", "F")   # D-E-F forms another component
], ["src", "dst"])

# Create a GraphFrame
g = GraphFrame(vertices, edges)

# Run connected components
result = g.connectedComponents()
result.show()
