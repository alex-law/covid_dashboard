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

#Get data frames
deaths_df = pd.read_csv('covid_deaths.csv')
cases_df = pd.read_csv('covid_cases.csv')

#Format data frames.
deaths_df = formatdf(deaths_df)
cases_df = formatdf(cases_df)
deaths_df['Type'] = 'Deaths'
cases_df['Type'] = 'Cases'

#Get per day column
countries = getCountries(cases_df)
deaths_df = getPerDayWeek(deaths_df, countries)
cases_df = getPerDayWeek(cases_df, countries)

deaths_df.to_csv('covid_deaths_cleaned.csv')
cases_df.to_csv('covid_cases_cleaned.csv')