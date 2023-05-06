
import plotly.graph_objs as go
import pandas as pd

# Load data
df = pd.read_csv('data.csv')

# Create list to hold data for each date
data_slider = []

# Create data for each date
for date in df['date'].unique():
    df_date = df[df['date'] == date]
    
    data = dict(
        type='choropleth',
        locations=df_date['state_code'],
        z=df_date['population'],
        text=df_date['population'],
        locationmode='USA-states',
        name=str(date)
    )
    
    data_slider.append(data)

# Create steps for slider
steps = []
for i in range(len(data_slider)):
    step = dict(
        method='restyle',
        args=['visible', [False] * len(data_slider)],
        label=str(df['date'].unique()[i])
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
