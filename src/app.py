import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
from datetime import date
from datetime import datetime

import api_esios as ae 

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,
external_stylesheets=external_stylesheets)

url_base_aws = 'https://z7n1qubz0k.execute-api.eu-west-3.amazonaws.com/default/api_data_pvpc?locale=es'
url_base_esios = 'https://api.esios.ree.es/archives/70/download_json?locale=es'

api_esios = ae.APIESIOS(url_base_aws)

now = datetime.now()

app.layout = html.Div(children=[
    html.H1(children='MIAX Practica Cloud'),


    html.H5(children='''
        Esios API
    '''),            

    html.Div([
        dcc.DatePickerSingle(
            id='my-date-picker-single',            
            initial_visible_month=date(now.year, now.month, now.day),
            min_date_allowed=date(year=(now.year - 5), month=now.month, day=now.day),
            max_date_allowed=date(year=now.year, month=now.month, day=now.day),

            display_format='DD/MM/YYYY',
            first_day_of_week=1,

            date=date(now.year, now.month, now.day)
        )
    ]),

    dcc.Graph(
        id='example-graph'                              
    ),

    html.Div([
        dcc.DatePickerRange(
            id='my-date-picker-range',
            initial_visible_month=date(now.year, now.month, now.day),
            min_date_allowed=date(year=(now.year - 5), month=now.month, day=now.day),
            max_date_allowed=date(year=now.year, month=now.month, day=now.day),

            display_format='DD/MM/YYYY',
            first_day_of_week=1,

            end_date=date(now.year, now.month, now.day),
            start_date=date(year=now.year, month=(now.month-1), day=now.day)
        )
    ]),

    dcc.Graph(
        id='example-graph-2'                              
    ),
])

@app.callback(
    Output('example-graph','figure'),
    Input('my-date-picker-single', 'date'))
def update_figure(date_value):              
    if date_value is not None:
        date_object = date.fromisoformat(date_value)
        date_string = date_object.strftime('%Y-%m-%d')
        date_string_today = f'{now.year}-{now.month}-{now.day}'
    try:
        api_esios.url_base = url_base_aws
        df = api_esios.get_daily_data(date_string)
        df_today = api_esios.get_daily_data(date_string_today)
        df_today.rename(columns={'Hora': 'Hora_hoy', 'PCB': 'PCB_hoy'}, inplace=True)
        df = pd.concat([df,df_today], axis=1)
        df.drop('Hora_hoy', axis=1, inplace=True)        
    except:
        #Si hay algún problema con el servicio AWS voy al servicio original
        api_esios.url_base = url_base_esios
        df = api_esios.get_daily_data(date_string)
        df_today = api_esios.get_daily_data(date_string_today)
        df_today.rename(columns={'Hora': 'Hora_hoy', 'PCB': 'PCB_hoy'}, inplace=True)
        df = pd.concat([df,df_today], axis=1)        
        df.drop('Hora_hoy', axis=1, inplace=True)        

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.iloc[:,0], y=df.iloc[:,2],
                        mode='lines',
                        name=f'{date_string_today}'))
    fig.add_trace(go.Scatter(x=df.iloc[:,0], y=df.iloc[:,1],
                        mode='lines',
                        name=f'{date_string}'))
    fig.update_layout(title='TÉRMINO DE FACTURACIÓN DE ENERGÍA ACTIVA DEL PVPC',
            xaxis_title='Hora',
            yaxis_title='€/kWh',
            transition_duration=500)        
    #fig.show()
    return fig

@app.callback(
    Output('example-graph-2','figure'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'))
def update_output(start_date, end_date):
    string_prefix = 'You have selected: '
    if start_date is not None:
        start_date_object = date.fromisoformat(start_date)
        start_date_string = start_date_object.strftime('%Y-%m-%d')        
    if end_date is not None:
        end_date_object = date.fromisoformat(end_date)
        end_date_string = end_date_object.strftime('%Y-%m-%d')        
    try:
        api_esios.url_base = url_base_aws
        serie = api_esios.get_range_data(start_date_string,end_date_string)
    except Exception as e: 
        print("Caught exception:", e)        
    fig = px.line(serie, x=serie.index, y=serie.values, title='PRECIO MEDIO DIARIO', labels={'x':'Fecha', 'y':'€/kWh'})
    fig.update_layout(transition_duration=500)
    return fig

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=False, port=8080)
