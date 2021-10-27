import json

import dash
#import dash_core_components as dcc
from dash import dcc
#import dash_html_components as html
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px

import pandas as pd
import numpy as np

#load data function
def dataloading():
    urlowid= "https://covid.ourworldindata.org/data/owid-covid-data.csv"
    data = pd.read_csv(urlowid)
    data['date'] = pd.to_datetime(data['date']) #this helps when creating graphs where x = date
    return data

def dataNL(df):
    NLdata = df.loc[df.location == "Netherlands", "location"]
    NLdata = pd.merge(NLdata, df)
    return NLdata

def dataSWE(df):
    SWEdata = df.loc[df.location == "Sweden", "location"]
    SWEdata = pd.merge(SWEdata, df)
    return SWEdata

def dataAUS(df):
    AUSdata = df.loc[df.location == "Australia", "location"]
    AUSdata = pd.merge(AUSdata, df)
    return AUSdata

#create dataframes
df = dataloading()
NLdata = dataNL(df)
SWEdata = dataSWE(df)
AUSdata = dataAUS(df)
frames = [NLdata, SWEdata, AUSdata]
threecountries = pd.concat(frames)
print(threecountries)

#create dfs for figures in dropdown
df1 = NLdata[['date', 'new_cases', 'location', 'stringency_index']]
df2 = NLdata[['date', 'stringency_index', 'location', 'new_cases']]
# create graph with data from owid use date as x use new cases for y every 'location' gets different color
fig37 = px.line(
    threecountries, x='date', y='new_cases', color='location',
    title="corona cases for each country", height=450
)
#create graph 2 specify the dataframe and what xy labels to use, every country gets own color
fig2 = px.line(
    threecountries, x='date', y='stringency_index', color='location',
    title="stringency for each", height=450
)

# initialize dash
app = dash.Dash(__name__)
#give layout, graphs set at the top give unique id 
app.layout = html.Div([
    dcc.Graph(id="graph", figure=fig37),
    dcc.Graph(id="graph2", figure=fig2),
    dcc.Dropdown(
        id='dropdown',
        options=[
            {'label': 'Netherlands_cases', 'value': 'Netherlands_cases'},
            {'label': 'Netherlands_index', 'value': 'Netherlands_index'}],
        value='Netherlands_cases'
        ),
    dcc.Graph(id='graph1'),
    
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
@app.callback(Output(component_id='graph1', component_property= 'figure'),
              [Input(component_id='dropdown', component_property= 'value')])


def graph_update(dropdown_value):
    print(dropdown_value)
    if dropdown_value == "Netherlands_cases":
        fig = px.line(
        df1, x='date', y='new_cases',  
        title="corona cases for Netherlands", height=325
        )
    if dropdown_value == "Netherlands_index":
        fig = px.line(
        df2, x='date', y='stringency_index',
        title="stringency for Netherlands", height=325
        )
    return fig

app.run_server(debug=True)