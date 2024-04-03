# Importar bibliotecas y módulos necesarios
from dash import Dash, dcc, html, Input, Output, callback, Patch, clientside_callback,State
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

logo1_style = {'flex': '0 0 auto', 'margin-right': 'auto'}  # Para alinear el primer logo hacia la izquierda
logo2_style = {'flex': '0 0 auto', 'margin-left': 'auto', 'margin-right': 'auto'}  # Para centrar el segundo logo

logos_container = html.Div([
    html.Div(logo1, style=logo1_style),
    html.Div(logo2, style=logo2_style)
], style={
    'display': 'flex',
    'justify-content': 'space-between',  # Para distribuir los logos horizontalmente
    'max-width': '80%',
    'margin': 'auto'
})



# ------------------------------------Botones-----------------------------------
def Botones(nombre):
    """
    Crea un componente de botones para la interfaz.

    Parámetros:
    - nombre: str, el nombre del botón.

    Retorna:
    - Botones: html.Div, el componente de botones.
    """
    Botones = html.Div(
    [dmc.Button("CSV",
            variant="gradient",
            id=f"btn_csv_{nombre}",
            leftIcon=[DashIconify(icon="fa-solid:file-download", width=15)],
            style={"padding": "10px", "background": "#3498DB", "border": "1px solid black",
                "margin-top": "10px", "margin-bottom": "10px"},
            ),

    dcc.Download(id=f"descarga_dataframe_csv_{nombre}"),

    dmc.Button("Medir",
            variant="gradient",
            id=f"btn_medir_{nombre}",
            leftIcon=[DashIconify(icon="fa-solid:play", width=15)],
            style={"padding": "10px", "background": "#3498DB", "border": "1px solid black",
                "margin-top": "10px", "margin-left": "20px", "margin-bottom": "5px"}
            ),

    dmc.Button("Reiniciar todo",
            id=f"btn_reset_all_{nombre}",
            n_clicks=0,
            leftIcon=[DashIconify(icon="grommet-icons:power-reset", width=20)],
            style={"padding": "10px", "background": "#3498DB", "border": "1px solid black",
                "margin-top": "10px", "margin-left": "20px", "margin-right": "20px", "margin-bottom": "10px"},
            )

    ], style={"margin-left": "10px"}
)

    return Botones




#------------------------------Función para graficar -----------------------------

def graficar(titulo, lista_dataframes, xmedida="U", ymedida="U", xtitle="x", ytitle="y"):
    """
    Genera un gráfico de dispersión con líneas y marcadores a partir de una lista de DataFrames.

    Parámetros:
    - titulo (str): El título del gráfico.
    - lista_dataframes (list): Una lista de DataFrames que contienen los datos a graficar.
    - xmedida (str, opcional): La unidad de medida para el eje x. Por defecto es "U".
    - ymedida (str, opcional): La unidad de medida para el eje y. Por defecto es "U".
    - xtitle (str, opcional): El título del eje x. Por defecto es "x".
    - ytitle (str, opcional): El título del eje y. Por defecto es "y".

    Retorna:
    - fig: El objeto figura de Plotly que representa el gráfico generado.
    """
    
    fig = px.scatter(title=f'{titulo}')
    
    # Iterar sobre la lista de DataFrames y agregar los puntos al gráfico
    for i in range(1, len(lista_dataframes)):
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
# Botones_V_P = Botones("V-P") #Botones para medir Voltaje-Potencia
# Botones_T_V = Botones("T-V") #Botones para medir Temperatura-Voltaje







#-------------------------------Listas------------------------------------
list_df_Voltage_Current = [pd.DataFrame()] #Lista de DataFrames Voltage-Current
list_df_Temperature_Voltage = [pd.DataFrame()] #Lista de DataFrames Temperature-Voltage
lista_VOC = [html.H5("Medidas: "),html.Hr()]
lista_df_Voltage_Power= [pd.DataFrame()] #Lista de DataFrames Voltage-Power
G1 = pd.DataFrame()
IP_list = ["192.168.0.100"]
chanel_selection_V_C = [15]
chanel_selection_temperature = [15]
list_sensor_V_C = [False]
list_sensor_temperature = [False]
list_fuente = [False]




#------------------Callback Ckeck_list de cuadro de seleccion temperatura--------------------

