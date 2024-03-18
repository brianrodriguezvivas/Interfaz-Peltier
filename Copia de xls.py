# Importar bibliotecas y módulos necesarios
from dash import Dash, dcc, html, Input, Output, callback, Patch, clientside_callback
import plotly.express as px
import plotly.io as pio
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
# import dash_ag_grid as dag
import pandas as pd
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import numpy as np
import dash
from dash_iconify import DashIconify
import os
from Mediciones import Resultados 

# Crear DataFrame
# Cargar la hoja de estilo Bootstrap para dar estilo a los componentes
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"



# if 'REDIS_URL' in os.environ:
#     # Use Redis & Celery if REDIS_URL set as an env variable
#     from celery import Celery
#     celery_app = Celery(__name__, broker=os.environ['REDIS_URL'], backend=os.environ['REDIS_URL'])
#     background_callback_manager = CeleryManager(celery_app)

# Crear la aplicación Dash con temas de Bootstrap y hojas de estilo externas
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, dbc_css],)





# Crear un interruptor de modo de color con opciones de tema claro/oscuro
color_mode_switch =  html.Span(
    [
        dbc.Label(className="fa fa-moon", html_for="switch"),
        dbc.Switch( id="switch", value=True, className="d-inline-block ms-1", persistence=True),
        dbc.Label(className="fa fa-sun", html_for="switch"),
    ]
)

# Los controles de tema incluyen un selector de tema y el interruptor de modo de color
theme_controls = html.Div(
    [ThemeChangerAIO(aio_id="theme"), color_mode_switch],
    className="hstack gap-3 mt-4"
)


Temas = ["bootstrap"]



#----------------------------------- Logos-----------------------------------

logo1 = html.Div(
    html.Img(src='assets/logo.png', height='80px', width='auto')
)
logo2 = html.Div(
    html.Img(src='assets/udea-png.png', height='80px', width='auto')
)


# ------------------------------------Botones-----------------------------------
def Botones (nombre):
    Botones= html.Div(
    
        [dmc.Button("CSV",
                    variant="gradient",
                    id=f"btn_csv_{nombre}",
                    leftIcon=[DashIconify(icon="fa-solid:file-download", width=15)],
                    style={"padding": "10px", "background": "#3498DB", "border": "1px solid black",
                        "margin-top": "10px", "margin-bottom": "10px"},
                ),
        
        dcc.Download(id=f"descarga_dataframe_csv_{nombre}"),

        dmc.Button ("Medir",
                    variant="gradient",
                    id=f"btn_medir_{nombre}",
                    leftIcon=[DashIconify(icon="fa-solid:play", width=15)],
                    style={"padding": "10px", "background": "#3498DB", "border": "1px solid black",
                        "margin-top": "10px", "margin-left": "20px","margin-bottom": "5px"}
                ),


        dmc.Button("Reiniciar todo", 
                    id=f"btn_reset_all_{nombre}", 
                    n_clicks=0,
                    leftIcon=[DashIconify(icon="grommet-icons:power-reset", width=20)],  
                    style={"padding": "10px", "background": "#3498DB", "border": "1px solid black",
                        "margin-top": "10px","margin-left": "20px", "margin-right": "20px","margin-bottom": "10px"},
                )


        ],style={"margin-left": "10px"}

    )
    
    return Botones




#------------------------------Función para graficar -----------------------------

def graficar(titulo,lista_dataframes,xmedida = "U",ymedida = "U", xtitle="x", ytitle="y"):
    
    fig = px.scatter(title=f'{titulo}')
    
    # Iterar sobre la lista de DataFrames y agregar los puntos al gráfico
    for i in range(1,len(lista_dataframes)):
        df = lista_dataframes[i]
        
        fig.add_scatter(x=df[f"{df.columns[0]}"], y=df[f"{df.columns[1]}"], 
                        mode='lines+markers', 
                        name=f'{titulo}',
                        marker=dict(symbol='circle-open', 
                        size=10, 
                        line=dict(color='black', width=2),),
        )

    fig.update_xaxes(title_text=f'{xtitle} {xmedida}', 
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray'
    )
    
    fig.update_yaxes(title_text=f'{ytitle} {ymedida}',
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray'
    )
    
    return fig
    


