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
    model = AutoReg(df3, lags=1)
    model_fit = model.fit()
    y = model_fit.predict(len(df3), len(df3)+30)
    return y

def predictor(x):
    model = AutoReg(x, lags=1)
    model_fit = model.fit()
    y = model_fit.predict(len(x), len(x)+30)
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
predicteddf['location'] = 'Netherlands'
print(predicteddf)

# AutoRegression for sweden using predictor()
SWEpredict = SWEdata['new_cases']
predictSWE = predictor(SWEpredict.astype(float))
predictedSWE = []
predictedSWE = pd.DataFrame({'index':predictSWE.index, 'predicted':predictSWE.values})
predictedSWE['date'] = pd.date_range(start=pd.Timestamp('today'), periods=31)
predictedSWE['date'] = pd.to_datetime(predictedSWE['date']).dt.date
predictedSWE['location'] = 'Sweden'
print(predictedSWE)

# AUtoRegression for Australia using predictor(), could be more efficient probably
AUSpredict = AUSdata['new_cases']
predictAUS = predictor(AUSpredict.astype(float))
predictedAUS = []
predictedAUS = pd.DataFrame({'index':predictAUS.index, 'predicted':predictAUS.values})
predictedAUS['date'] = pd.date_range(start=pd.Timestamp('today'), periods=31)
predictedAUS['date'] = pd.to_datetime(predictedAUS['date']).dt.date
predictedAUS['location'] = 'Australia'
print(predictedAUS)

# combine data
framesPredicted = [predicteddf, predictedSWE, predictedAUS]
NLSWEAUSpredicted = pd.concat(framesPredicted)
print(NLSWEAUSpredicted)

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
#RIVM graphs
figRIVM = px.line(
    df3, x='date', y='Total_reported',
    title="RIVM reported cases per day", height=450
)
figPredicted = px.line(
    NLSWEAUSpredicted, x='date', y='predicted', color='location',
    title="Predicted trend for the next 30 days", height=450
)

# initialize dash
app = dash.Dash(__name__)
#give layout, graphs set at the top give unique id 
app.layout = html.Div([
    html.Div([html.H1('COVID-19 Dashboard with Predictive Analytics', style={'font-family':'verdana'})]),
    dcc.Graph(id="graph", figure=fig37),
    dcc.Graph(id="graph2", figure=fig2),
    dcc.Graph(id="graph3", figure=figRIVM),
    dcc.Graph(id="graph4", figure=figPredicted),
    dcc.Dropdown(
        id='dropdown',
        options=[
            {'label': 'Netherlands_cases', 'value': 'Netherlands_cases'},
            {'label': 'Netherlands_index', 'value': 'Netherlands_index'}],
        value='Netherlands_cases'
        ),
    #instead of plotting specific countries we can plot predicted graphs
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


if __name__ == "__main__":
    app.run_server(host='0.0.0.0', debug= True, port=5000)