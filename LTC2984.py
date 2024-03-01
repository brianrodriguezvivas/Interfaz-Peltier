#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  24 13:53:31 2024
Script for reading the LTC2984. LTC2984 is a 
multisensor, high acurracy, temperature measurement 
system. This script is intended for
Raspberry PI usage, using the onboard SPI port.

At the current state, the sensor configuration is 
not supported. It must be done externally by using the
Analog devices demo software: 
https://ltspice.analog.com/quikeval/ins2984.msi

Configuration must be saved in the on-chip EEPROM

@author: juan
"""

from spidev import SpiDev

class LTC2984:
    def __init__(self, spiport=1, spidevice=2,spispeed=1000000):
        #Debug mode: True to activate printing and aditional checks..
        self.debug=False
        
        self.spiport=spiport
        self.spispeed=spispeed
        self.spidevice=spidevice
        
    def DebugPrint(self,string):
        if self.debug==True:
            print(string)
        
    def connect(self):
        #Creates SPI communication object
        self.SPI=SpiDev()
        self.SPI.open(self.spiport,self.spidevice)
        #Configure SPI settings
        self.SPI.mode = 0b00
        self.SPI.max_speed_hz=self.spispeed
        self.SPI.bits_per_word=8  
        #We will use 8 bit words, 
        #16 bit adresses will be software managed.

    def WriteReg(self,address,data):
        """
        Writes a register to the LTC2984.

        Parameters
        ----------
        address :Integer, 2 Byte
            Register address, must be on the range 0x00 to 0x3CF.
            see table 2A on datasheet for register usage.
        data : List
            Data to be written to the register (Bytes).
            List size (number of bytes) must be according Table 2A.

        Returns
        -------
        None.

        """
        #instruction byte for write register.
        instructionreg=0x02 
        #Formats the 16 bit address.
        address_bytes=list(address.to_bytes(2,"big"))
        #Formats the complete spi payload
        payload=[instructionreg]+address_bytes+data
        payload_cp=payload.copy() #Payload is overwrriten by spi.xfer2
        #Write to the SPI port.
        self.SPI.xfer2(payload)
        if self.debug==True:
            print("Write to reg "+hex(address))
            print("sent:")
            print([hex(byte) for byte in payload_cp])
                
            
    def ReadReg(self,address,size):
        """
        Reads a register from the LTC2984.

        Parameters
        ----------
        address : Integer, 2 Byte
            Register address, must be on the range 0x00 to 0x3CF.
            see table 2A on datasheet for register usage.
        size : Integer
            Number of bytes to be read.

        Returns
        -------
        Payload: Received data, excluding the SPI overhead.

        """
        #instruction byte for read register.
        instructionreg=0x03
        #Formats the 16 bit address.
        address_bytes=list(address.to_bytes(2,"big"))
        #Formats the complete spi payload (adding dummy data)
        dummy=0
        dummy_bytes=list(dummy.to_bytes(size, "big"))
        payload=[instructionreg]+address_bytes+dummy_bytes
        payload_cp=payload.copy() #Payload is overwrriten by spi.xfer2
        self.SPI.xfer2(payload)
        if self.debug==True:
            print("Read from reg "+hex(address))
            print("sent:")
            print([hex(byte) for byte in payload_cp])
            print("Rcvd:")
            print([hex(byte) for byte in payload])
        return payload[3:]


    def HasStartupFinished(self):
        """
        Checks if LTC2984 startup has ended,
        by reading the Command status register...
        
        Can be used to put the device out of the sleep mode.        

        Returns
        -------
        bool
            True if the chip has finished startup and is ready to work.

        """
        Answer=self.ReadReg(0x00,1)
        if Answer[0]&0b11000000==0x40:
            return True
        return False
    
    def LoadConfigFromEEPROM(self):
        """
        Loads in RAM the configuration stored in EEPROM.
        It includes channel configuration, tables, coefficients, etc...
        

        Returns
        -------
        bool
            DESCRIPTION.

        """
        #First send the EEPROM unlock sequence
        self.WriteReg(0xB0, [0xA5, 0x3C, 0x0F, 0x5A])
        #Then send the EEPROM read command
        self.WriteReg(0x0,[0x96])
        self.DebugPrint("Read EPROM comand sent")
        self.DebugPrint("Waiting process end")
        #Wait for the EEPROM process to finish
        retry=100
        for i in range(retry) :
            Answer=self.ReadReg(0x00,1)
            if Answer[0]&0b11000000==0b01000000:
                self.DebugPrint("EEPROM read ended")
                break
            if i==retry-1:
                self.DebugPrint("EEPROM read timeout error")
                return False
        
        #Check succesfull EEPROM read process
        Answer=self.ReadReg(0x0D,1)
        if Answer[0]==0:
            self.DebugPrint("EEPROM read succesfull")
            return True  #If register 0x0D is zero, the process was succesfull.
        else: 
            self.DebugPrint("EEPROM read fail")
            return False #Else, there was a failure.
        
    def StartConversion(self,channel):
        """
        Starts the conversion in a single channel.

        Parameters
        ----------
        channel : Integer
            Channel to be measured
            Must be in the range 1 to 20.

        Returns
        -------
        None.

        """
        if channel>20:
            channel=20
        if channel<1:
            channel=1
        command=0b10000000+channel
        self.DebugPrint("Conversion started on channel " + str(channel)) 
        self.WriteReg(0x0, [command])
        
        
    def ReadResults(self,channel):
        """
        Reads the result from the last conversion in a given channel.
        The conversion must have been started and the finished sucessfully

        Parameters
        ----------
        channel : Integer
            Channel to be measured
            Must be in the range 1 to 20.

        Returns
        -------
        list
            faultdata: Binary data about sensor fail. 
                        If equal to one, the measurement is valid.
                        See datasheet for fault identification.
            temperature: Temperature in centigrades.

        """
        if channel>20:
            channel=20
        if channel<1:
            channel=1
        #Calculate the address of the results register
        address=0x10+4*(channel-1)
        #Read the register
        data=self.ReadReg(address,4)
        #decode data
        faultdata=data[0]
        temperature=(data[1]*65536+data[2]*256+data[3])/1024
        return [faultdata,temperature]
    
    
    
def sensor_measurement(n_measurements,chanel):
    # in : numero de medidas, canal del sensor
    import time
    ADC=LTC2984()
    #Optional debug printing..
    ADC.debug=False
    ADC.connect()
    print("Waiting for LTC2984 startup...")
    while (True) :
        if  ADC.HasStartupFinished() ==True:
            print("Started sucessfully")
            break
    ADC.LoadConfigFromEEPROM()
    return  ADC
    
    #Convert and read channel 8
    # for i in range (n_measurements):
    #     ADC.StartConversion(chanel) # Canal se sensor
    #     while(ADC.HasStartupFinished()==False):
    #         pass
    #     [fault,temp]=ADC.ReadResults(chanel) 
    #     print(f"Channel {chanel}: "+str(temp)+" fault "+str(fault))
        


    #Example of class usage.

