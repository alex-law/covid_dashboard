import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
from datetime import datetime
    
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

def getPerDayWeek(df, countries):
    #Get per day deaths from difference in cumulative for each country.
    per_day_week_df = pd.DataFrame(columns=['Country/Region','Date','Value','Type','Diff','Week'])
    for country in countries:
        country_df = df[df['Country/Region']==country]
        day_series = df[df['Country/Region']==country]['Value'].diff()
        week_series = df[df['Country/Region']==country]['Value'].diff(7)
        temp_df = pd.concat([country_df, day_series, week_series],axis=1)
        #Rename columns
        temp_df.columns = ['Country/Region','Date','Value','Type','Diff','Week']
        per_day_week_df = per_day_week_df.append(temp_df)
    return per_day_week_df




def getCovidDays(min_date, max_date):
    min_datetime = datetime.strptime(min_date, '%Y-%m-%d')
    max_datetime = datetime.strptime(max_date, '%Y-%m-%d')
    time_delta = max_datetime - min_datetime
    return time_delta.days
