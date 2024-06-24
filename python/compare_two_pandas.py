import pandas as pd

# Example DataFrames
data1 = {'A': [1, 2, 3, 4, 5], 'B': [5, 6, 7, 8, 9], 'C': [9, 8, 7, 6, 5]}
data2 = {'A': [1, 2, 3, 4, 5], 'B': [5, 6, 7, 8, 9], 'C': [9, 8, 7, 6, 5]}

df1 = pd.DataFrame(data1)
df2 = pd.DataFrame(data2)

# Perform an inner join on column 'A'
merged_df = pd.merge(df1, df2, on='A', suffixes=('_df1', '_df2'))

# Compare all other columns
comparison_results = (merged_df.filter(like='_df1').values == merged_df.filter(like='_df2').values).all(axis=1)

# Check if all rows are equal
all_equal = comparison_results.all()
print(f"All rows in the other columns are equal: {all_equal}")

# If you want to see which rows or columns are different, you can inspect the comparison results
print(merged_df[~comparison_results])