#-----------------------------Botones de medición V-C----------------------------

Botones_V_C = Botones("V-C") #Botones para medir Voltaje-Corriente
Botones_V_P = Botones("V-P") #Botones para medir Voltaje-Potencia
Botones_T_V = Botones("T-V") #Botones para medir Temperatura-Voltaje







#-------------------------------Listas------------------------------------
list_df_Voltage_Current = [pd.DataFrame()] #Lista de DataFrames Voltage-Current
list_df_Temperature_Voltage = [pd.DataFrame()] #Lista de DataFrames Temperature-Voltage
lista_VOC = [html.H5("Medidas: "),html.Hr()]
lista_df_Voltage_Power= [pd.DataFrame()] #Lista de DataFrames Voltage-Power
G1 = pd.DataFrame()
IP_list = ["192.168.0.100"]



#------------------Callback Ckeck_list de cuadro de seleccion temperatura--------------------

def checklist_sensor(nombre,name_label):
    checklist_sensor = dcc.Checklist(
        [
            {
                "label": html.Div([f'{name_label}'], style={ 'font-size': 20, 'padding': '0px'}), 
                "value": True,
            },                
        ],
        labelStyle={"display": "flex", "align-items": "center", "font-size": 20},
        inputStyle={ 
            "width": "20px",
            "height": "20px", 
        },
        id=f"checklist_{nombre}",  
    )
    return checklist_sensor


#checklist_sensor_1 = checklist_fuente
checklist_V_C = checklist_sensor("sensor_V_C","Sensor V-C")
checklist_fuente = checklist_sensor("fuente","Fuente")
checklist_temperature = checklist_sensor("temperatura","Temperatura")

NO_cheklist1 = html.Div(id="NO_checklist1")
NO_cheklist2 = html.Div(id="NO_checklist2")
NO_cheklist3 = html.Div(id="NO_checklist3")

list_sensor_V_C = [False]
list_sensor_temperature = [False]
list_fuente = [False]

def update_sensor_list(selected_value, sensor_list):
    if selected_value:
        sensor_list.clear()
        sensor_list.append(True)
    else:
        sensor_list.clear()
        sensor_list.append(False)
        # print(chanel_selection_list1)
# Crear un callback para actualizar el contenido del Div con el valor seleccionado

@app.callback(
    [Output("NO_checklist1", "children"),
    Output("NO_checklist2", "children"),
    Output("NO_checklist3", "children"),],
    [Input("checklist_fuente", "value"),
    Input("checklist_temperatura", "value"),
    Input("checklist_sensor_V_C", "value")],
    prevet_initial_call=True
)

def callback_selection_temperature(select_value1, select_value2,select_value3):
    update_sensor_list(select_value1, list_fuente)
    update_sensor_list(select_value2, list_sensor_temperature)
    update_sensor_list(select_value3, list_sensor_V_C)
    
    return '','',''


Alineacion_ckecklist_V_C= dbc.Container([
    html.Div([
        checklist_V_C,
        NO_cheklist3,
    ], style={'display': 'flex','align-items': 'center'})
], className="mt-4")

Alineacion_ckecklist_temperature = dbc.Container([
    html.Div([
        checklist_temperature,
        NO_cheklist2,
    ], style={'display': 'flex','align-items': 'center'})
], className="mt-4")
    
#------------------------------Listas_despegables----------------------------------

chanel_selection_list1 = []
chanel_selection_list2 = []

opciones_dropdown = [{'label': f'Canal {i}', 'value': i} for i in range(1, 21)]

NO_dropnow1 = html.Div(id="output_NO_dropnow1")
NO_dropnow2 = html.Div(id="output_NO_dropnow2")