def checklist_sensor(nombre, name_label):
    """
    Crea un componente de lista de verificación (checklist) para un sensor.

    Parámetros:
    - nombre: El nombre del sensor.
    - name_label: La etiqueta del nombre del sensor.

    Retorna:
    - El componente de lista de verificación (checklist) para el sensor.
    """
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
checklist_temperature = checklist_sensor("temperature","Temperatura")

NO_cheklist1 = html.Div(id="NO_checklist1")
NO_cheklist2 = html.Div(id="NO_checklist2")
NO_cheklist3 = html.Div(id="NO_checklist3")



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
    Input("checklist_temperature", "value"),
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


NO_dropnow1 = html.Div(id="output_NO_dropnow1")
NO_dropnow2 = html.Div(id="output_NO_dropnow2")

def dropdown_sensor(nombre):
    """
    Crea un componente de interfaz de usuario que muestra un dropdown con opciones de sensores.

    Parámetros:
    nombre (str): El nombre del dropdown.

    Retorna:
    dash_html_components.Div: El componente de dropdown_sensor.
    """
    opciones_dropdown = [{'label': f'Canal {i}', 'value': i} for i in range(1, 21)]
    dropdown_sensor = html.Div([
        dcc.Dropdown(
            id=f'mi-dropdown_{nombre}',
            options=opciones_dropdown,
            multi=True,
            value=[],
            style={'width': '250px'},
            disabled=True
            
        )   
    ])
    return dropdown_sensor

dropdown_V_C = dropdown_sensor("V_C")
dropdown_temperature= dropdown_sensor("temperature")

@app.callback(
    Output('output_NO_dropnow1', 'children', allow_duplicate=True),
    Output('output_NO_dropnow2', 'children', allow_duplicate=True),
    [Input('mi-dropdown_V_C', 'value'),
    Input('mi-dropdown_temperature', 'value')],
    prevent_initial_call=True
)
def actualizar_dropdown(value1, value2):
    """
    Actualiza los dropdowns de salida en la interfaz gráfica.

    Parámetros:
    - value1: Valor seleccionado en el dropdown 'mi-dropdown_V_C'.
    - value2: Valor seleccionado en el dropdown 'mi-dropdown_temperature'.

    Retorna:
    - Una cadena vacía para cada uno de los dos dropdowns de salida.
    """
    if value1 == []:
        chanel_selection_V_C.clear()
        print(chanel_selection_V_C)
    if value2 == []:
        chanel_selection_temperature.clear()
        print(chanel_selection_temperature)
    return "", ""


@callback(
    Output('output_NO_dropnow1', 'children'),
    [Input('mi-dropdown_temperature', 'value')],
    prevent_initial_call=True
)
def callback_selection_chanel_T(value1):
    """
    Esta función es un callback que se ejecuta cuando se selecciona un valor en el dropdown 'mi-dropdown_temperature'.
    Limpia la lista 'chanel_selection_temperature' y agrega el valor seleccionado.
    Imprime la lista 'chanel_selection_temperature'.
    Retorna una cadena vacía.
    """
    chanel_selection_temperature.clear()
    chanel_selection_temperature.append(value1)
    print(chanel_selection_temperature)
    return ''


@callback(
    Output('output_NO_dropnow2', 'children'),
    [Input('mi-dropdown_V_C', 'value')],
    prevent_initial_call=True
)
def callback_selection_chanel_VC(value1):
    """
    Esta función es un callback que se ejecuta cuando se selecciona un valor en el dropdown 'mi-dropdown_V_C'.
    
    Parámetros:
        - value1: El valor seleccionado en el dropdown 'mi-dropdown_V_C'.
    
    Retorna:
        - Una cadena vacía.
    """
    chanel_selection_V_C.clear()
    chanel_selection_V_C.append(value1)
    print(chanel_selection_V_C)
    return ""

