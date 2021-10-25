import json

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

import pandas as pd


#load data function
def dataloading():
    urlowid= "https://covid.ourworldindata.org/data/owid-covid-data.csv"
    data = pd.read_csv(urlowid)
    data['date'] = pd.to_datetime(data['date']) #this helps when creating graphs where x = date
    return data

#create data frame for figure
df = dataloading()
df1 = df[['date', 'new_cases', 'location']]
df2 = df[['date', 'stringency_index', 'location']]
# create graph with data from owid use date as x use new cases for y every 'location' gets different color
fig = px.line(
    df1, x=df1['date'], y=df1['new_cases'], 
    title="corona cases for each country", height=325, color=df['location']
)
#create graph 2 specify the dataframe and what xy labels to use, every country gets own color
fig2 = px.line(
    df2, x='date', y='stringency_index', 
    title="stringency for each", height=325, color=df2['location']
)

# initialize dash
app = dash.Dash(__name__)
#give layout, graphs set at the top give unique id 
app.layout = html.Div([
    dcc.Graph(id="graph", figure=fig),
    dcc.Graph(id="graph2", figure=fig2),
    #idk what this next thing is
    html.Pre(
        id='structure',
        style={
            'border': 'thin lightgrey solid', 
            'overflowY': 'scroll',
            'height': '275px'
        }
    )
])



app.run_server(debug=True)