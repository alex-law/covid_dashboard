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

app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='display-country',
                options=[{'label': i, 'value': i} for i in countries],
                multi=True,
                value=['United Kingdom']
            ),
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
            dcc.DatePickerRange(
                id='date-picker-range',
                min_date_allowed=min_date,
                max_date_allowed=max_date,
                initial_visible_month='2020-03-22',
                end_date=cases_df['Date'].max()
            ),
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
            dcc.RadioItems(
                id='lin-log',
                options=[
                    {'label': 'Linear', 'value': 'lin'},
                    {'label': 'Logarithmic', 'value': 'log'}
                ],
                value='lin'
            )
        ],
        style={'width': '30%', 'float': 'right', 'display': 'inline-block'})
    ]),

    dcc.Graph(id='indicator-graphic', config={'displayModeBar': False}),
    dcc.Slider(
        id='days-since-slider',
        min = 0,
        max = days_since,
        step = 1,
        value = 5,
    ),
    dcc.Graph(id='log-log-graphic', config={'displayModeBar': False})
])

@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('display-country', 'value'),
     Input('per-day-cum', 'value'),
     Input('lin-log', 'value'),
     Input('deaths-cases', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')])
def update_graph(display_countries, per_day_cum,
                 lin_log, deaths_cases, min_d, max_d):

    
    #Drop out of range dates.
    deaths_drop_index = deaths_df[(deaths_df['Date'] < min_d) | (deaths_df['Date'] > max_d)].index
    cases_drop_index = cases_df[(cases_df['Date'] < min_d) | (cases_df['Date'] > max_d)].index
    deaths_dff = deaths_df.drop(deaths_drop_index)
    cases_dff = cases_df.drop(cases_drop_index)
    #deaths_dff['Datetime'] = pd.to_datetime(deaths_dff['Date'])
    #cases_dff['Datetime'] = pd.to_datetime(cases_dff['Date'])

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
            yaxis={'title': 'Deaths', 'type': 'linear'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest',
            legend={'x': 0, 'y': 1}
        )
    }

@app.callback(
    Output('log-log-graphic', 'figure'),
    [Input('display-country', 'value'),
     Input('deaths-cases', 'value'),
     Input('days-since-slider', 'value')])
def update_log_log_graph(display_countries, deaths_cases, days_since):
    
    #Drop out of range dates.
    #deaths_drop_index = deaths_df[(deaths_df['Date'] < min_d) | (deaths_df['Date'] > max_d)].index
    #cases_drop_index = cases_df[(cases_df['Date'] < min_d) | (cases_df['Date'] > max_d)].index
    #deaths_dff = deaths_df.drop(deaths_drop_index)
    #cases_dff = cases_df.drop(cases_drop_index)
    #deaths_dff['Datetime'] = pd.to_datetime(deaths_dff['Date'])
    #cases_dff['Datetime'] = pd.to_datetime(cases_dff['Date'])

    traces = []
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
            country_df = country_df.iloc[7:]
            country_df = country_df[country_df['Value'] >= 30]

            traces.append(dict(
                x=country_df.head(days_since)['Value'],
                y=country_df.head(days_since)['Week'],
                text=option,
                mode='lines+markers',
                marker={
                    'size': 10,
                    'opacity': 0.7,
                    'line': {'width': 0.5, 'color': 'white'}
                }
            ))

    return {
        'data': traces,
        'layout': dict(
            xaxis={'title': 'Date', 'type': 'log'},
            yaxis={'title': 'Deaths', 'type': 'log'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest',
            legend={'x': 0, 'y': 1}
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)