@app.callback(
    [Output('mi-dropdown_V_C', 'disabled'),
    Output('mi-dropdown_V_C', 'value'),
    Output('mi-dropdown_temperature', 'disabled'),
    Output('mi-dropdown_temperature', 'value')],
    [Input('checklist_sensor_V_C', 'value'),
    Input('checklist_temperature', 'value')],
    [State('mi-dropdown_V_C', 'options'),
    State('mi-dropdown_temperature', 'options')],
    prevent_initial_call=True
)
def update_dropdown_and_clear_selection(checklist_sensor_V_C, checklist_temperature,
                                        options_sensor_V_C, options_temperature):
    """
    Actualiza los valores y el estado de los dropdowns y limpia la selección en caso necesario.

    Parámetros:
    - checklist_sensor_V_C (list): Lista de valores seleccionados en el checklist del sensor V_C.
    - checklist_temperature (list): Lista de valores seleccionados en el checklist de temperatura.
    - options_sensor_V_C (list): Lista de opciones disponibles para el dropdown del sensor V_C.
    - options_temperature (list): Lista de opciones disponibles para el dropdown de temperatura.

    Retorna:
    - dropdown_disabled_sensor_V_C (bool): Estado de habilitación/deshabilitación del dropdown del sensor V_C.
    - dropdown_value_sensor_V_C (any): Valor seleccionado en el dropdown del sensor V_C.
    - dropdown_disabled_temperature (bool): Estado de habilitación/deshabilitación del dropdown de temperatura.
    - dropdown_value_temperature (any): Valor seleccionado en el dropdown de temperatura.
    """
    
    dropdown_value_sensor_V_C = None
    dropdown_value_temperature = None

    if checklist_sensor_V_C and checklist_temperature:
        dropdown_disabled_sensor_V_C = False
        dropdown_disabled_temperature = False
        
    elif not checklist_sensor_V_C and not checklist_temperature:
        dropdown_disabled_sensor_V_C = True
        dropdown_disabled_temperature = True
        chanel_selection_temperature.clear()
        chanel_selection_V_C.clear()
        print(chanel_selection_V_C)
        
    elif checklist_sensor_V_C and not checklist_temperature:
        dropdown_disabled_sensor_V_C = False
        dropdown_disabled_temperature = True
        dropdown_value_temperature = None
        chanel_selection_temperature.clear()  
        # Limpiar la selección del dropdown de temperatura
    elif not checklist_sensor_V_C and checklist_temperature:
        dropdown_disabled_sensor_V_C = True
        dropdown_disabled_temperature = False
        dropdown_value_sensor_V_C = None
        chanel_selection_V_C.clear()

    return dropdown_disabled_sensor_V_C, dropdown_value_sensor_V_C, dropdown_disabled_temperature, dropdown_value_temperature




    #-----------------------------Alerta de resultado-----------------------------

alerta_medidas = dbc.Alert(lista_VOC,
                id="resultado-alert",
                color="success",
                is_open=True,
                style={"height": "38vh", "overflow": "auto",},
                # Establecer en True para que quede permanentemente visible
                )



alerta_cargando = dbc.Alert(
    html.Div([
        dbc.Spinner(color="success", type="grow"),
        dbc.Spinner(color="success", type="grow"),
        dbc.Spinner(color="success", type="grow"),
        dbc.Spinner(color="success", type="grow"),
        dbc.Spinner(color="success", type="grow"),
        dbc.Spinner(color="success", type="grow"),
        dbc.Spinner(color="success", type="grow"),
    ]),
    id="cargando-alerta",
    dismissable=True,
    color="ligth",
    is_open=False,
    style={
        "max-width": "100%",  # Establecer un ancho máximo relativo al 95% del tamaño de la ventana
        "font-size": "24px",
        "display": "flex",
        "justify-content": "center",
        "align-items": "center",
        "overflow": "auto"  # Agregar overflow para permitir el desplazamiento si el contenido es demasiado grande
    },
)




#-----------------------------Callback de  alerta de medicion y descativar botones----------------------------
@app.callback(
    [Output("cargando-alerta", "is_open",allow_duplicate=True),
    Output("btn_medir_V-C", "disabled",allow_duplicate=True),
    Output("btn_csv_V-C", "disabled",allow_duplicate=True),
    Output("btn_reset_all_V-C", "disabled",allow_duplicate=True)],
    [Input("btn_medir_V-C", "n_clicks")],
    prevent_initial_call=True,
)
def activar_alerta(n_clicks):
    """
    Activa o desactiva la alerta y los botones relacionados según el número de clics en el botón "btn_medir_V-C".

    Parámetros:
    - n_clicks: int, número de clics en el botón "btn_medir_V-C".

    Retorna:
    - is_open: bool, indica si la alerta está abierta o cerrada.
    - disabled: bool, indica si los botones "btn_medir_V-C", "btn_csv_V-C" y "btn_reset_all_V-C" están deshabilitados o no.
    """
    if n_clicks:
        return True, True, True, True
    # Por defecto, mantener la alerta desactivada
    return False, False, False, False

