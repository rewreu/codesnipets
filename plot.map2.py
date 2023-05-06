Unfortunately, it is not possible to add text annotations directly on a choropleth map using Plotly. However, you can use the `scattergeo` trace type to add text annotations to the map by setting the `lat` and `lon` parameters to the latitude and longitude coordinates of the state centroids and setting the `text` parameter to the population data. Here's an example code that shows how to do this:

```python
import plotly.graph_objs as go
import pandas as pd

# Load data
df = pd.read_csv('data.csv')

# Create list to hold data for each date
data_slider = []

# Create data for each date
for date in df['date'].unique():
    df_date = df[df['date'] == date]
    
    # Create choropleth trace
    choropleth = dict(
        type='choropleth',
        locations=df_date['state_code'],
        z=df_date['population'],
        locationmode='USA-states',
        name=str(date),
        hoverinfo='location+z'
    )
    
    # Create scattergeo trace for text annotations
    scattergeo = dict(
        type='scattergeo',
        lat=df_date['latitude'],
        lon=df_date['longitude'],
        text=df_date['population'],
        mode='text',
        showlegend=False,
        hoverinfo='none'
    )
    
    data_slider.append([choropleth, scattergeo])

# Create steps for slider
steps = []
for i in range(len(data_slider)):
    step = dict(
        method='restyle',
        args=['visible', [False] * len(data_slider) * 2],
        label=str(df['date'].unique()[i])
    )
    step['args'][1][i * 2] = True
    step['args'][1][i * 2 + 1] = True
    steps.append(step)

# Flatten data_slider list
data_slider = [trace for traces in data_slider for trace in traces]

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
```

This code is similar to the previous example, but with the addition of creating a `scattergeo` trace for each date to add text annotations to the map. The `lat` and `lon` parameters of the `scattergeo` trace are set to the latitude and longitude coordinates of the state centroids and the `text` parameter is set to the population data. This will display the population number for each state on the choropleth map.

I hope this helps! Let me know if you have any questions.