def dropdown_sensor(nombre):
    opciones_dropdown = [{'label': f'Canal {i}', 'value': i} for i in range(1, 21)]
    dropdown_sensor = html.Div([
        dcc.Dropdown(
            id=f'mi-dropdown_{nombre}',
            options=opciones_dropdown,
            multi=True,
            value=[],
            style={'width': '250px'}
        )   
    ])
    return dropdown_sensor

dropdown_sensor_1 = dropdown_sensor("sensor1")
dropdown_sensor_2 = dropdown_sensor("sensor2")

@app.callback(
    Output(f'output_NO_dropnow1', 'children',allow_duplicate=True),
    [Input(f'mi-dropdown_sensor1', 'value')],
    prevent_initial_call=True
)
def actualizar_dropdown(value):
    if value ==[]:
        chanel_selection_list1.clear()
        
    return ""


@callback(
    [Output('output_NO_dropnow1', 'children'),
    Output('output_NO_dropnow2', 'children')],
    [Input('mi-dropdown_sensor1', 'value'),
    Input('mi-dropdown_sensor2', 'value')],
    prevent_initial_call=True
)
def callback_selection_chanel(value1,value2):
    if value1:
        chanel_selection_list1.clear()
        chanel_selection_list1.append(value1)
        # print(chanel_selection_list1)
    if value2:
        chanel_selection_list2.clear()
        chanel_selection_list2.append(value2)
        # print(chanel_selection_list2)
    return '',''




    #-----------------------------Alerta de resultado-----------------------------

alerta_medidas = dbc.Alert(lista_VOC,
    id="resultado-alert",
    color="success",
    is_open=True,
    style={"height": "44vh", "overflow": "auto",},
    # Establecer en True para que quede permanentemente visible
)




#-----------------------------Callback de medición V-C----------------------------



@app.callback(
    [Output("grafico", "figure"),
    Output("grafico2", "figure"),
    Output("grafico3", "figure"),
    Output("resultado-alert", "children"),
    # Output("grid","rowData"),
    ],
    Input("btn_medir_V-C", "n_clicks"),
    
    prevent_initial_call=True,
)




def medir_callback(n_clicks):

    ############################################################
    temperature_selection = list_sensor_temperature[0] #COrregir
    
    ############################################################
    chanel_selection = chanel_selection_list1[0]
    valores = Resultados(IP=IP_list[-1],Temperature =temperature_selection , chanel = chanel_selection) # Selecion de True o False para medir temperatura
    if len(valores) == 3:
        
        df_voltage_current,measurement_voltage_Voc,df_voltage_power = valores
        
        df_voltage_current = df_voltage_current.rename(columns={
                                df_voltage_current.columns[0]: f'{df_voltage_current.columns[0]}_{n_clicks}',
                                df_voltage_current.columns[1]: f'{df_voltage_current.columns[1]}_{n_clicks}'})
        
        list_df_Voltage_Current.append(df_voltage_current)
        lista_df_Voltage_Power.append(df_voltage_power)
        
        fig = graficar("Curva V_I TEC-12706",list_df_Voltage_Current,
                    xmedida="[V]",ymedida="[A]",
                    xtitle="Voltage",ytitle="Current")
        
        fig3 = graficar("Voltage vs Power",lista_df_Voltage_Power,
                        xmedida="[V]",ymedida="[W]",
                        xtitle="Voltage", ytitle="Power")
        fig2 = dash.no_update
        
        
        lista_VOC.append(html.Small(f"VOC: {measurement_voltage_Voc} [V]"))
        lista_VOC.append(html.Br())
        G1 = pd.concat(list_df_Voltage_Current,axis=1)
        
        
        return  fig, fig2, fig3, lista_VOC ,100,f"{100} %"
    
    if len(valores) == 4:
        df_voltage_current,measurement_voltage_Voc,df_voltage_power,df_temperature_voltage = valores
        df_temperature_voltage = df_temperature_voltage.rename(columns={
                                    df_temperature_voltage.columns[0]: f'{df_temperature_voltage.columns[0]}_{n_clicks}',
                                    df_temperature_voltage.columns[1]: f'{df_temperature_voltage.columns[1]}_{n_clicks}'})
        
        
        df_voltage_current = df_voltage_current.rename(columns={
                                df_voltage_current.columns[0]: f'{df_voltage_current.columns[0]}_{n_clicks}',
                                df_voltage_current.columns[1]: f'{df_voltage_current.columns[1]}_{n_clicks}'})
        
        list_df_Voltage_Current.append(df_voltage_current)
        list_df_Temperature_Voltage.append(df_temperature_voltage)
        lista_df_Voltage_Power.append(df_voltage_power)
        
        fig = graficar("Curva V_I TEC-12706",list_df_Voltage_Current,xmedida="[V]",ymedida="[A]")
        fig2 = graficar("Voltaje vs Temperatura",list_df_Temperature_Voltage,xmedida="[V]",ymedida="[°C]")
        fig3 = graficar("Voltaje vs Potencia",lista_df_Voltage_Power,xmedida="[V]",ymedida="[W]")
        
        Temperatura_str = np.array(list_df_Temperature_Voltage) 
        
        lista_VOC.append(html.Small(f"VOC: {measurement_voltage_Voc} [V] T_prom: {np.mean(Temperatura_str.astype(int))} [W]"))
        lista_VOC.append(html.Br())
        G1 = pd.concat(list_df_Voltage_Current,axis=1)
        
        return  fig, fig2, fig3, lista_VOC 
        

    
    
    


