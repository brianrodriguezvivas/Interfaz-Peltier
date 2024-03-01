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
    className="hstack gap-3 mt-2"
)


Temas = ["bootstrap"]



#----------------------------------- Logos-----------------------------------

logo1 = html.Div(
    html.Img(src='assets/logo.png', height='60px', width='auto')
)
logo2 = html.Div(
    html.Img(src='assets/udea-png.png', height='60px', width='auto')
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




#-------------------------------------------------------------------

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


#-------------------------------Barra de progresso--------------------------------

barra_progreso = dbc.Progress(id="progress-bar", value=0, striped=True, animated=True)


#-------------------------------Listas------------------------------------
list_df_Voltage_Current = [pd.DataFrame()] #Lista de DataFrames Voltage-Current
list_df_Temperature_Voltage = [pd.DataFrame()] #Lista de DataFrames Temperature-Voltage
lista_VOC = [html.H3("Medidas: "), html.Hr()]
lista_df_Voltage_Power= [pd.DataFrame()] #Lista de DataFrames Voltage-Power
G1 = pd.DataFrame()



#------------------Callback Ckeck_list de cuadro de seleccion temperatura--------------------

check_list = dcc.Checklist(
    [
        {
            "label": html.Div(['Temperatura'], style={'color': 'Black', 'font-size': 20, 'padding': '0'}), 
            "value": True,
        },                
    ],
    labelStyle={"display": "flex", "align-items": "center", "font-size": 20},
    inputStyle={ 
        "width": "20px",
        "height": "20px",  # Ajusta el tamaño según prefieras
    },
    id="checklist",  
)


NO = html.Div(id="output11")

temperature_selection_list = [False]

# Crear un callback para actualizar el contenido del Div con el valor seleccionado
@app.callback(
    Output("output11", "children"),
    [Input("checklist", "value")],
    prrevet_initial_call=True
)
def callback_selection_temperatute(selected_value):
    if selected_value:
        temperature_selection_list.clear()
        temperature_selection_list.append(True)
        return ""
    else:
        temperature_selection_list.clear()
        temperature_selection_list.append(False)
        return ""

#------------------------------Lista_despegable----------------------------------
chanel_selection_list = [15]

opciones_dropdown = [{'label': f'Canal {i}', 'value': i} for i in range(1, 21)]

dropnow=html.Div([
            dcc.Dropdown(
            id='mi-dropdown',
            options=opciones_dropdown,
            value=15 ,
            # style={'width': '50%'},
            ),
        ]
)

NO_dropnow = html.Div(id="output_NO_dropnow")
@callback(
    Output('output_NO_dropnow', 'children'),
    Input('mi-dropdown', 'value'),
    prevent_initial_call=True
)
def callback_selection_chanel(value):
    chanel_selection_list.clear()
    chanel_selection_list.append(int(value))
    return ''




#-----------------------------Callback de medición V-C----------------------------



@app.callback(
    [Output("grafico", "figure"),
    Output("grafico2", "figure"),
    Output("grafico3", "figure"),
    Output("resultado-alert", "children"),
    # Output("grid","rowData"),
    Output("progress-bar", "value"),
    Output("progress-bar", "label"),
    ],
    Input("btn_medir_V-C", "n_clicks"),
    
    prevent_initial_call=True,
)




def medir_callback(n_clicks):

    
    temperature_selection = temperature_selection_list[0]
    chanel_selection = chanel_selection_list[0]
    valores = Resultados(Temperature =temperature_selection , chanel = chanel_selection) # Selecion de True o False para medir temperatura
    if len(valores) == 3:
        df_voltage_current,measurement_voltage_Voc,df_voltage_power = valores
        df_voltage_current = df_voltage_current.rename(columns={df_voltage_current.columns[0]: f'{df_voltage_current.columns[0]}_{n_clicks}',
                                df_voltage_current.columns[1]: f'{df_voltage_current.columns[1]}_{n_clicks}'})
        
        list_df_Voltage_Current.append(df_voltage_current)
        lista_df_Voltage_Power.append(df_voltage_power)
        
        fig = graficar("Curva V_I TEC-12706",list_df_Voltage_Current,xmedida="[V]",ymedida="[A]", xtitle="Voltage", ytitle="Current")
        fig3 = graficar("Voltage vs Power",lista_df_Voltage_Power,xmedida="[V]",ymedida="[W]", xtitle="Voltage", ytitle="Power")
        fig2 = dash.no_update
        
        
        lista_VOC.append(html.P(f"VOC: {measurement_voltage_Voc} [V]"))
        lista_VOC.append(html.Hr())
        G1 = pd.concat(list_df_Voltage_Current,axis=1)
        
        
        return  fig, fig2, fig3, lista_VOC ,100,f"{100} %"
    
    if len(valores) == 4:
        df_voltage_current,measurement_voltage_Voc,df_voltage_power,df_temperature_voltage = valores
        df_temperature_voltage = df_temperature_voltage.rename(columns={df_temperature_voltage.columns[0]: f'{df_temperature_voltage.columns[0]}_{n_clicks}',
                                df_temperature_voltage.columns[1]: f'{df_temperature_voltage.columns[1]}_{n_clicks}'})
        
        
        df_voltage_current = df_voltage_current.rename(columns={df_voltage_current.columns[0]: f'{df_voltage_current.columns[0]}_{n_clicks}',
                            df_voltage_current.columns[1]: f'{df_voltage_current.columns[1]}_{n_clicks}'})
        
        list_df_Voltage_Current.append(df_voltage_current)
        list_df_Temperature_Voltage.append(df_temperature_voltage)
        lista_df_Voltage_Power.append(df_voltage_power)
        
        fig = graficar("Curva V_I TEC-12706",list_df_Voltage_Current,xmedida="[V]",ymedida="[A]")
        fig2 = graficar("Voltaje vs Temperatura",list_df_Temperature_Voltage,xmedida="[V]",ymedida="[°C]")
        fig3 = graficar("Voltaje vs Potencia",lista_df_Voltage_Power,xmedida="[V]",ymedida="[W]")
        
        
        lista_VOC.append(html.P(f"VOC: {measurement_voltage_Voc} [V] T_prom: {np.mean(np.array(list_df_Temperature_Voltage))} [W]"))
        lista_VOC.append(html.Hr())
        G1 = pd.concat(list_df_Voltage_Current,axis=1)
        
        return  fig, fig2, fig3, lista_VOC ,100,f"{100} %"
        

    
    
    
    

    # Devolver tanto los datos del DataFrame como el gráfico
    



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
        dbc.Input(id="input", placeholder="192.168.0.100", type="text"),
        html.Br(),
        
    ]
)

