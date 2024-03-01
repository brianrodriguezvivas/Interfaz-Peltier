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
dm = [pd.DataFrame()] #Lista de DataFrames
lista_VOC = [html.H5("VOC medido: "), html.Hr()]
G1 = pd.DataFrame()
#-------------------------------------------------------------------

def graficar(titulo,lista_dataframes,xmedida = "U",ymedida = "U"):
    
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

    fig.update_xaxes(title_text=f'{df.columns[0][:-2]} ({xmedida})', 
                    showgrid=True,
                    gridwidth=1,
                    gridcolor='lightgray'
    )
    
    fig.update_yaxes(title_text=f'{df.columns[1][:-2]} ({ymedida})',
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




#-----------------------------Callback de medición V-C----------------------------



@app.callback(
    [Output("grafico", "figure"),
    Output("resultado-alert", "children"),
    # Output("grid","rowData"),
    Output("progress-bar", "value"),
    Output("progress-bar", "label"),
    ],
    Input("btn_medir_V-C", "n_clicks"),
    
    prevent_initial_call=True,
)

#-----------------------------Función de medición V-C----------------------------

def medir_callback(n_clicks):

    
    
    
    new_df,measurement_voltage_Voc = Resultados(Temperature=True)
    new_df = new_df.rename(columns={new_df.columns[0]: f'{new_df.columns[0]}_{n_clicks}',
                                    new_df.columns[1]: f'{new_df.columns[1]}_{n_clicks}'})
    
    dm.append(new_df)
    
    fig = graficar("Curva I-V TEC-12706",dm,xmedida=["V"],ymeida=["A"])
        
    lista_VOC.append(html.P(f"Voc medido: {measurement_voltage_Voc} V"))
    lista_VOC.append(html.Hr())
    
    
    
    G1 = pd.concat(dm,axis=1)

    # Devolver tanto los datos del DataFrame como el gráfico
    return  fig, lista_VOC ,100,f"{100} %"




#-----------------------------Callback de Reinicio----------------------------

@app.callback(
    [Output("grafico", "figure",allow_duplicate=True),
    Output("resultado-alert", "children",allow_duplicate=True)],
    Input("btn_reset_all_V-C", "n_clicks"),
    prevent_initial_call=True
)

def reset(n_clicks):
    global dm 
    lista_VOC = [html.H5("VOC medido: "), html.Hr()]  # Limpiar lista de VOC
    fig = px.scatter(template="bootstrap")
    dm = [pd.DataFrame()]
    return fig, lista_VOC


#-----------------------------Callback de Descarga CSV----------------------------


# Callback para descargar como CSV
@app.callback(
    Output("descarga_dataframe_csv_V-C", "data"),
    Input("btn_csv_V-C", "n_clicks"),
    prevent_initial_call=True,
    
)
def csv_callback(btn_csv):
    df = pd.concat(dm, axis=1)
    
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



    
    
    
    
# ------------------------Pestañas con gráficos y cuadrícula AG-------------------------------

tab1 = dbc.Tab([barra_progreso,dcc.Graph(id="grafico", figure=px.line(template="bootstrap")),Botones_V_C], label="Voltage-Current")
tab2 = dbc.Tab([dcc.Graph(figure=px.line(template="bootstrap")),Botones_V_P], label="Voltage-Power")
tab3 = dbc.Tab([dcc.Graph(figure=px.line(template="bootstrap")),Botones_T_V], label="Temperature-Voltage")
# tab4 = dbc.Tab([cuadricula], label="Table", className="p-4")
tabs = dbc.Card(dbc.Tabs([tab1, tab2, tab3]))

#---------------------------------------Titulo Mediciones---------------------------------------

header = dbc.Alert(
        [html.Div([html.H1("Medición")], style={"text-align": "center"}),],
        id="resultado",
        color="success",
        is_open=True,
        style={"height": "10vh"},
        )








# ------------------------Diseño de la aplicación Dash-------------------------
app.layout = dbc.Container([   
        dbc.Row([
                dbc.Col([logo1],width=1),
                dbc.Col([logo2],),
                dbc.Col([header]),
        ],style={'padding': '10px'}),
        dbc.Row([
            
                dbc.Col([
                        dbc.Row([
                            controls,
                        ]),
                        dbc.Row([
                            g1,
                        ],style={'padding': '10px'}),
                        dbc.Row([
                            theme_controls,
                        ]),
                    ], width=4, id='columna_controles'),
                
                dbc.Col([
                        # Fila para los tabs
                        dbc.Row([
                            dbc.Col([tabs],
                                        width=12),
                        ], id='fila_tabs'),
                        # Fila para los botones
                        # dbc.Row([
                            
                        #     dbc.Col([Botones_V_C],
                        #                 width=12),
                        # ], id='fila_botones'),
                        
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