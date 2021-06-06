import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import plotly.io as pio
import matplotlib.pyplot as plt
import plotly.figure_factory as ff

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'

    }
]

plotly_template = pio.templates.default = "simple_white"

app = dash.Dash(external_stylesheets=external_stylesheets)

df19 = pd.read_csv('data/bluebikes_tripdata_2019.csv',
                   parse_dates=['starttime', 'stoptime'])

df20 = pd.read_csv('data/bluebikes_tripdata_2020.csv',
                   parse_dates=['starttime', 'stoptime'])

df = pd.concat([df19, df20])

df.columns = ['duration', 'start_time', 'stop_time', 'start_id',
              'start_name', 'start_lat', 'start_long', 'end_id', 'end_name',
              'end_lat', 'end_long', 'bike_id', 'user_type',
              'birth_year', 'gender', 'year', 'month', 'postal_code']

df = df.drop(columns=['birth_year', 'gender', 'postal_code'])

counts_bikes = df.groupby(by="year")['bike_id'].nunique()
counts_rides = df.groupby(by="year")['bike_id'].count()
counts_stations = df.groupby(by="year")['start_id'].nunique()
colors1 = ['#8fc0a9', '#68b0ab', '#c8d5b9']
colors2 = ['#68b0ab', '#c8d5b9', '#8fc0a9']
counts = df.groupby(by=["year", 'user_type']).count()
counts.reset_index(inplace=True)

layout = go.Layout(
    yaxis=dict(type='category')
)

figure_1 = go.Figure(data=go.Bar(y=['2019', '2020'], x=counts_bikes.values,
                                 orientation='h', marker_color=colors1), layout=layout)
figure_2 = go.Figure(data=go.Bar(y=['2019', '2020'], x=counts_rides.values,
                                 orientation='h', marker_color=colors1), layout=layout)
figure_3 = go.Figure(data=go.Bar(y=['2019', '2020'], x=counts_stations.values,
                                 orientation='h', marker_color=colors1), layout=layout)

figure_4 = go.Figure()
figure_4.add_trace(go.Bar(x=counts['user_type'],
                          y=counts[counts['year'] == 2019]['duration'],
                          name="2019",
                          marker_color=colors2[1]
                          ))
figure_4.add_trace(go.Bar(x=counts['user_type'],
                          y=counts[counts['year'] == 2020]['duration'],
                          name="2020",
                          marker_color=colors2[2]
                          ))

df['log_duration'] = np.log(df['duration'])

figure_5 = ff.create_distplot([df[df['year'] == 2020].log_duration, df[df['year'] == 2019].log_duration],
                              ['2020', '2019'], show_hist=False, show_rug=False, colors=colors2)

figure_5.update_layout(

    xaxis = dict(
        tickmode = 'array',
         tickvals = [0, 5, 6,7,8, 9, 14],
         ticktext = [np.exp(0), round(np.exp(5)/60,0), round(np.exp(6)/60,0),
                     round(np.exp(7)/60,0),round(np.exp(8)/60,0),
                     round(np.exp(9)/60,0), round(np.exp(14)/60,0)],
         title='Duration (minutes)'
    ),
        yaxis = dict(
         title='Frequency'
    )
 )

figure_6 = go.Figure(
    go.Scattermapbox(
        lon=df['start_long'],
        lat=df['start_lat'],
        mode='markers',
        marker=go.scattermapbox.Marker(
        )
    )
)

# Specify layout information
figure_6.update_layout(
    mapbox=dict(
        accesstoken='pk.eyJ1IjoibWFyaWV0YWFzY3giLCJhIjoiY2twazhpbG9hMXQzNTJwcmlid20ycXNyaiJ9.WIiHwd33qORzzmSWfFxNtw',  #
        center=go.layout.mapbox.Center(lat=42.35, lon=-71.06),
        zoom=11
    )
)

df['hour'] = df['start_time'].dt.hour
df['weekday'] = df['start_time'].dt.weekday

config = {"displayModeBar": False}

