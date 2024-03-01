
import numpy as np
import pandas as pd
import pyvisa as visa 

def Resultados(IP_fuente="192.168.0.100",
                    voltaje_inicial=0,
                    num_puntos=6,
                    Temperature = False,
                    chanel=8):
    
    
    current = []
    voltage = []
    temperature = []
    
    if Temperature == False :
        from prueba import voltage_current,Barrido_IV
        inst,measurement_voltage_Voc = voltage_current()
    elif Temperature == True:
        from prueba import voltage_current,Barrido_IV
        from LTC2984 import sensor_measurement
        inst,measurement_voltage_Voc = voltage_current()
        ADC = sensor_measurement(num_puntos,chanel)
    

    if measurement_voltage_Voc <= 2 and Temperature == True:

        inst.write("smua.source.output = smua.OUTPUT_ON")
        print('---------------------------Iniciando medidas----------------------------------------')

        v = np.linspace(voltaje_inicial,measurement_voltage_Voc,num_puntos)
        
        for element in range(len(v)):
            new_v, new_i = Barrido_IV(inst, v[element], measurement_voltage_Voc)
            voltage.append(new_v)
            current.append(new_i)
            
            
            #---------------Temperatura-------------
            ADC.StartConversion(chanel) # Canal se sensor
            while(ADC.HasStartupFinished()==False):
                pass
            [fault,temp]=ADC.ReadResults(chanel)
            temperature.append(temp) 
            print(f"Channel {chanel}: "+str(temp)+" fault "+str(fault))
            #---------------------------------------
        
        inst.write('smua.source.output = smua.OUTPUT_OFF') # Apagar salida de la fuente
        inst.close()
        potencia = np.array(voltage)*np.array(current)
        return (pd.DataFrame({'Voltage': voltage, 'Current': current}),
                measurement_voltage_Voc,
                pd.DataFrame({'Voltage': voltage,'Power': potencia}),
                pd.DataFrame({'Voltage': voltage,'Temperature': temperature }),)
    
    
    elif measurement_voltage_Voc <= 2 and Temperature == False:
        inst.write("smua.source.output = smua.OUTPUT_ON")
        print('---------------------------Iniciando medidas----------------------------------------')

        v = np.linspace(voltaje_inicial,measurement_voltage_Voc,num_puntos)
        
        for element in v:
            new_v, new_i = Barrido_IV(inst, element, measurement_voltage_Voc)
            voltage.append(new_v)
            current.append(new_i)
        
        inst.write('smua.source.output = smua.OUTPUT_OFF') # Apagar salida de la fuente
        inst.close()
        potencia = np.array(voltage)*np.array(current)
        return (pd.DataFrame({'Voltage': voltage, 'Current': current}),
                measurement_voltage_Voc,
                pd.DataFrame({'Voltage': voltage,'Power': potencia}))
    
