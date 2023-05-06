
import plotly.graph_objs as go
import pandas as pd

# Load data
df = pd.read_csv('data.csv')

# Create list to hold data for each year
data_slider = []

# Create data for each year
for year in df['year'].unique():
    df_year = df[df['year'] == year]
    
    data = dict(
        type='choropleth',
        locations=df_year['state_code'],
        z=df_year['population'],
        locationmode='USA-states',
        name=str(year)
    )
    
    data_slider.append(data)

# Create steps for slider
steps = []
for i in range(len(data_slider)):
    step = dict(
        method='restyle',
        args=['visible', [False] * len(data_slider)],
        label=str(i + df['year'].min())
    )
    step['args'][1][i] = True
    steps.append(step)

# Create layout with slider
layout = dict(
    title='US Population by State',
    geo=dict(scope='usa'),
    sliders=[dict(steps=steps)]
)

# Create figure
fig = go.Figure(data=data_slider, layout=layout)

# Show figure
fig.show()