app.layout = html.Div([
    html.Div(children=
    [
    html.Div([
        html.H1(children='BLUEBIKES Bike Sharing', className='my-3 p-3 justify-content-lg-start',
                ),
        html.H3(children="Bluebikes is Metro Boston's public bike share program,with more than 1,800"
                         " bikes at over 200stations. The bikes can be unlocked from one station and"
                         " returned to any other station in the system, making them ideal for one-way trips.",
                className='my-3 p-3'),
    ],className='container bg-dark text-light', style={'background-color': '#68b0ab',
                                    'border-radius': '25px'
                       })
    ], className=' p-4 p-md-4 text-dark rounded bg-white'),

    html.Div([
        html.Div([html.H4(children="Number of Bikes Used", className='display-4'),
                  dcc.Graph(figure=figure_1, config=config)], className='col-md-4'),
        html.Div([html.H4(children="Number of Rides", className='display-4'),
                  dcc.Graph(figure=figure_2, config=config)], className='col-md-4'),
        html.Div([html.H6(children="Number of Stations", className='display-4'),
                  dcc.Graph(figure=figure_3, config=config)], className='col-md-4')
    ], className='row p-3 p-md-5'),

    html.Div([
        html.Div([
            html.H4(children="Number of Rides", className='display-4'),
            dcc.Graph(figure=figure_4, config=config)], className=' eight columns box-shadow'),

    ], className='row p-3 p-md-5 justify-content-center '),

    html.Div([
        html.Div([
            html.H4(children="Distribution of Log-Duration of Rides", className='display-4'),
            dcc.Graph(figure=figure_5, config=config)], className='eight columns'),

    ], className='row p-3 p-md-5 justify-content-center '),

    html.Div([
        html.Div([
            dcc.Dropdown(
                id='option_in_dur',
                options=[
                    {'label': 'Average Duration of a Ride', 'value': 'dur'},
                    {'label': 'Number of Rides', 'value': 'counts'},
                ],
                value='dur',
                style={'width': "40%"},

            ),

            dcc.Dropdown(
                id='option_in_weekday',
                options=[
                    {'label': 'By the Days of the Week', 'value': 'weekday'},
                    {'label': 'By the Hours of the Day', 'value': 'hour'},
                    {'label': 'By the Months of the Year', 'value': 'month'},
                ],
                value='weekday',
                style={'width': "40%"},

            )

        ],


            className='p-3 p-md-3'
        ),

        dcc.Graph(id='our_graph', config=config)
    ], className='p-5 p-md-5'),

    html.Div([
        html.Div([
            html.H4(children="Stations in Boston", className='display-4'),
            dcc.Graph(figure=figure_6, config=config)], className=' eight columns box-shadow'),

    ],
        className='row justify-content-center '),

], className='position-relative overflow-hidden bg-light')

layout_new = go.Layout(
    xaxis=dict(type='category')
)


@app.callback(
    Output(component_id='our_graph', component_property='figure'),
    [Input(component_id='option_in_weekday', component_property='value'),
     Input(component_id='option_in_dur', component_property='value')
     ]
)
def update_graph(value1, value2):
    counts = df.groupby(by=value1)['bike_id'].count()
    means = df.groupby(by=value1).mean()
    means.reset_index(inplace=True)
    if value2 == 'dur':
        figure_7 = go.Figure(data=go.Bar(x=means[value1], y=means['duration'],
                                         marker_color=colors1[1]))
    elif value2 == 'counts':
        figure_7 = go.Figure(data=go.Bar(x=counts.index, y=counts.values,
                                         marker_color=colors1[1]))

    if value1 == 'hour':
        xlabel='Hours of the Day'
    if value1 == 'month':
        xlabel='Months of the Year'
    if value1 == 'weekday':
        xlabel = 'Days of the Week'

    if value2 == 'dur':
        ylabel = 'Avergae Duration of a Ride'
    if value2 == 'counts':
        ylabel = 'Number of Rides'


        figure_7.update_layout(

            xaxis=dict(
                title=xlabel
            ),
            yaxis=dict(
                title=ylabel
            )
        )

    return figure_7


if __name__ == '__main__':
    app.run_server(debug=True)
