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

api_esios = ae.APIESIOS()
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
            date=date(now.year, now.month, now.day)
        )
    ]),

    dcc.Graph(
        id='example-graph'                              
    )
])

@app.callback(
    Output('example-graph','figure'),
    Input('my-date-picker-single', 'date'))
def update_figure(date_value):              
    if date_value is not None:
        date_object = date.fromisoformat(date_value)
        date_string = date_object.strftime('%d-%m-%Y')
    df = api_esios.get_data(date_string)
    fig = px.line(df, x=df.columns[0], y=df.columns[1], title='TÉRMINO DE FACTURACIÓN DE ENERGÍA ACTIVA DEL PVPC', labels={'x':'Hora', 'y':'€/kWh'})
    fig.update_layout(transition_duration=500)
    return fig

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=False, port=8080)
