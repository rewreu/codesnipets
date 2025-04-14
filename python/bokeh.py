from bokeh.models import ColumnDataSource, DataTable, TableColumn, Panel, Tabs
from bokeh.plotting import show
from bokeh.io import output_notebook

output_notebook()

# Table 1 with 2 rows
data1 = dict(name=["Alice", "Bob"], age=[25, 30])
source1 = ColumnDataSource(data1)
columns1 = [
    TableColumn(field="name", title="Name"),
    TableColumn(field="age", title="Age"),
]
table1 = DataTable(source=source1, columns=columns1, width=400, height=200)

# Table 2 with 3 rows
data2 = dict(city=["New York", "Los Angeles", "Chicago"], population=[8000000, 4000000, 2700000])
source2 = ColumnDataSource(data2)
columns2 = [
    TableColumn(field="city", title="City"),
    TableColumn(field="population", title="Population"),
]
table2 = DataTable(source=source2, columns=columns2, width=400, height=200)

# Create tabs
tab1 = Panel(child=table1, title="People")
tab2 = Panel(child=table2, title="Cities")
tabs = Tabs(tabs=[tab1, tab2])

show(tabs)