# Controles generales incluyendo desplegable, lista de verificación y control deslizante
controls = dbc.Card(
    [text_input],
    body=True,
)


#-----------------------------Alerta de resultado-----------------------------

g1 = dbc.Alert(lista_VOC,
    id="resultado-alert",
    color="success",
    is_open=True,
    style={"height": "50vh"},
    # Establecer en True para que quede permanentemente visible
)


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
    lista_VOC.append(html.H3("Medidas: "))  # Limpiar lista de VOC
    lista_VOC.append( html.Hr())
    
    fig = px.scatter(template="bootstrap")
    fig2 = px.scatter(template="bootstrap")
    fig3 = px.scatter(template="bootstrap")
    
    list_df_Voltage_Current = [pd.DataFrame()]
    list_df_Temperature_Voltage = [pd.DataFrame()]
    lista_df_Voltage_Power = [pd.DataFrame()]
    
    return fig, fig2, fig3, lista_VOC   
# ------------------------Pestañas con gráficos y cuadrícula AG-------------------------------
Alineacion_ckecklist = dbc.Container([
    html.Div([
        check_list,
        NO,
    ], style={'display': 'flex','align-items': 'center'})
], className="mt-4")

tab1 = dbc.Tab([barra_progreso,dcc.Graph(id="grafico", figure=px.line(template="bootstrap")),Botones_V_C], label="Voltaje-Corriente")
tab3 = dbc.Tab([dcc.Graph(id="grafico2",figure=px.line(template="bootstrap")),Botones_V_P], label="Voltaje-Temperatura")
tab2 = dbc.Tab([dcc.Graph(id="grafico3",figure=px.line(template="bootstrap")),Botones_T_V], label="Voltaje-Potencia")
# tab4 = dbc.Tab([cuadricula], label="Table", className="p-4")
tabs = dbc.Card(dbc.Tabs([tab1, tab2, tab3]))

#---------------------------------------Titulo Mediciones---------------------------------------

header = dbc.Alert(
        [html.Div([html.H1("Tomas Peltier")], style={"text-align": "center"}),],
        id="resultado",
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
            dbc.Row([controls]),
            dbc.Row([g1], style={'padding': '10px'}),
            dbc.Row([
                dbc.Col([theme_controls]),
                dbc.Col([
                    dbc.Row([Alineacion_ckecklist]),
                    dbc.Row([dropnow, NO_dropnow])  # Closing bracket added here
                ]),
            ]),
        ]),
        dbc.Col([
            dbc.Row([dbc.Col([tabs], width=12)], id='fila_tabs'),
        ], width=8, id='columna_tabs_botones'),
    ]),
],
fluid=True,
className="dbc dbc-ag-grid",
)






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