#-----------------------------Callback de activacion de boton de medición cuando la alerta esté apagada ----------------------------

@app.callback(
    Output("btn_medir_V-C", "disabled",allow_duplicate=True),
    Output("btn_csv_V-C", "disabled",allow_duplicate=True),
    Output("btn_reset_all_V-C", "disabled",allow_duplicate=True),
    Input("cargando-alerta", "is_open"),
    prevent_initial_call=True,
)
def habilitar_boton(is_open):
    """
    Habilita o deshabilita los botones "btn_medir_V-C", "btn_csv_V-C" y "btn_reset_all_V-C" 
    según el estado de la alerta "cargando-alerta".

    Parámetros:
    - is_open (bool): Indica si la alerta está abierta o cerrada.

    Retorna:
    - is_open (bool): Estado de la alerta "cargando-alerta".
    """
    return is_open, is_open, is_open


#-----------------------------Callback de medición V-C ----------------------------



@app.callback(
    [Output("grafico", "figure"),
    Output("grafico2", "figure"),
    Output("grafico3", "figure"),
    Output("resultado-alert", "children"),
    Output("cargando-alerta", "is_open")],
    Input("btn_medir_V-C", "n_clicks"),
    prevent_initial_call=True,
)
def medir_callback(n_clicks):
    """
    Esta función es el callback para el botón "btn_medir_V-C". 
    Se encarga de realizar las mediciones y generar los gráficos correspondientes.
    
    Parámetros:
    - n_clicks (int): El número de veces que se ha hecho clic en el botón.
    
    Retorna:
    - fig (objeto Figure): El gráfico de la curva V-I TEC-12706.
    - fig2 (objeto Figure): El gráfico de voltaje vs temperatura.
    - fig3 (objeto Figure): El gráfico de voltaje vs potencia.
    - lista_VOC (lista de str): La lista de valores de VOC.
    - False (bool): Indica si la alerta de carga está abierta o no.
    """
    ############################################################
    temperature_selection = list_sensor_temperature[0] 
    sensor_V_C_selection = list_sensor_V_C[0]
    fuente_selection = list_fuente[0]
    ############################################################
    chanel_selec_temperature =chanel_selection_temperature[0]
    print(chanel_selection_V_C,"a")
    chanel_selec_V_C = chanel_selection_V_C[0]
    
    valores = Resultados(IP=IP_list[-1],Temperature =temperature_selection,
                        Fuente=fuente_selection ,Sensor_V_C=sensor_V_C_selection,
                        chanel_temperature=chanel_selec_temperature)
    
    if  len(valores) == 0:
        return dash.no_update, dash.no_update, dash.no_update, lista_VOC,False
    elif valores[-1] == "F":
        
        df_voltage_current,measurement_voltage_Voc,df_voltage_power,elemento = valores
        
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
        
        print(type(measurement_voltage_Voc))
        print(measurement_voltage_Voc)
        lista_VOC.append(f"VOC: {measurement_voltage_Voc} [V]")
        lista_VOC.append(html.Br())
        G1 = pd.concat(list_df_Voltage_Current,axis=1)
        
        
        return  fig, fig2, fig3, lista_VOC, False
    
    elif valores[-1] == "F_T":
        df_voltage_current,measurement_voltage_Voc,df_voltage_power,df_temperature_voltage,elemento = valores
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

        
        Ag_temp_proom = list_df_Temperature_Voltage[-1]
        Prom_Temp = Ag_temp_proom[Ag_temp_proom.columns[1]].astype(float).mean()
        lista_VOC.append(html.Small(f"VOC: {measurement_voltage_Voc} [V] T: {round(Prom_Temp,3)} [ºC]"))
        lista_VOC.append(html.Br())
        G1 = pd.concat(list_df_Voltage_Current,axis=1)

    
        return  fig, fig2, fig3, lista_VOC, False
    

        

    
    
    


#-----------------------------Callback de Descarga CSV----------------------------


