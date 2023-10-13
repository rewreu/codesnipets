from pyspark.sql import SparkSession
from pyspark.sql.functions import lit
import random
import string
import time
from pyspark.sql import functions as F
from pyspark.sql.types import BooleanType
from pyspark.sql import SparkSession

# Assuming spark is your SparkSession and df is your DataFrame
spark = SparkSession.builder.appName("PerformanceTest").getOrCreate()

# Function to generate random string
def random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

# Function to generate random set of strings
def random_string_set(num_strings, string_length):
    return [random_string(string_length) for _ in range(num_strings)]

# Generate some test data
num_rows = 1000  # number of rows in the DataFrame
num_strings = 10  # number of strings in each collect_set
string_length = 5  # length of each string

data = [(i, random_string_set(num_strings, string_length), random_string_set(num_strings, string_length)) for i in range(num_rows)]

# Create DataFrame
schema = ["id", "AA", "BB"]
df = spark.createDataFrame(data, schema)

# If you want to make sure that AA and BB are indeed sets, you can use the following:
df = df.withColumn("AA", F.array_distinct(df.AA)).withColumn("BB", F.array_distinct(df.BB))

# Show some data to verify
df.show()



# Method 1: Using explode
def method_explode(df):
    def udf_c(str1, str2):
        return str1 in str2 or str2 in str1

    udf_c = F.udf(udf_c, BooleanType())
    df_exploded = df.withColumn("AA_exploded", F.explode(df.AA)).withColumn("BB_exploded", F.explode(df.BB))
    df_with_match = df_exploded.withColumn("substring_match", udf_c(df_exploded.AA_exploded, df_exploded.BB_exploded))

    return df_with_match

# Method 2: Without using explode
def method_no_explode(df):
    def check_substrings(set1, set2):
        for str1 in set1:
            for str2 in set2:
                if str1 in str2 or str2 in str1:
                    return True
        return False

    substring_udf = F.udf(check_substrings, BooleanType())
    df_with_match = df.withColumn("substring_match", substring_udf(df.AA, df.BB))

    return df_with_match

# Timing Method 1
start_time = time.time()
df_method1 = method_explode(df)
df_method1.collect()  # Force evaluation
method1_time = time.time() - start_time

# Timing Method 2
start_time = time.time()
df_method2 = method_no_explode(df)
df_method2.collect()  # Force evaluation
method2_time = time.time() - start_time

# Output the results
print(f'Method 1 (Using explode) took {method1_time:.2f} seconds')
print(f'Method 2 (Without using explode) took {method2_time:.2f} seconds')
