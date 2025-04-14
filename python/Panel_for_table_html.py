import pandas as pd
import panel as pn
pn.extension('tabulator')

# Create sample data
df1 = pd.DataFrame({
    'Date': pd.to_datetime(['2025-04-14', '2025-04-13']),
    'Value': [100, 200]
})

df2 = pd.DataFrame({
    'Category': ['A', 'B', 'C'],
    'Score': [90, 85, 92]
})

# Create tables
table1 = pn.widgets.Tabulator(df1, show_index=False, frozen_columns=['Date'], width=500, height=200)
table2 = pn.widgets.Tabulator(df2, show_index=False, width=500, height=200)

# Add titles and descriptions
section1 = pn.Column(
    "# Table 1: Dates and Values",
    "This table shows some example data with dates and values.",
    table1
)

section2 = pn.Column(
    "# Table 2: Categories and Scores",
    "Here is another table with categories and scores.",
    table2
)

# Combine into one layout
layout = pn.Column(section1, pn.Spacer(height=30), section2)

# Save to standalone HTML file
layout.save("multi_tables.html", embed=True)

# To preview in notebook/script (optional)
layout.show()
