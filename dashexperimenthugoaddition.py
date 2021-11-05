import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
from flask import Flask
import statsmodels as sm
from statsmodels.tsa.ar_model import AutoReg

app=Flask(__name__)

@app.route("/")


#load data function
def dataloading():
    urlowid= "https://covid.ourworldindata.org/data/owid-covid-data.csv"
    data = pd.read_csv(urlowid)
    data['date'] = pd.to_datetime(data['date']) #this helps when creating graphs where x = date
    #set NaN to 0
    return data

def RIVMdata():
    urlRIVM = "https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_per_dag.csv"
    data = pd.read_csv(urlRIVM, sep=';')
    data['date'] = pd.to_datetime(data['Date_of_publication'])
    data.sort_values(by=['date'])
    #Total_reported is postive tests per day
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

def predictRIVM(df3):
    # fit model
    model = AutoReg(df3, lags=1)
    model_fit = model.fit()
    # let's make prediction
    y = model_fit.predict(len(df3), len(df3)+30)
    print(y)
    return y

#create dataframes
df = dataloading()
RIVMdf = RIVMdata()
NLdata = dataNL(df)
SWEdata = dataSWE(df)
AUSdata = dataAUS(df)
frames = [NLdata, SWEdata, AUSdata]
threecountries = pd.concat(frames)
print(threecountries)

#create dfs for figures in dropdown
df1 = NLdata[['date', 'new_cases', 'location', 'stringency_index']]
df2 = NLdata[['date', 'stringency_index', 'location', 'new_cases']]
df3 = RIVMdf[['date', 'Total_reported']]
print(df3.info())
df3 = df3.groupby('date')['Total_reported'].sum()
df3 = pd.DataFrame({'date':df3.index, 'Total_reported':df3.values})
df4 = SWEdata[['date', 'new_cases', 'location', 'stringency_index']]
df5 = AUSdata[['date', 'new_cases', 'location', 'stringency_index']]
df6 = threecountries[['date', 'new_cases', 'location', 'stringency_index']]

print(df3.info())

#predict RIVM data using predictRIVM()
df3onlynums = df3['Total_reported']
predict = predictRIVM(df3onlynums.astype(float))
#create new df where output of predictRIVM can be stored
predicteddf = []
predicteddf = pd.DataFrame({'index':predict.index, 'predicted':predict.values})
# add date range for next 30 days
predicteddf['date'] = pd.date_range(start=pd.Timestamp('today'), periods=31)
#remove hours from column date
predicteddf['date'] = pd.to_datetime(predicteddf['date']).dt.date
print(predicteddf)

figRIVMpredicted = px.line(
    predicteddf, x='date', y='predicted',
    title="Rredicted trend for the next 30 days", height=450
)

# initialize dash
app = dash.Dash(__name__)
#give layout, graphs set at the top give unique id 
app.layout = html.Div([
    dcc.Dropdown(
        id='dropdown',
        options=[
            {'label': 'Netherlands_cases', 'value': 'Netherlands_cases'},
            {'label': 'Sweden_cases', 'value': 'Sweden_cases'},
            {'label': 'Australia_cases', 'value': 'Australia_cases'},
            {'label': 'All', 'value': 'All'}],
        value='Netherlands_cases'
        ),
    #instead of plotting specific countries we can plot predicted graphs
    dcc.Graph(id='graph1'),
    dcc.Graph(id='graph2'),
    
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

    if dropdown_value == "Sweden_cases":
        fig = px.line(
        df4, x='date', y='new_cases',  
        title="corona cases for Netherlands", height=325
        ) 
        
    if dropdown_value == "Australia_cases":
        fig = px.line(
        df5, x='date', y='new_cases',  
        title="corona cases for Netherlands", height=325
        ) 

    return fig

@app.callback(Output(component_id='graph2', component_property= 'figure'),
              [Input(component_id='dropdown', component_property= 'value')])

def graph_update(dropdown_value):
    print(dropdown_value)
    if dropdown_value == "Netherlands_cases":
        fig = px.line(
        df1, x='date', y='stringency_index',  
        title="corona cases for Netherlands", height=325
        )

    if dropdown_value == "Sweden_cases":
        fig = px.line(
        df4, x='date', y='stringency_index',  
        title="corona cases for Netherlands", height=325
        ) 
        
    if dropdown_value == "Australia_cases":
        fig = px.line(
        df5, x='date', y='stringency_index',  
        title="corona cases for Netherlands", height=325
        ) 
    
    return fig
    


if __name__ == "__main__":
    app.run_server(host='0.0.0.0', debug= True, port=5000)