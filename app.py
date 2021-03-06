import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import io
import requests

from app_functions import *

#Define web app style.
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#Get dataframes from GitHub
#git_url="https://raw.githubusercontent.com/alex-law/covid_dashboard/master/"
#cases_df = getDfFromUrl(git_url, 'covid_cases_cleaned.csv')
#deaths_df = getDfFromUrl(git_url, 'covid_deaths_cleaned.csv')

cases_df = pd.read_csv('covid_cases_cleaned.csv')
deaths_df = pd.read_csv('covid_deaths_cleaned.csv')

cases_df = pd.read_csv('covid_cases_cleaned.csv')
deaths_df = pd.read_csv('covid_deaths_cleaned.csv')

#Get input options.
countries = getCountries(cases_df)
min_date, max_date = getMinMaxDate(cases_df)
days_since = getCovidDays(min_date, max_date)

#Define webpage layout
app.layout = html.Div([

    dcc.Markdown('''
    # Covid-19 Dashboard

    This dashboard takes live data from the 
    [Johns Hopkins Covid-19 Dataset](https://data.humdata.org/dataset/novel-coronavirus-2019-ncov-cases) 
    and presents it in two interactive graphs. 
    
    **Graph 1** is the standard exponential graph which
    is often seen in the news.

    **Graph 2** provides an easy way to see if a countries increase in cases/deaths
    is exponential or not. Exponential growth occurs when the growth rate is proportional
    to the current population size. This means if we plot the number of cases/deaths in 
    the past week (the growth rate), against the total number of cases/deaths 
    (the population size) we will see a straight line when the relationship is exponential.
    When countries drop off this line, it means they are no longer experiencing an
    exponential increase in cases/deaths.
    '''),
    html.Br(),
    html.Div([

        html.Div([
            dcc.Markdown('''**Options for Graph 1 and 2**'''),
            dcc.Dropdown(
                id='display-country',
                options=[{'label': i, 'value': i} for i in countries],
                multi=True,
                value=['United Kingdom']
            ),
            html.Br(),
            dcc.Checklist(
                id='deaths-cases',
                options=[
                    {'label': 'Cases', 'value': 'cases'},
                    {'label': 'Deaths', 'value': 'deaths'}
                ],
                value=['deaths']
            )
        ],
        style={'width': '45%', 'float': 'left', 'display': 'inline-block'}),

        html.Div([
            dcc.Markdown('''**Options for Graph 1**'''),
            dcc.RadioItems(
                id='lin-log-1',
                options=[
                    {'label': 'Linear', 'value': 'lin'},
                    {'label': 'Logarithmic', 'value': 'log'}
                ],
                value='lin'
            ),
            html.Br(),
            dcc.RadioItems(
                id='per-day-cum',
                options=[
                    {'label': 'Per Day', 'value': 'per_day'},
                    {'label': 'Cumulative', 'value': 'cumulative'}
                ],
                value='cumulative'
            )
        ],
        style={'width': '45%', 'display': 'inline-block'})
    ]),
    html.Br(),
    dcc.RangeSlider(
        id='date-range-slider',
        min=0,
        max=days_since,
        dots=False,
        step=1,
        value=[0, days_since],
        updatemode='drag'
    ),
    dcc.Markdown(id='date-range-text'),
    dcc.Graph(id='indicator-graphic', config={'displayModeBar': False}),
    dcc.Graph(id='log-log-graphic', config={'displayModeBar': False}),
    dcc.Markdown('''[Source code](https://github.com/alex-law/covid_dashboard "GitHub")'''),
    dcc.Markdown('''[Thanks to Minute Physics](https://www.youtube.com/watch?v=54XLXg4fYsc "Minute Physics")''')
])

@app.callback(
    Output('date-range-text', 'children'),
    [Input('date-range-slider', 'value')])
def update_output(value):
    start_date = cases_df.loc[value[0], 'Date']
    end_date = cases_df.loc[value[1], 'Date']
    return "**Date Range:** *{}* to *{}*".format(start_date, end_date)

@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('display-country', 'value'),
     Input('per-day-cum', 'value'),
     Input('lin-log-1', 'value'),
     Input('deaths-cases', 'value'),
     Input('date-range-slider', 'value')])
def update_graph(display_countries, per_day_cum,
                 lin_log, deaths_cases, day_range):

    #Get date range
    min_d = cases_df.loc[day_range[0], 'Date']
    max_d = cases_df.loc[day_range[1], 'Date']
    #Drop out of range dates.
    deaths_drop_index = deaths_df[(deaths_df['Date'] < min_d) | (deaths_df['Date'] > max_d)].index
    cases_drop_index = cases_df[(cases_df['Date'] < min_d) | (cases_df['Date'] > max_d)].index
    deaths_dff = deaths_df.drop(deaths_drop_index)
    cases_dff = cases_df.drop(cases_drop_index)

    if per_day_cum == 'per_day':
        y_axis = 'Diff'
    elif per_day_cum == 'cumulative':
        y_axis = 'Value'

    label = getGraph1Label(deaths_cases)

    traces = []
    for option in deaths_cases:
        for country in display_countries:

            if option == 'deaths':
                temp_df = deaths_dff
            elif option == 'cases':
                temp_df = cases_dff

            traces.append(dict(
                x=temp_df[temp_df['Country/Region'] == country]['Date'],
                y=temp_df[temp_df['Country/Region'] == country][y_axis],
                text="{} {}".format(country,option),
                mode='lines+markers',
                marker={
                    'size': 7,
                    'opacity': 0.7,
                    'line': {'width': 0.5, 'color': 'white'}
                },
                name="{} {}".format(country,option)
            ))

    return {
        'data': traces,
        'layout': dict(
            xaxis={'title': 'Date'},
            yaxis={'title': label, 'type': 'linear' if lin_log == 'lin' else 'log'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest',
            legend={'x': 0, 'y': 1}
        )
    }

@app.callback(
    Output('log-log-graphic', 'figure'),
    [Input('display-country', 'value'),
     Input('deaths-cases', 'value'),
     Input('date-range-slider', 'value')])
def update_log_log_graph(display_countries, deaths_cases, day_range):

 

    traces = []

    label, min_value = getGraph2Label(deaths_cases)

    for option in deaths_cases:
        for country in display_countries:

            if option == 'deaths':
                temp_df = deaths_df
            elif option == 'cases':
                temp_df = cases_df

            country_df = temp_df[temp_df['Country/Region'] == country]
            country_df.sort_values(by=['Date'], inplace=True)
            country_df.reset_index(drop=True, inplace=True)
            country_df.reset_index(inplace=True)
            country_df = country_df[day_range[0]:day_range[1]]
            country_df = country_df[country_df['Value'] >= min_value]

            #range=[min_value, country_df['Value'].max()],
            traces.append(dict(
                x=country_df['Value'],
                y=country_df['Week'],
                mode='lines+markers',   
                name="{} {}".format(country,option),
                option="{} {}".format(country,option),
                marker={
                    'size': 7,
                    'opacity': 0.7,
                    'line': {'width': 0.5, 'color': 'white'}
                }
            ))

    return {
        'data': traces,
        'layout': dict(
            xaxis={'title': '{})'.format(label) if label != ' ' else ' ', 'type': 'log'},
            yaxis={'title': '{} in past week)'.format(label) if label != ' ' else ' ', 'type': 'log'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest',
            legend={'x': 0, 'y': 1}
            )
    }

if __name__ == '__main__':
    app.run_server(debug=True)