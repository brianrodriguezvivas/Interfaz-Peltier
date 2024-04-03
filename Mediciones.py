
import numpy as np
import pandas as pd
import pyvisa as visa 

def Resultados(IP="192.168.0.100",
                    voltaje_inicial=0,
                    num_puntos=20,
                    Temperature = False,
                    Fuente = False,
                    Sensor_V_C = False,
                    chanel_temperature=[15]):
    
    
    current = []
    voltage = []
    temperature = []


    #Aqui va la fuente encendida 
    if Fuente == True and Temperature == True and Sensor_V_C == False: 
        from prueba import voltage_current,Barrido_IV
        from LTC2984 import sensor_measurement
        inst,measurement_voltage_Voc = voltage_current(IP)
        
        if measurement_voltage_Voc <= 2:
            
            ADC = sensor_measurement()


            inst.write("smua.source.output = smua.OUTPUT_ON")
            print('---------------------------Iniciando medidas----------------------------------------')

            v = np.linspace(voltaje_inicial,measurement_voltage_Voc,num_puntos)
            Temperature_prom = []
#---------------------------------------Temperatura inicial ----------------------------------------           
            for chanel in chanel_temperature:

                ADC.StartConversion(chanel)

                while(ADC.HasStartupFinished()==False):
                    pass
                [fault,temp]=ADC.ReadResults(chanel)
                Temperature_prom.append(temp) 
                print(f"Channel {chanel}: "+str(temp)+" fault "+str(fault))
#--------------------------------------------------------------------------------------------------

            for element in range(len(v)):
                new_v, new_i = Barrido_IV(inst, v[element], measurement_voltage_Voc)
                voltage.append(new_v)
                current.append(new_i)
                
#---------------------------------------Temperatura final ------------------------------------------           
            for chanel in chanel_temperature:

                ADC.StartConversion(chanel)

                while(ADC.HasStartupFinished()==False):
                    pass
                [fault,temp]=ADC.ReadResults(chanel)
                Temperature_prom.append(temp) 
                print(f"Channel {chanel}: "+str(temp)+" fault "+str(fault))
#-----------------------------------Temperatura Promedio--------------------------------------------


                
            temperature.append(np.mean(np.array(Temperature_prom)))

#---------------------------------------------------------------------------------------------------
                
            
            
            inst.write('smua.source.output = smua.OUTPUT_OFF') # Apagar salida de la fuente
            inst.close()
            potencia = np.array(voltage)*np.array(current)
            return (pd.DataFrame({'Voltage': voltage, 'Current': current}),
                    measurement_voltage_Voc,
                    pd.DataFrame({'Voltage': voltage,'Power': potencia}),
                    pd.DataFrame({'Voltage': voltage,'Temperature': temperature }),"F_T")
    
    elif Fuente == True and Temperature == False and Sensor_V_C == False: 
        
        from prueba import voltage_current,Barrido_IV
        inst,measurement_voltage_Voc = voltage_current(IP)
        if measurement_voltage_Voc <= 2:
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
                    pd.DataFrame({'Voltage': voltage,'Power': potencia}),"F")
        
    else:
        return ''
    # elif Fuente == True and Temperature == False and Sensor_V_C == False: 
        