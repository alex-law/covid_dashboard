import pandas as pd
from tqdm import tqdm

def formatdf(df):
    #Drop unnecessary columns
    df = df.drop(labels=['Lat', 'Long', 'Province/State'], axis=1)
    #Melt coluns ready for further processing
    df_m = df.melt(id_vars=['Country/Region'], var_name='Date', value_name='Value')
    #Convert string values to ints.
    df_m['Value'] = pd.to_numeric(df_m['Value'])
    #Sum entries with same date and country (but different region).
    df_m = df_m.groupby(['Country/Region', 'Date']).sum()
    df_m.reset_index(inplace=True)
    #Format date to be datetime
    df_m.Date = pd.to_datetime(df_m.Date)
    #Sort by country then date
    df_m = df_m.sort_values(['Country/Region', 'Date'], ascending=[True, True])
    return df_m

def getCountries(cases_df):
    #Get list of countries for dropdown
    return cases_df['Country/Region'].unique()

def getPerDayWeek(df, countries):
    #Get per day deaths from difference in cumulative for each country.
    per_day_week_df = pd.DataFrame(columns=['Country/Region','Date','Value','Type','Diff','Week'])
    for country in tqdm(countries):
        country_df = df[df['Country/Region']==country]
        day_series = df[df['Country/Region']==country]['Value'].diff()
        week_series = df[df['Country/Region']==country]['Value'].diff(7)
        temp_df = pd.concat([country_df, day_series, week_series],axis=1)
        #Rename columns
        temp_df.columns = ['Country/Region','Date','Value','Type','Diff','Week']
        per_day_week_df = per_day_week_df.append(temp_df)
    return per_day_week_df

#Get data frames   
cases_df = pd.read_csv(r'C:/Users/alexw/coding-projects/covid-dash/data_repo/COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')
deaths_df = pd.read_csv(r'C:/Users/alexw/coding-projects/covid-dash/data_repo/COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')


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