#-----------------------------Callback de Descarga CSV----------------------------


# Callback para descargar como CSV
@app.callback(
    Output("descarga_dataframe_csv_V-C", "data"),
    Input("btn_csv_V-C", "n_clicks"),
    prevent_initial_call=True,
    
)
def csv_callback(btn_csv):
    df = pd.concat(list_df_Voltage_Current, axis=1)
    
    if not btn_csv:
        raise Dash.exceptions.PreventUpdate

    return dcc.send_data_frame(df.to_csv, "medicion.csv")



# ------------------------Entrada de texto y salida de texto-------------------------


text_input = html.Div(
    [   
        dbc.Input(id="IP", placeholder="192.168.0.100", type="text"),
        html.Br(),   
        
    ],style= {'margin-down': "0px"},
)

IP_layout = html.Div([
    html.H6("Protocolo de Internet (IP)",style={'font-size': '20px','margin-right': '20px'}),
    checklist_fuente,
], style={'display': 'flex', 'justify-content': 'flex-start'})

# Controles generales incluyendo desplegable, lista de verificación y control deslizante
controls_fuente = dbc.Card(
    [IP_layout,text_input,NO_cheklist1],
    body=True,
)

NO_output = html.Div(id="NO_output")
@app.callback(Output("NO_output", "children"),
            [Input("IP", "value")],
            prevent_initial_call=True,
            
            )


def input_IP(IP):
    IP_list.append(IP)
    return ''


#-----------------------------Configuración de la cuadrícula AG para mostrar datos-------------


# cuadricula= dag.AgGrid(
#         id="grid",
#         columnDefs=[{"field": i} for i in G1.columns],
#         rowData=G1.to_dict("records"),
#         defaultColDef={"flex": 1, "minWidth": 120, "sortable": True, "resizable": True, "filter": True},
#         dashGridOptions={"rowSelection":"multiple"},    

#)

#-----------------------------Callback de Reinicio----------------------------

@app.callback(
    [Output("grafico", "figure",allow_duplicate=True),
    Output("grafico2", "figure",allow_duplicate=True), 
    Output("grafico3", "figure",allow_duplicate=True),
    Output("resultado-alert", "children",allow_duplicate=True)],
    Input("btn_reset_all_V-C", "n_clicks"),
    prevent_initial_call=True
)

