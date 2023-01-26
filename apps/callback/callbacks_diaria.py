# -*- coding: utf-8 -*-

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


dashboard_name = 'Plataforma Multi-Mapa CEAR/UFPB'
x = 0

# Função que recebe um dataframe com os parâmetros necessários para criar o gráfico de rosa dos ventos
# Parâmetros:: 
# (mag_binned)              Intervalo em que a velocidade do vento se encontra (ex.: 0 - 1)
# (dir_binned)              Direção do vento convertida para pontos cardeais (ex.: Norte, Sul, Noroeste)
# (frequency)               Frequência que um intervalo aparece em determinado ponto cardeal (ex: 5 vezes é tido o intervalo 0 - 1 para Norte)
def wind_rose(grp):
    fig = px.bar_polar(grp, r='frequency', theta='dir_binned', color='mag_binned', color_discrete_sequence = px.colors.qualitative.G10, template='plotly_white')
    fig.update_layout(
        title={
        'text': 'Velocidade e Direção do Vento',    
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        },
        title_font_size=20,
        title_font_family='Arial',
        margin=dict(
            t=80,
            b=35,
            r=0,
            l=5
        ),
        height=350,
        legend_title_text='Velocidade Vento(m/s)',
        legend_font_size=15,
        legend_x=1.3,
        legend_y=1.0,
        #paper_bgcolor = "rgb(186, 235, 235)",
        legend_xanchor='right',
        polar = dict(radialaxis = dict(tickfont_size=1, gridcolor='black'), angularaxis=dict(gridcolor='black')),
        font=dict(
            family="Arial",
            size=18,
            color="black")
    )
    return fig

# Função que preenche as horas faltantes do dataframe recebido
# Ex.: é recebido um dataframe até 6:20, a função vai preencher o horário até as 23:59 sem adicionar nenhum dado climático
def fill_dataframe(df):
    data_inicial = df.iloc[0][0]
    
    date = datetime.strptime(data_inicial, "%Y-%m-%d %H:%M:%S")
    modified_date = date + timedelta(days=1)
    data_final = datetime.strftime(modified_date, "%Y-%m-%d %H:%M:%S")
    
    add_row = df.iloc[0]
    add_row[0] = data_final
    df.loc[len(df)] = add_row
    
    df_aux = pd.DataFrame(index = pd.date_range(df.iloc[0][0][0:10], df.iloc[-1][0][0:10], freq='10Min'))
    df_f = pd.merge(df_aux, df, left_index = True, right_index = True, how = 'left')
    df_f.reset_index(inplace=True)
    df_f = df_f.drop(['Datetime'], axis=1)
    df_f.columns = df_f.columns.str.replace('index', 'Datetime')
    
    df = df.iloc[:-1]
    
    df_f = df_f.iloc[len(df):]
    
    df_f = pd.concat([df, df_f])
    
    return df_f
    



# ---------------------------------------------------------
# ----------------------------------------------- callbacks
# ---------------------------------------------------------

# Callback do componente 'interval' necessário para ficar atualizando a aplicação
# O componente tá configurado para ser atualizado a cada 5 segundos
@app.callback(
    Output('Plataforma Multi-Mapa CEAR/UFPB_column_vazia_2', 'children'),
    Input('Plataforma Multi-Mapa CEAR/UFPB_column_vazia', 'children'),
)
def update(values):

    return html.Div(
        id="row_topo",
        className='row row_style',
        children=[
            html.Div(
                dcc.Interval(
                    id='interval-component',
                    interval=5*1000, # in milliseconds
                    n_intervals=0
                )
            )
        ],
    )


