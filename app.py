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
#min_date, max_date = getMinMaxDate(cases_df)
#min_date = '2020-01-22'

app.layout = html.Div([
    html.Div([

        html.Div([
            dcc.Dropdown(
                id='display-country',
                options=[{'label': i, 'value': i} for i in countries],
                multi=True,
                value='United Kingdom'
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
                min_date_allowed=cases_df['Date'].min(),
                max_date_allowed=cases_df['Date'].max(),
                initial_visible_month='2020-03-22',
                end_date='2020-03-22'
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

    dcc.Graph(id='indicator-graphic')
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
                 lin_log, deaths_cases, min_date, max_date):

    
    #Drop out of range dates.
    deaths_drop_index = deaths_df[(deaths_df['Date'] < min_date) | (deaths_df['Date'] > max_date)].index
    cases_drop_index = cases_df[(cases_df['Date'] < min_date) | (cases_df['Date'] > max_date)].index
    deaths_dff = deaths_df.drop(deaths_drop_index)
    cases_dff = cases_df.drop(cases_drop_index)
    deaths_dff['Datetime'] = pd.to_datetime(deaths_dff['Date'])
    cases_dff['Datetime'] = pd.to_datetime(cases_dff['Date'])

    traces = []
    for option in deaths_cases:
        for country in display_countries:

            if option == 'deaths':
                temp_df = deaths_dff
            elif option == 'cases':
                temp_df = cases_dff

            traces.append(dict(
                x=temp_df[temp_df['Country/Region'] == country]['Date'],
                y=temp_df[temp_df['Country/Region'] == country]['Value'],
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


if __name__ == '__main__':
    app.run_server(debug=True)