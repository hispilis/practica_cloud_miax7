import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
from datetime import date
from datetime import datetime

import api_esios as ae 

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

url_base_aws = 'https://z7n1qubz0k.execute-api.eu-west-3.amazonaws.com/default/api_data_pvpc?locale=es'
url_base_esios = 'https://api.esios.ree.es/archives/70/download_json?locale=es'

api_esios = ae.APIESIOS(url_base_aws)

now = datetime.now()

PLOTLY_LOGO = "https://aulavirtual.institutobme.es/pluginfile.php/1/theme_edumy/headerlogo_mobile/1618036393/Marca_Instituto%20BME_RGB_Negativo.png"
app.layout = dbc.Container([

    dbc.Navbar(
        dbc.Container(
            children=[
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src=PLOTLY_LOGO, height="40px")),
                            #dbc.Col(dbc.NavbarBrand("INICIO", className="ms-2")),
                        ],
                        align="left",
                        className="g-0",
                    ),
                    href="https://practica-cloud-miax7-6c52whetxq-ew.a.run.app/",
                    style={"textDecoration": "none"},
                ),
                dbc.NavItem(dbc.NavLink("INICIO", href="#", style={"color":"white"})),
                #dbc.NavItem(dbc.NavLink("COMPARATIVA", href="#", style={"color":"white"})),
                html.Hr(),            
            ],
            style={"justify-content":"left"},
        ),
        color="#002f5f",
        dark=False,        
    ),                    

    html.Hr(),

    html.Div([
        dbc.Row(
            [
                dbc.Col(html.H5('TÉRMINO DE FACTURACIÓN DE ENERGÍA ACTIVA DEL PVPC', style={'text-align':'center', 'color':'#006699'})),                
            ],
            align="center",
            className="g-0",
        ),
        dbc.Row(
            [
                dbc.Col(html.H6('Fecha', style={'text-align':'right', 'margin-top':'0.5rem', 'margin-bottom':'1rem'})),
                dbc.Col(dcc.DatePickerSingle(
                    id='my-date-picker-single',            
                    initial_visible_month=date(now.year, now.month, now.day),
                    min_date_allowed=date(year=(now.year - 5), month=now.month, day=now.day),
                    max_date_allowed=date(year=now.year, month=now.month, day=now.day),

                    display_format='DD/MM/YYYY',
                    first_day_of_week=1,

                    date=date(now.year, now.month, now.day)
                )),
            ],
        ),                    
        dcc.Graph(
            id='example-graph'                              
        ),
    ]),    

    html.Div([
        dbc.Row(
            [
                dbc.Col(html.H6('Rango', style={'text-align':'right', 'margin-top':'0.5rem', 'margin-bottom':'1rem'})),
                dbc.Col(dcc.DatePickerRange(
                    id='my-date-picker-range',
                    initial_visible_month=date(now.year, now.month, now.day),
                    #Limitado a 4 meses por el rendimiento de la capa free de AWS
                    min_date_allowed=date(year=now.year , month=(now.month - 4), day=now.day),
                    max_date_allowed=date(year=now.year, month=now.month, day=now.day),

                    display_format='DD/MM/YYYY',
                    first_day_of_week=1,

                    end_date=date(now.year, now.month, now.day),
                    start_date=date(year=now.year, month=(now.month-1), day=now.day)
                )),
            ],
        ),        
        dcc.Graph(
            id='example-graph-2'                              
        ),
    ]),    
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
    fig.update_layout(
            title='PRECIO DEL DIA',
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

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=serie.index, y=serie.values,
                        mode='lines+markers',
                        name=f'{start_date_string}-{end_date_string}'))    
    fig.update_layout(
            title='PRECIO MEDIO DIARIO',
            xaxis_title='Fecha',
            yaxis_title='€/kWh',
            transition_duration=500)        
    return fig

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=False, port=8080)