# Callback principal do sistema
@app.callback(
    [
        Output('Plataforma Multi-Mapa CEAR/UFPB_column_markdown1', 'children'),
        Output('Plataforma Multi-Mapa CEAR/UFPB_column_markdown2', 'children'),
        Output('Plataforma Multi-Mapa CEAR/UFPB_column_markdown3', 'children'),
        Output('Plataforma Multi-Mapa CEAR/UFPB_column_titulo', 'children'),
    ],
    Input('interval-component', 'n_intervals'),
)
def update(result):
    # variável global necessário para atualizar o componente visualmente, 
    # ela é responsável por guardar o índice de exibição dos dados do dataframe
    global x

    try:
        df_global = pd.read_csv('apps\callback\dados_estacao_cear_puro.csv')

        # trecho de código responsável por pegar os dados do dia da variável 'comp'
        comp = '2022-10-02'
        df_temp = df_global.query("Datetime.str.contains(@comp, na=False)", engine='python')

        # atualizando os dados de exibição através do incremento da variável que será usada como índice de intervalo final
        x = x + 10

        # preenchendo o dataframe e aumentando os índices de exibição com a variável 'x'
        df_fill = fill_dataframe(df_temp[0:(50 + x)])
        df_fill = df_fill.iloc[:-1] 

        # dicionários para exibição textual dos dados climáticos 
        dicTemp = {
                "className": "two columns column_style",
                "type": "markdown",

                "id": "mark_temp",
                "text": [
                    "## Temperatura: " ,
                    #"## Max: " + str(round(df_irradiance['Temp_Max'].loc[len(df_irradiance) - 1], 2)) + " °C",
                    "## " + str(round(df_fill['Temp_Med'].iloc[(50 + x) - 1], 2)) + " °C",
                    #"## Min: " + str(round(df_irradiance['Temp_Min'].loc[len(df_irradiance) - 1], 2)) + " °C"

                ],
            }
        
        dicUmi = {
                "className": "two columns column_style",
                "type": "markdown",

                "id": "mark_umi",
                "text": [
                    "## Umidade Relativa: " ,
                    "## " + str(round(df_fill['Umi_Med'].iloc[(50 + x) - 1], 2)) + " %",
                ],
            }

        dicPress = {
                "className": "two columns column_style",
                "type": "markdown",

                "id": "mark_press",
                "text": [
                    "## Pressão Atmosférica: " ,
                    "## " + str(round(df_fill['Air_Press_Med'].iloc[(50 + x) - 1], 2)) + " hPa",
                ],
            }

        dicChuva = {
                "className": "two columns column_style",
                "type": "markdown",

                "id": "mark_chuva",
                "text": [
                    "## Precipitação Acumulada: ",
                    "## " + str(round(df_fill['Precip_Sum'].iloc[(50 + x) - 1], 2)) + " mm"
                ],
            }
        '''
        dicDHI = {
                "className": "four columns column_style",
                "type": "markdown",

                "id": "mark_dhi",
                "text": [
                    "## DHI: " + str(randi2) + " w/m²"
                ],
            }

        dicDNI = {
                "className": "four columns column_style",
                "type": "markdown",

                "id": "mark_dni",
                "text": [
                    "## DNI: " + str(randi) + " w/m²"
                ],
            }
        '''
        dicGHI = {
                "className": "two columns column_style",
                "type": "markdown",

                "id": "mark_ghi",
                "text": [
                    "## Irradiância Global: ",
                    "## " + str(round(df_fill['GHI_Med'].iloc[(50 + x) - 1], 2)) + " W/m²"
                ],
            }

        dicVento = {
                "className": "two columns column_style",
                "type": "markdown",

                "id": "mark_vento",
                "text": [
                    "## Velocidade Vento: ",
                    "## " + str(round(df_fill['Wind_Speed_Med'].iloc[(50 + x) - 1], 2)) + " m/s"
                ],
            }
        

        dicMM = {
                "className": "six columns column_style",
                "type": "markdown",

                "id": "mark_mm",
                "text": [
                    "# Plataforma Multi-Mapa CEAR/UFPB",
                    "Estação Meteorológica do CEAR"
                ],
            }


        
        dicTemp = json2dash.validate_dic_layout_row_column(
                app.dic_app['default_fcns_per_type'], dicTemp)
        temp = json2dash.build_div_row_column(dashboard_name, dicTemp)

        dicUmi = json2dash.validate_dic_layout_row_column(
                app.dic_app['default_fcns_per_type'], dicUmi)
        umi = json2dash.build_div_row_column(dashboard_name, dicUmi)

        dicPress = json2dash.validate_dic_layout_row_column(
                app.dic_app['default_fcns_per_type'], dicPress)
        press = json2dash.build_div_row_column(dashboard_name, dicPress)

        dicChuva = json2dash.validate_dic_layout_row_column(
                app.dic_app['default_fcns_per_type'], dicChuva)
        chuva = json2dash.build_div_row_column(dashboard_name, dicChuva)

        '''
        dicDHI = json2dash.validate_dic_layout_row_column(
                app.dic_app['default_fcns_per_type'], dicDHI)
        DHI = json2dash.build_div_row_column(dashboard_name, dicDHI)

        dicDNI = json2dash.validate_dic_layout_row_column(
                app.dic_app['default_fcns_per_type'], dicDNI)
        DNI = json2dash.build_div_row_column(dashboard_name, dicDNI)
        '''
        dicGHI = json2dash.validate_dic_layout_row_column(
                app.dic_app['default_fcns_per_type'], dicGHI)
        GHI = json2dash.build_div_row_column(dashboard_name, dicGHI)
        
        dicVento = json2dash.validate_dic_layout_row_column(
                app.dic_app['default_fcns_per_type'], dicVento)
        vento = json2dash.build_div_row_column(dashboard_name, dicVento)


        dicMM = json2dash.validate_dic_layout_row_column(
                app.dic_app['default_fcns_per_type'], dicMM)
        mm = json2dash.build_div_row_column(dashboard_name, dicMM)
        


        # criação dos índices de intervalo onde se encontram os dados de velocidade dos ventos
        bins_mag_labels = ['0 - 1','1 - 2','2 - 3','3 - 4','4 - 5', '5 - 6', '6 - 7', '7 >']
        bins = [0, 1, 2, 3, 4, 5, 6, 7, 15]
        df_temp['mag_binned'] = pd.cut(df_fill['Wind_Speed_Med'].iloc[0:(50 + x)], bins, labels=bins_mag_labels)

        #criação dos índices de conversão da direção em pontos cardeais 
        bins_dir = [0, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180, 202.5, 225, 247.5, 270, 292.5, 315, 337.5, 360]
        bins_dir_labels = ['N','NNE','NE','LNE','L','LSE','SE','SSE','S','SSO','SO','OSO','O','ONO','NO','NNO']

        df_temp['dir_binned'] = pd.cut(df_fill['Wind_Direction_Med'].iloc[0:(50 + x)],bins_dir, labels=bins_dir_labels)

        # criação do dataframe com índices de intervalo de velocidade dos ventos, pontos cardeais e a frequência com que se relacionam
        grp = df_temp.groupby(['mag_binned', 'dir_binned']).size().reset_index(name="frequency")     
        grp = grp.sort_values(by=['dir_binned', 'mag_binned', 'frequency'])

        # armazenando data e hora para exibir textual no dashboard
        datas = pd.to_datetime(df_fill['Datetime'].iloc[0:(50 + x)]).dt.date
        horas = pd.to_datetime(df_fill['Datetime'].iloc[0:(50 + x)]).dt.time

        data_f = str(datas.iloc[-1].day) + "/" + str(datas.iloc[-1].month) + "/" + str(datas.iloc[-1].year)

        horas_fill = pd.to_datetime(df_fill['Datetime']).dt.time




        # return para criar ou finalizar os componentes exibidos no dashboard
        return (
            # componentes textuais em markdown
            html.Div(
                id = 'row_rodape_col_1',
                className = "row row_style_col1",
                children = [temp, press, umi, GHI, vento, chuva],
            ),
            # gráfico de temperatura
            html.Div(
                    id="row_meio",
                    className='row row_style',
                    children=[
                        html.Div(
                            dcc.Graph(
                                id='graph_temp',
                                className="four columns column_style",
                                figure = {
                                    'data': [
                                        {'x': df_fill['Datetime'], 'y': df_fill['Temp_Max'], 'type': 'line', 'name': 'Máx'},
                                        {'x': df_fill['Datetime'], 'y': df_fill['Temp_Med'], 'type': 'line', 'name': 'Méd'},
                                        {'x': df_fill['Datetime'], 'y': df_fill['Temp_Min'], 'type': 'line', 'name': 'Mín'},
                                        {'orientation': 'v',}
                                    ],
                                    'layout': {
                                        'title': 'Temperatura',
                                        'height': '350',
                                        'margin': {
                                            'l': 45,
                                            'r': 35,
                                            't': 60,
                                            'b': 50
                                        },
                                        'font':{
                                            'family': "Arial",
                                            'size': '15'
                                        },
                                        'legend': {
                                                'orientation': 'h',
                                                'yarchor': 'bottom',
                                                'y': '1.09',
                                                'xanchor': 'right',
                                                'x': '1'
                                        },
                                        'xaxis': {
                                            'tickangle': '360',
                                            'nticks': '8',
                                            'tickformat': "%H:%M"
                                        },
                                        'yaxis': {
                                            'title': '(°C)'
                                        }
                                        
                                    },
                                    
                                    
                                },
                                
                            ),
                        ),

                        # gráfico de pressão atmosférica
                        html.Div(
                            dcc.Graph(
                                id='graph_press',
                                className="four columns column_style",
                                figure = {
                                    'data': [
                                        {'x': df_fill['Datetime'], 'y': df_fill['Air_Press_Max'], 'type': 'line', 'name': 'Máx'},
                                        {'x': df_fill['Datetime'], 'y': df_fill['Air_Press_Med'], 'type': 'line', 'name': 'Méd'},
                                        {'x': df_fill['Datetime'], 'y': df_fill['Air_Press_Min'], 'type': 'line', 'name': 'Mín'},
                                        {'orientation': 'v',}
                                    ],
                                    'layout': {
                                        'title': 'Pressão Atmosférica',
                                        'height': '350',
                                        'margin': {
                                            'l': 75,
                                            'r': 35,
                                            't': 60,
                                            'b': 50
                                        },
                                        'font':{
                                            'family': "Arial",
                                            'size': '15'
                                        },
                                        'legend': 
                                            {
                                                'orientation': 'h',
                                                'yarchor': 'bottom',
                                                'y': '1.09',
                                                'xanchor': 'right',
                                                'x': '1'
                                            },
                                        'xaxis': {
                                            'tickangle': '360',
                                            'nticks': '8',
                                            'tickformat': "%H:%M",
                                        },
                                        'yaxis': {
                                            'title': '(hPa)'
                                        }
                                    }
                                },
                                
                            ),
                        ),

                        # gráfico de umidade
                        html.Div(
                            dcc.Graph(
                                id='graph_umi',
                                className="four columns column_style",
                                figure = {
                                    'data': [
                                        {'x': df_fill['Datetime'], 'y': df_fill['Umi_Max'], 'type': 'line', 'name': 'Máx'},
                                        {'x': df_fill['Datetime'], 'y': df_fill['Umi_Med'], 'type': 'line', 'name': 'Méd'},
                                        {'x': df_fill['Datetime'], 'y': df_fill['Umi_Min'], 'type': 'line', 'name': 'Mín'},
                                        {'orientation': 'v',}
                                    ],
                                    'layout': {
                                        'title': 'Umidade Relativa',
                                        'height': '350',
                                        'margin': {
                                            'l': 45,
                                            'r': 35,
                                            't': 60,
                                            'b': 50
                                        },
                                        'font':{
                                            'family': "Arial",
                                            'size': '15'
                                        },
                                        'legend': 
                                            {
                                                'orientation': 'h',
                                                'yarchor': 'bottom',
                                                'y': '1.09',
                                                'xanchor': 'right',
                                                'x': '1'
                                            },
                                        'xaxis': {
                                            'tickangle': '360',
                                            'nticks': '8',
                                            'tickformat': "%H:%M",
                                        },
                                        'yaxis': {
                                            'title': '(%)'
                                        } 
                                    }
                                },
                                
                            ),
                        ),
                    ],
                ),

        # gráfico de irradiância
        html.Div(
                    id="row_meio2",
                    className='row row_style2',
                    children=[
                        html.Div(
                            dcc.Graph(
                                id='graph_irradiance',
                                className="eight columns column_style",
                                figure = {
                                    'data': [
                                        {'x': df_fill['Datetime'], 'y': df_fill['DHI_Med'], 'type': 'line', 'name': 'DHI'},
                                        {'x': df_fill['Datetime'], 'y': df_fill['DNI_Med'], 'type': 'line', 'name': u'DNI'},
                                        {'x': df_fill['Datetime'], 'y': df_fill['GHI_Med'], 'type': 'line', 'name': u'GHI'},
                                        {'orientation': 'v',}
                                    ],
                                    'layout': {
                                        'title': 'Irradiância ',
                                        'height': '350',
                                        'font':{
                                            'family': "Arial",
                                            'size': '15'
                                        },
                                        'margin': {
                                            'l': 50,
                                            'r': 35,
                                            't': 60,
                                            'b': 50
                                        },
                                        'legend': 
                                            {
                                                'orientation': 'h',
                                                'yarchor': 'bottom',
                                                'y': '1.09',
                                                'xanchor': 'right',
                                                'x': '1'
                                            },
                                        'xaxis': {
                                            'tickangle': '360',
                                            'nticks': '12',
                                            'tickformat': "%H:%M",
                                        },
                                        'yaxis': {
                                            'title': '(W/m²)'
                                        }
                                    }
                                },
                                
                            ),
                        ),

                        # gráfico de rosa dos ventos
                        html.Div(
                            dcc.Graph(
                                id='dirVento',
                                className = "four columns column_style",
                                figure = wind_rose(grp)     
                            ),
                        )
                    ]
                ),

                # componente textual para hora e data
                html.Div(
                    id = 'row_rodape_col_1',
                    className = "row row_style_col1",
                    children = [
                        html.Div(
                            id='markdown_MM',
                            className = "row row_style_col1_row1",
                            children = [
                                mm,
                                
                                html.Div(
                                    id='display_data',
                                    className = "three columns column_style",
                                    children = [
                                        daq.LEDDisplay(
                                            value = str(data_f).replace("/", "."),
                                            color = "black",
                                            size = 20,
                                        )
                                    ]
                                ),

                                html.Div(
                                    id='display_hora',
                                    className = "three columns column_style",
                                    children = [
                                        daq.LEDDisplay(
                                            value = horas.iloc[-1],
                                            color = "black",
                                            size = 20
                                        )
                                    ]
                                )

                            ]
                        ),

                        

                        
                        
                    ],
                ),
        )           


    except:
        x = 0
        raise PreventUpdate

