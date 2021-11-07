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
import warnings 
warnings.filterwarnings("ignore")

app=Flask(__name__)

@app.route("/")



#This next function loads data from OWID. Every time the python file is ran a new version of the data will be loaded.
#The data is minimized using usecols to reduce file size
def dataloading():
    urlowid= "https://covid.ourworldindata.org/data/owid-covid-data.csv"
    colsowid = ['date','new_cases','stringency_index', 'location']
    data = pd.read_csv(urlowid, usecols=colsowid)
    data['new_cases'] = data['new_cases'].replace(np.nan, 0)
    data = data.astype({"new_cases":np.int64, "stringency_index":np.float64, "location":object})
    data['date'] = pd.to_datetime(data['date']) #this helps when creating graphs where x = date
    return data

#This loads the RIVM data, the second data source. It will be used to predict new cases in the Netherlands 
#Also this data is minimized to reduce file size and increase performance
def RIVMdata():
    urlRIVM = "https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_per_dag.csv"
    colsrivm = ['Date_of_publication', 'Total_reported']
    data = pd.read_csv(urlRIVM, usecols=colsrivm, sep=';')
    data = data.astype({'Total_reported':np.int64})
    data['date'] = pd.to_datetime(data['Date_of_publication'])
    data.sort_values(by=['date'])
    #Total_reported is postive tests per day
    return data

#these next functions filter the required countries from the OurWorldInData dataset
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

#this function is used to
def predictRIVM(df3):
    #AutoReg uses Conditional Maximum Likelihood estimate to predict 
    #source: https://www.statsmodels.org/dev/generated/statsmodels.tsa.ar_model.AutoReg.html
    #source: https://www.sciencedirect.com/topics/mathematics/conditional-likelihood 
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
RIVMdf = RIVMdf.sort_values(by = 'date')
NLdata = dataNL(df)
NLdata = NLdata.sort_values(by = 'date')
SWEdata = dataSWE(df)
SWEdata = SWEdata.sort_values(by = 'date')
AUSdata = dataAUS(df)
AUSdata = AUSdata.sort_values(by = 'date')
frames = [NLdata, SWEdata, AUSdata]
threecountries = pd.concat(frames)
print(threecountries)
threecountries = threecountries.sort_values(by = 'date')

#create dfs for figures in dropdown
df1 = NLdata[['date', 'new_cases', 'location', 'stringency_index']]
df2 = NLdata[['date', 'stringency_index', 'location', 'new_cases']]
df3 = RIVMdf[['date', 'Total_reported']]
print(df3.info())
df3 = df3.groupby('date')['Total_reported'].sum()
df3 = pd.DataFrame({'date':df3.index, 'Total_reported':df3.values})
print(df3.info())
df4 = SWEdata[['date', 'new_cases', 'location', 'stringency_index']]
df5 = AUSdata[['date', 'new_cases', 'location', 'stringency_index']]
df6 = threecountries[['date', 'new_cases', 'location', 'stringency_index']]
df6 = df6.sort_values(by = ['date', 'location'])

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
predicteddf = predicteddf.sort_values(by='date')

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
framesPredicted = [predictedAUS, predicteddf, predictedSWE]
NLSWEAUSpredicted = pd.concat(framesPredicted)
print(NLSWEAUSpredicted)
NLSWEAUSpredicted = NLSWEAUSpredicted.sort_values(by='date')




# preload graphs for faster loading in dropdown switcher
figPredicted = px.line(
    NLSWEAUSpredicted, x='date', y='predicted', color='location',
    title="Predicted trend for the next 30 days", height=450
)

fig_cases_all = px.line(
        threecountries, x='date', y='new_cases', color='location',
        title="Corona cases for each country", height=450
)

allSI = px.line(
        threecountries, x='date', y='stringency_index', color='location',
        title="Stringency for each country", height=450
)

# initialize dash
app = dash.Dash(__name__)
#give layout, graphs set at the top give unique id 
app.layout = html.Div([
    html.Div([html.H1('COVID-19 Dashboard with Predictive Analytics', style={'font-family':'verdana'})]),
    dcc.Graph(id="graph", figure=figPredicted),
#    dcc.Graph(id="graph3", figure=figRIVM),
    
    dcc.Dropdown(
        id='dropdown',
        options=[
            {'label': 'Netherlands', 'value': 'Netherlands_cases'},
            {'label': 'Sweden', 'value': 'Sweden_cases'},
            {'label': 'Australia', 'value': 'Australia_cases'},
            {'label': 'All', 'value': 'All'}],
        value='All'
        ),
    #instead of plotting specific countries we can plot predicted graphs
    dcc.Graph(id='graph1'),
    dcc.Graph(id='graph2')
])
@app.callback(Output(component_id='graph1', component_property= 'figure'),
              [Input(component_id='dropdown', component_property= 'value')])

def graph_update(dropdown_value):
    print(dropdown_value)
    if dropdown_value == "Netherlands_cases":
        fig = px.line(
        df3, x='date', y='Total_reported',  
        title="Corona cases for Netherlands", height=450
        ) 

    if dropdown_value == "Sweden_cases":
        fig = px.line(
        df4, x='date', y='new_cases',  
        title="Corona cases for Sweden", height=450
        ) 
        
    if dropdown_value == "Australia_cases":
        fig = px.line(
        df5, x='date', y='new_cases',  
        title="Corona cases for Australia", height=450
        ) 
    if dropdown_value == "All":
        fig = fig_cases_all

    return fig


@app.callback(Output(component_id='graph2', component_property= 'figure'),
              [Input(component_id='dropdown', component_property= 'value')])

def graph_update(dropdown_value):
    print(dropdown_value)
    if dropdown_value == "Netherlands_cases":
        fig = px.line(
        df1, x='date', y='stringency_index',  
        title="Stringency Index for Netherlands", height=450
        )

    if dropdown_value == "Sweden_cases":
        fig = px.line(
        df4, x='date', y='stringency_index',  
        title="Stringency Index for Sweden", height=450
        ) 
        
    if dropdown_value == "Australia_cases":
        fig = px.line(
        df5, x='date', y='stringency_index',  
        title="Stringency Index for Australia", height=450
        ) 
    if dropdown_value == "All":
        fig = allSI

    return fig

server = app.server
if __name__ == "__main__":
    app.run_server(host='0.0.0.0', port=5000)