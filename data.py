import pandas as pd

def dataloading():
    urlowid= "https://covid.ourworldindata.org/data/owid-covid-data.csv"
    data = pd.read_csv(urlowid)
    data['date'] = pd.to_datetime(data['date']) #this helps when creating graphs where x = date
    return data

def RIVMdata():
    urlRIVM = "https://data.rivm.nl/covid-19/COVID-19_aantallen_gemeente_per_dag.csv"
    data = pd.read_csv(urlRIVM, sep=';', header=0)
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

# create dataframe for each country with data from OurWorldInData
df = dataloading()
RIVMdf = RIVMdata()
NLdata = dataNL(df)
SWEdata = dataSWE(df)
AUSdata = dataAUS(df)
frames = [NLdata, SWEdata, AUSdata]
threecountries = pd.concat(frames)
print(RIVMdf)