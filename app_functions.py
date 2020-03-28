import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
    
def formatdf(df):
    #Drop unnecessary columns and rows.
    to_drop = ['Province/State','Lat','Long']
    df.drop(labels=to_drop, axis=1, inplace=True)
    df.drop(0, axis=0, inplace=True)
    #Convert string values to ints.
    df['Value'] = pd.to_numeric(df['Value'])
    #Sum entries with same date and country (but different region).
    df = df.groupby(['Country/Region', 'Date']).sum()
    df.reset_index(inplace=True)
    return df

def getCountries(cases_df):
    #Get list of countries for dropdown
    return cases_df['Country/Region'].unique()

def getMinMaxDate(cases_df):
    #Get max and min dates to display data in main graph
    min_date = cases_df['Date'].min()
    max_date = cases_df['Date'].max()
    return min_date, max_date

