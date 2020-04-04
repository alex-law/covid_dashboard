import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app_functions import *

import pandas as pd

#Define web app style.
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#Get data frames.
deaths_df = pd.read_csv('covid_deaths.csv')
cases_df = pd.read_csv('covid_cases.csv')
deaths_df = formatdf(deaths_df)
cases_df = formatdf(cases_df)
deaths_df['Type'] = 'Deaths'
cases_df['Type'] = 'Cases'

#Get input options.
countries = getCountries(cases_df)
min_date, max_date = getMinMaxDate(cases_df)
days_since = getCovidDays(min_date, max_date)

#Get per day column
deaths_df = getPerDayWeek(deaths_df, countries)
cases_df = getPerDayWeek(cases_df, countries)

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
            dcc.Markdown('''**Graph 1 and 2**'''),
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
        style={'width': '30%', 'float': 'left', 'display': 'inline-block'}),

        html.Div([
            dcc.Markdown('''**Graph 1**'''),
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
        style={'width': '30%', 'display': 'inline-block'}),

        html.Div([
            dcc.Markdown('''**Graph 2**'''),
            dcc.RadioItems(
                id='lin-log-2',
                options=[
                    {'label': 'Linear', 'value': 'lin'},
                    {'label': 'Logarithmic', 'value': 'log'}
                ],
                value='log'
            )
        ],
        style={'width': '30%', 'float': 'right', 'display': 'inline-block'})
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
    html.Br(),
    dcc.Graph(id='indicator-graphic', config={'displayModeBar': False}),
    dcc.Graph(id='log-log-graphic', config={'displayModeBar': False})
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
                text=option,
                mode='lines+markers',
                marker={
                    'size': 15,
                    'opacity': 0.7,
                    'line': {'width': 0.5, 'color': 'white'}
                },
                name="{} {}".format(country,option)
            ))

    return {
        'data': traces,
        'layout': dict(
            xaxis={'title': 'Date'},
            yaxis={'title': 'Deaths', 'type': 'linear' if lin_log == 'lin' else 'log'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest',
            legend={'x': 0, 'y': 1}
        )
    }

@app.callback(
    Output('log-log-graphic', 'figure'),
    [Input('display-country', 'value'),
     Input('deaths-cases', 'value'),
     Input('lin-log-2', 'value'),
     Input('date-range-slider', 'value')])
def update_log_log_graph(display_countries, deaths_cases, lin_log, day_range):

    #Get date range
    #min_d = cases_df.loc[day_range[0], 'Date']
    #max_d = cases_df.loc[day_range[0], 'Date']

    traces = []
    for option in deaths_cases:
        for country in display_countries:

            if option == 'deaths':
                temp_df = deaths_df
                min_value = 1
            elif option == 'cases':
                temp_df = cases_df
                min_value = 30

            country_df = temp_df[temp_df['Country/Region'] == country]
            country_df.sort_values(by=['Date'], inplace=True)
            country_df.reset_index(drop=True, inplace=True)
            country_df.reset_index(inplace=True)
            country_df_range = country_df[day_range[0]:day_range[1]]

            traces.append(dict(
                x=country_df_range['Value'],
                y=country_df_range['Week'],
                text=option,
                mode='lines+markers',
                range=[min_value, country_df['Value'].max()],
                marker={
                    'size': 10,
                    'opacity': 0.7,
                    'line': {'width': 0.5, 'color': 'white'}
                }
            ))

    return {
        'data': traces,
        'layout': dict(
            xaxis={'title': 'Date', 'type': 'linear' if lin_log == 'lin' else 'log'},
            yaxis={'title': 'Deaths', 'type': 'linear' if lin_log == 'lin' else 'log'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest',
            legend={'x': 0, 'y': 1}
        )
    }

if __name__ == '__main__':
    app.run_server(debug=True)