def reset(n_clicks):
    global list_df_Voltage_Current
    global list_df_Temperature_Voltage
    global lista_df_Voltage_Power
    
    lista_VOC.clear()
    lista_VOC.append(html.H5("Medidas: "))  # Limpiar lista de VOC
    lista_VOC.append( html.Hr())
    
    fig = px.scatter(template="bootstrap")
    fig2 = px.scatter(template="bootstrap")
    fig3 = px.scatter(template="bootstrap")
    
    list_df_Voltage_Current = [pd.DataFrame()]
    list_df_Temperature_Voltage = [pd.DataFrame()]
    lista_df_Voltage_Power = [pd.DataFrame()]
    chanel_selection_list1 = []
    
    return fig, fig2, fig3, lista_VOC   
# ------------------------Pestañas con gráficos y cuadrícula AG-------------------------------




tab1 = dbc.Tab([dcc.Graph(id="grafico", figure=px.line(template="bootstrap")),Botones_V_C], label="Voltaje-Corriente")
tab3 = dbc.Tab([dcc.Graph(id="grafico2",figure=px.line(template="bootstrap")),Botones_V_P], label="Voltaje-Temperatura")
tab2 = dbc.Tab([dcc.Graph(id="grafico3",figure=px.line(template="bootstrap")),Botones_T_V], label="Voltaje-Potencia")
# tab4 = dbc.Tab([cuadricula], label="Table", className="p-4")
tabs = dbc.Card(dbc.Tabs([tab1, tab2, tab3]))

#---------------------------------------Titulo Mediciones---------------------------------------

header = dbc.Alert(
        [html.Div([html.H1("Peltier")], style={"text-align": "center"}),],
        id="Titulo",
        color="success",
        is_open=True,
        style={"height": "10vh"},
        )


logos_container = html.Div([logo1, logo2], style={'display': 'flex'})



# ------------------------Diseño de la aplicación Dash-------------------------
app.layout = dbc.Container([   
    dbc.Row([
        dbc.Col([logos_container]),
        dbc.Col([header]),
    ], style={'padding': '10px'}),
    dbc.Row([
        dbc.Col([
            dbc.Row([controls_fuente, NO_output], style={"padding": "0px 5px 10px 10px"}),
            dbc.Row([alerta_medidas], style={"padding": "5px 5px 0px 10px"}),  # Ajuste de relleno aquí
            dbc.Row([
                
                
            ], style={"padding": "0px 5px 5px 5px"}),
        ]),
        dbc.Col([
            dbc.Row([dbc.Col([tabs], width=12)], id='fila_tabs'),
        ], width=8, id='columna_tabs_botones'),
        
    ]), 
    dbc.Row([
        dbc.Col([
                    dbc.Row([Alineacion_ckecklist_V_C]),
                    dbc.Row([dropdown_sensor_1, NO_dropnow1]),
                ]),
        dbc.Col([
                    dbc.Row([Alineacion_ckecklist_temperature]),
                    dbc.Row([dropdown_sensor_2, NO_dropnow2]),
                ]),
        dbc.Col([],),
        dbc.Col([theme_controls], style={"padding": "20px", "display": "flex", "justify-content": "end"}),
    ],style={"padding": "0px 0px 5px 5px"}),
    
],
fluid=True,
className="dbc dbc-ag-grid")







# Actualiza el modo de color global claro/oscuro de Bootstrap
clientside_callback(
    """
    switchOn => {       
    switchOn
        ? document.documentElement.setAttribute('data-bs-theme', 'light')
        : document.documentElement.setAttribute('data-bs-theme', 'dark')
    return window.dash_clientside.no_update
    }
    """,
    Output("switch", "id"),
    Input("switch", "value"),
)

if __name__ == "__main__":
    app.run_server(debug=True)
    # app.run_server(debug=False, host='0.0.0.0')
