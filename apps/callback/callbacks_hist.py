from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import html, dcc
import dash_daq as daq
import plotly.graph_objects as go
import plotly.express as px

import random
import pandas as pd
from datetime import datetime, timedelta


from app import app

import json2dash.json2dash
import json2dash.build_dash_components


dashboard_name = '1º Aplicação Web com Json2Dash'
x = 0



@app.callback(
    Output('1º Aplicação Web_column_markdown1', 'children'),
    Output('1º Aplicação Web_column_markdown2', 'children'),
    Input('1º Aplicação Web_column_vazia', 'children'),
)
def update(values):

    try:
        df_global = pd.read_csv('apps\callback\dados_estacao_cear_puro.csv')

        df_global['Date'] = pd.to_datetime(df_global['Datetime']).dt.date
        df_global['Time'] = pd.to_datetime(df_global['Datetime']).dt.time


        return (html.Div(
                id = 'row_rodape_col_1',
                className="row row_style",
                children = [
                    html.Div(
                        id = 'row_rodape_col_1',
                        className="four columns column_style",
                        children = [
                            dcc.DatePickerRange(
                            id='my-date-picker-range',
                            min_date_allowed=df_global['Date'].iloc[0],
                            max_date_allowed=df_global['Date'].iloc[-1],
                            initial_visible_month=df_global['Date'].iloc[0],
                            #end_date=datetime.strptime(datas[-100], '%d/%m/%Y').date(),
                            display_format='D/MM/YY',
                            start_date_placeholder_text="Data Inicial",
                            end_date_placeholder_text="Data Final",
                            )
                        ]
                    ),              

                    html.Div(
                        id = 'row_rodape_col_1',
                        className="four columns column_style",
                        children = [
                            html.Div(
                                dcc.Dropdown(
                                id='mark_vars',
                                options=[
                                    {'label': 'Temperatura', 'value': 'temperatura'},
                                    {'label': 'Pressão Atmosférica', 'value': 'pressao'},
                                    {'label': 'Umidade Relativa', 'value': 'umidade'},
                                    {'label': 'Velocidade do Vento', 'value': 'velocidade'},
                                    {'label': 'DHI (Diffuse Horizontal Irradiance)', 'value': 'dhi'},
                                    {'label': 'DNI (Direct Normal Irradiance)', 'value': 'dni'},
                                    {'label': 'GHI (Global Horizontal Irradiance)', 'value': 'ghi'},
                                ],
                                multi=True
                                )
                            )
                        
                        ]
                        )
                ],
            ),

            None
        )
    except:
        raise PreventUpdate

'''
@app.callback(
    [
        Output('1º Aplicação Web_column_markdown1', 'children'),
        Output('1º Aplicação Web_column_markdown2', 'children'),
    ],
    Input('interval-component', 'n_intervals'),
)
def update(result):
    try:
        df_global = pd.read_csv('apps\callback\dados_estacao_cear_puro.csv')

        df_global['Date'] = pd.to_datetime(df_global['Datetime']).dt.strftime('%d/%m/%y')
        df_global['Time'] = pd.to_datetime(df_global['Datetime']).dt.time
        print(df_global.columns)
        #print(df_global['Time'])
        return (html.Div(
                id = 'row_rodape_col_1',
                className="row row_style",
                children = [
                    html.Div(
                        id = 'row_rodape_col_1',
                        className="four columns column_style",
                        children = [
                            dcc.DatePickerRange(
                            id='my-date-picker-range',
                            min_date_allowed=df_global['Date'].iloc[0],
                            max_date_allowed=df_global['Date'].iloc[-1],
                            initial_visible_month=df_global['Date'].iloc[0],
                            #end_date=datetime.strptime(datas[-100], '%d/%m/%Y').date(),
                            display_format='D/MM/YY',
                            start_date_placeholder_text="Data Inicial",
                            end_date_placeholder_text="Data Final",
                            )
                        ]
                    ),              

                    html.Div(
                        id = 'row_rodape_col_1',
                        className="four columns column_style",
                        children = [
                            html.Div(
                                dcc.Dropdown(
                                id='mark_vars',
                                options=[
                                    {'label': 'Temperatura', 'value': 'temperatura'},
                                    {'label': 'Pressão Atmosférica', 'value': 'pressao'},
                                    {'label': 'Umidade Relativa', 'value': 'umidade'},
                                    {'label': 'Velocidade do Vento', 'value': 'velocidade'},
                                    {'label': 'DHI (Diffuse Horizontal Irradiance)', 'value': 'dhi'},
                                    {'label': 'DNI (Direct Normal Irradiance)', 'value': 'dni'},
                                    {'label': 'GHI (Global Horizontal Irradiance)', 'value': 'ghi'},
                                ],
                                multi=True
                                )
                            )
                        
                        ]
                        )
                ],
            ),

            None
        )
    except:
        raise PreventUpdate
'''

@app.callback(
    [
        Output('1º Aplicação Web_column_markdown3', 'children'),
    ],
    Input('mark_vars', 'value'),
    Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')
)
def update(vars, start_date, end_date):
    try:
        

        start_date = datetime.fromisoformat(start_date)
        start_date = start_date.strftime('%Y-%m-%d')

        end_date = datetime.fromisoformat(end_date)
        end_date = end_date.strftime('%Y-%m-%d')

        print(vars)
        print(start_date)
        print(end_date)


        df_global = pd.read_csv('apps\callback\dados_estacao_cear_puro.csv')

        df_global['Date'] = pd.to_datetime(df_global['Datetime']).dt.date

        print(df_global['Date'])
        id_inicial = df_global[df_global['Date'] == start_date].index[0]
        id_final   = df_global[df_global['Date'] == end_date].index[0]

        df_f = df_global.loc[id_inicial:id_final]

        print(df_f)

        return html.Div(
                id = 'row_rodape_col_1',
                className="row row_style",
                children = [
                    dcc.Markdown('''
                        *This text will be italic*

                        _This will also be italic_


                        **This text will be bold**

                        __This will also be bold__

                        _You **can** combine them_
                    ''')
                ]
        )
    except:
        raise PreventUpdate