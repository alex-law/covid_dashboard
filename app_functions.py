import pandas as pd
import requests
import io
from datetime import datetime

def getMinMaxDate(cases_df):
    #Get max and min dates to display data in main graph
    min_date = cases_df['Date'].min()
    max_date = cases_df['Date'].max()
    return min_date, max_date

def getCovidDays(min_date, max_date):
    #Get the number of days since covid start.
    print('min date: ', min_date)
    print('max date: ', max_date)
    min_datetime = datetime.strptime(min_date, '%Y-%m-%d')
    max_datetime = datetime.strptime(max_date, '%Y-%m-%d')
    time_delta = max_datetime - min_datetime
    return time_delta.days

def getGraph1Label(deaths_cases):
    if len(deaths_cases) == 0:
        label = ' '
    elif len(deaths_cases) == 1: 
        if 'cases' in deaths_cases:
            label = 'Cases'
        elif 'deaths' in deaths_cases:
            label = 'Deaths'
    elif len(deaths_cases) == 2:
        label = 'Deaths\Cases'
    return label

def getGraph2Label(deaths_cases):
    if len(deaths_cases) == 0:
        label = ' '
        min_value = 0
    elif len(deaths_cases) == 1: 
        if 'cases' in deaths_cases:
            label = 'Log(Cases'
            min_value = 40
        elif 'deaths' in deaths_cases:
            label = 'Log(Deaths'
            min_value = 10
    elif len(deaths_cases) == 2:
        label = 'Log(Deaths\Cases'
        min_value = 40
    return label, min_value

def getDfFromUrl(git_url, file_name):
    #Get data frame from GitHub
    url = git_url + file_name
    raw = requests.get(url).content
    df = pd.read_csv(io.StringIO(raw.decode('utf-8')))
    return df

def getCountries(cases_df):
    #Get list of countries for dropdown
    return cases_df['Country/Region'].unique()