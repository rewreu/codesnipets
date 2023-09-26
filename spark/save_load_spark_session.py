# Save Configuration to a JSON File:
import json

confs = spark.sparkContext.getConf().getAll()
conf_dict = dict(confs)

with open('spark_config.json', 'w') as file:
    json.dump(conf_dict, file, indent=4)

# read from json
from pyspark.sql import SparkSession
import json

with open('spark_config.json', 'r') as file:
    conf_dict = json.load(file)

builder = SparkSession.builder.appName("YourAppName")
for k, v in conf_dict.items():
    builder = builder.config(k, v)
spark_new = builder.getOrCreate()