# Callback para descargar como CSV
@app.callback(
    Output("descarga_dataframe_csv_V-C", "data"),
    Input("btn_csv_V-C", "n_clicks"),
    prevent_initial_call=True,
    
)
def csv_callback(btn_csv):
    """
    Esta función es el callback para generar y descargar un archivo CSV con los datos del dataframe.
    
    Parámetros:
        - btn_csv (int): El número de veces que se ha hecho clic en el botón "btn_csv_V-C".
        
    Retorna:
        - data (dict): Un CSV que contiene los datos del archivo a descargar.
    """
    df = pd.concat(list_df_Voltage_Current, axis=1)
    
    if not btn_csv:
        raise Dash.exceptions.PreventUpdate

    return dcc.send_data_frame(df.to_csv, "medicion.csv")



# ------------------------Entrada de texto y salida de texto IP -------------------------


default_ip = "192.168.0.100"

# Crea el diseño de la aplicación
text_input= html.Div(
    [   
        dbc.Input(id="IP", placeholder=default_ip, type="text", value=default_ip),
        html.Br(),   
    ], style={'margin-down': "0px"}
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
    """
    Esta función se utiliza como un callback para el botón "btn_reset_all_V-C".
    Restablece los valores globales y las figuras utilizadas en la interfaz gráfica.

    Parámetros:
    - n_clicks: int - El número de veces que se ha hecho clic en el botón.

    Retorna:
    - fig: plotly.graph_objs._figure.Figure - La figura para el gráfico "grafico".
    - fig2: plotly.graph_objs._figure.Figure - La figura para el gráfico "grafico2".
    - fig3: plotly.graph_objs._figure.Figure - La figura para el gráfico "grafico3".
    - lista_VOC: list - La lista de elementos HTML para el componente "resultado-alert".
    """
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




tab1 = dbc.Tab([dcc.Graph(id="grafico", figure=px.line(template="bootstrap")),alerta_cargando], label="Voltaje-Corriente")
tab3 = dbc.Tab([dcc.Graph(id="grafico2",figure=px.line(template="bootstrap"))], label="Voltaje-Temperatura")
tab2 = dbc.Tab([dcc.Graph(id="grafico3",figure=px.line(template="bootstrap"))], label="Voltaje-Potencia")
# tab4 = dbc.Tab([cuadricula], label="Table", className="p-4")
tabs = dbc.Card(dbc.Tabs([tab1, tab2, tab3]))

#---------------------------------------Titulo Mediciones---------------------------------------
header = dbc.Alert(
    [html.Div([html.H1("Peltier", style={"max-width": "100%"})], style={"text-align": "center", "margin": "auto"}),],
    id="Titulo",
    color="success",
    is_open=True,
    style={"height": "10vh", "overflow": "hidden", "display": "flex", "align-items": "center"},
)





# ------------------------Diseño de la aplicación Dash-------------------------
app.layout = dbc.Container([
    # Primera fila
    dbc.Row([
        dbc.Col([logos_container]),  # 30% de ancho
        dbc.Col([header]),  # 30% de ancho
    ], style={'padding': '10px'}),


    
    # Segunda fila
    dbc.Row([
        # Primer columna
        dbc.Col([
            dbc.Row([controls_fuente, NO_output], style={"padding": "0px 5px 10px 10px"}),
            dbc.Row([alerta_medidas], style={"padding": "5px 5px 0px 10px"}),  # Ajuste de relleno aquí
            # dbc.Row([
            #     # Contenido de la fila
            # ], style={"padding": "0px 5px 5px 5px"}),
        ]),
        
        # Segunda columna
        dbc.Col([
            dbc.Row([tabs]),
            dbc.Row([Botones_V_C]),
        ], 
        width={"size": 12, "order": 2}, 
        xs=12, sm=12, md=12, lg=8, xl=8, id='columna_tabs_botones',
        className="align-items-start")
    ]),
    
    # Tercera fila
    dbc.Row([
        # Columna 1
        dbc.Col([
            dbc.Row([Alineacion_ckecklist_V_C]),
            dbc.Row([dropdown_V_C, NO_dropnow1]),
        ]),
        
        # Columna 2
        dbc.Col([
            dbc.Row([Alineacion_ckecklist_temperature]),
            dbc.Row([dropdown_temperature, NO_dropnow2]),
        ]),
        
        # Columna 3 (sin contenido)
        dbc.Col([]),
        
        # Columna 4
        dbc.Col([theme_controls], style={"padding": "20px", "display": "flex", "justify-content": "end"}),
    ], style={"padding": "0px 0px 5px 5px"}, className="mx-auto"),  # Centra el contenido horizontalmente
], fluid=True, className="dbc dbc-ag-grid")






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
