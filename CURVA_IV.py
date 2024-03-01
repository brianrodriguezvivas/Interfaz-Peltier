##################################  Importar Librerias   ######################################
import os
import time as tm
import numpy as np
import pandas as pd
import pyvisa as visa


######################  Función para realizar conexión con la fuente  ########################

def Conectar_Fuente(IP_fuente):
    inst = ""
    try:
        resourceManager = visa.ResourceManager() 
        dev = 'TCPIP::' + IP_fuente + '::INSTR'
        inst = resourceManager.open_resource(dev)
        print('Open Successful!')
        print('IDN:' + str(inst.query('*IDN?')))     
    except Exception as e:
        print('[!] Exception:' +str(e))
    
    return inst

IP_fuente = "192.168.0.100" # *********Puede cambiar en cualquier momento ********************
inst = Conectar_Fuente(IP_fuente)

#############################  Sección para realizar obtener Voc  ############################

# Poner la fuente a mostrar medida de voltaje en la pantalla de la fuente
inst.write('display.smua.measure.func = 1')
# Poner la fuente en modo corriente
inst.write('smua.source.func = 0')
# Poner un valor de cero amperios a la salida de la fuente 
inst.write("smua.source.leveli = " + str(0))
# Limitar voltaje
lim_v = 2
inst.write('smua.source.limitv =' + str(lim_v)) 
# Habilitamos la salida de la fuente
inst.write("smua.source.output = smua.OUTPUT_ON")
# delta de tiempo entre la activacion de salida de la fuente y toma de medida
tm.sleep(5)
# Obtener medida de Voc
inst.write('print(smua.measure.v())')
# Valor de Voce
measurement_voltage_Voc = float(inst.read())
print('Voc medido: ', measurement_voltage_Voc)
inst.write('smua.source.output = smua.OUTPUT_OFF') # Apagar salida de la fuente

################################# Poner la fuente en modo voltaje  #########################

#Poner la fuente en modo voltaje
inst.write('smua.source.func = 1') 
# Poner un valor de cero voltios a la salida de la fuente 
inst.write("smua.source.levelv = " + str(0))    
#Poner la fuente a mostrar valor de voltaje en la pantalla de la fuente
inst.write('display.smua.measure.func = 1')
#Limitar la corriente
lim_I = 1
inst.write('smua.source.limiti =' + str(lim_I)) 

############ Hacemos un barrido desde cero hasta Voc medido para realizar curva IV  ##########

if measurement_voltage_Voc <= 2:
    # Habilitamos la salida de la fuente
    inst.write("smua.source.output = smua.OUTPUT_ON")

    v = np.linspace(0,measurement_voltage_Voc,6) 
    current = []
    voltage = []
    for element in v:
        inst.write("smua.source.levelv = " + str(element))
        tm.sleep(4)
        
        inst.write('print(smua.measure.v())')
        measurement_voltage = float(inst.read())
        voltage.append(measurement_voltage)

        inst.write('print(smua.measure.i())')
        measurement_current = float(inst.read())
        current.append(measurement_current)
        print('[Voltage, Current] = ', [measurement_voltage, measurement_current])
        print('-----------------------------------------------------------------')
    inst.write('smua.source.output = smua.OUTPUT_OFF') # Apagar salida de la fuente
    inst.close()
##################################### Grafica curva iv #######################################

