#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  6 10:27:31 2023
Script for reading the MCP3910 dual ADC, used on the PWR METER 2 card of 
Mikroe. It gives simultaneous current and voltage readings. It is intended for
Raspberry PI usage, using the onboard SPI port.

@author: juan
"""

from spidev import SpiDev

class MCP3910:
    def __init__(self, spiport=0, spidevice=0,spispeed=4000000):
        #Debug mode: True to activate printing and aditional checks..
        self.debug=False
        
        #Default configuration registers:
        self.reg_phase=0x000000  #No phase delay between channels.
        self.reg_gain= 0x000000  #PGA gain =1 in booth channels.
        
        #STATUSCOM: Autoincrement on types mode, DR no high z, DR after last 
        #channel completation, CrC16bits, Data is 24 bits long, CRC disabled,
        #CRC interruption disabled, MOD pins disabled.
        self.reg_statuscom= 0xB90000 
        
        #CONFIG0: Disable on chip offset and gain calibration
        #default dittering, maximum boost, Prescaler 1/4, Oversampling 4096
        #default vref calibration.
        ##This configuration gives: MCLK=20Mhz, ACLK=5Mhz, DCLK=1.25Mhz, 
        #Data rate= 305.18Hz (3.28ms)
        self.reg_config0=0x3EE050
        
        #CONFIG1: Release channels from reset, release channels from shutdown
        #Configure internal vref, Activate XTAL oscilator, 
        self.reg_config1=0x000000
        
        #Offset and gain calibrations are disabled, 
        #so these registers are don't care
        self.reg_offCal0= 0x000000
        self.reg_offCal1= 0x000000
        self.reg_GainCal0=0x000000
        self.reg_GainCal1=0x000000
        
        #SPI port variables:
        self.spiport=spiport
        self.spidevice=spidevice
        self.spispeed=spispeed
        
        #Vref value for calculations
        self.vref=1.2
        
        #PWRMETER board resistors (for signal acquisition)
        #Voltage divider for Vin..
        self.R2=39e3
        self.R3=1e3
        #Resistance for current measurement
        self.R4=0.03
        
        
    def connect(self):
        #Creates SPI communication object
        self.SPI=SpiDev()
        self.SPI.open(self.spiport,self.spidevice)
        #Configure SPI settings
        self.SPI.mode = 0b11
        self.SPI.max_speed_hz=self.spispeed
        self.SPI.bits_per_word=8  
        #Control byte is 8 bits. Other registers are 24 bits.
        #We will use 8bits words, 24 bits are software converted.

    def unlockConfig(self):
        #Control reg for a write to LOCKREG
        controlreg=0x7e
        #Password to unlock config registers
        lock=0xA5
        #Data payload list (append 2 0x00 to fill the 24 bits register)
        payload= [controlreg,lock,0x00,0x00]
        payload_cp=payload.copy() #Payload is overwrriten by spi.xfer2
        self.SPI.xfer2(payload)
        if self.debug==True:
            print("Unlock command sent, payload:")
            print([hex(byte) for byte in payload_cp])
        
            
    def lockConfig(self):
        #Control reg for a write to LOCKREG
        controlreg=0x7e
        #Erases Password to lock config registers
        lock=0x00
        #Data payload list (append 2 0x00 to fill the 24 bits register)
        payload= [controlreg,lock,0x00,0x00]
        payload_cp=payload.copy() #Payload is overwrriten by spi.xfer2
        self.SPI.xfer2(payload)
        if self.debug==True:
            print("Lock command sent, payload:")
            print([hex(byte) for byte in payload_cp])
    
    def configure(self):
        """
        Function that performs the initial configuration of the ADC.
        
        Current information of the configuration registers are sent to the 
        MCP3910 by a continuous SPI transaction. Also, the configuration 
        writing lock is activated in the same transaction.
        If debug mode is True, the register data is readback and checked.

        Returns
        -------
        None.

        """
        #Unlock the configuration registers for writing.
        self.unlockConfig()
        #Begin a continuous write starting in the Phase register, 
        #to cover all the relevant registers.
        #Autoincrement type mode must be enabled!!! (default)
        payload=[]
        #Control reg for a write to Phase register
        controlreg=0x54
        #Concatenate the registers (in address order) to create 
        #the continous write payload
        payload=payload+list(controlreg.to_bytes(1, 'big'))
        payload=payload+list(self.reg_phase.to_bytes(3, 'big'))
        payload=payload+list(self.reg_gain.to_bytes(3, 'big'))
        payload=payload+list(self.reg_statuscom.to_bytes(3, 'big'))
        payload=payload+list(self.reg_config0.to_bytes(3, 'big'))
        payload=payload+list(self.reg_config1.to_bytes(3, 'big'))
        payload=payload+list(self.reg_offCal0.to_bytes(3, 'big'))
        payload=payload+list(self.reg_GainCal0.to_bytes(3, 'big'))
        payload=payload+list(self.reg_offCal1.to_bytes(3, 'big'))
        payload=payload+list(self.reg_GainCal1.to_bytes(3, 'big'))
        ##At this point is possible to write a lock operation in the same 
        #transfer, by writing 0x00 to the lock register.
        payload=payload+[0x00, 0x00, 0x00]
        payload_cp=payload.copy() #Payload is overwrriten by spi.xfer2
        self.SPI.xfer2(payload)
        if self.debug==True:
            print("Configuration sent, payload:")
            print([hex(byte) for byte in payload_cp])
            print("Reading registers for debug checking...")
            #Control reg for read at Phase register.
            payload_read=[0x55]
            #send dummy bytes to read the complete configuration registers
            dummy=0
            payload_read=payload_read+list(dummy.to_bytes(30,'big'))
            read_list=self.SPI.xfer2(payload_read)
            print("Register data:")
            print([hex(byte) for byte in read_list])
            #Check data integrity, except control and CRC registers...
            #Also skip dataready bits from statuscom...
            if payload_cp[1:8]==read_list[1:8] and payload_cp[10:-2]==read_list[10:-2]:
                print("Configuration register contents are OK")
            else:
                print("Error: Configuration registers are wrong")
        
        ##Finally, fill the gain variables for further calculations...
        PGA_CH1=(self.reg_gain & 0x38)>>3
        PGA_CH0=(self.reg_gain & 0x7)
        if PGA_CH0<6:
            self.gainCH0=2**PGA_CH0
        else :
            self.gainCH0=1
            
        if PGA_CH1<6:
            self.gainCH1=2**PGA_CH1
        else :
            self.gainCH1=1
        
        
    def waitDR(self):
        """
        FUunction that checks for the DR (Data ready) status from
        MCP3910.
        
        Check is done trough SPI, checking the statuscom register.

        Returns
        -------
        Status. True if there is data ready. False if not data ready.

        """
        #Control reg for read at statuscom register.
        payload_read=[0x59, 0x00,0x00,0x00]
        if self.debug==True:
            print("Checking DR, Payload:")
            print([hex(byte) for byte in payload_read])
        read_list=self.SPI.xfer2(payload_read)
        if self.debug==True:
            print("Statuscom read:")
            print([hex(byte) for byte in read_list])
        if read_list[-1]==0x00:
            return True
        else :
            return False
                
    def ReadBinChannels(self):
        """
        Function that reads current binary data from each ADC channel.
        
        This function waits for DR, and then retrieves data using one SPI transaction.

        Returns
        -------
        list
            List containing retrieved binary data from each channel.

        """
        #Control reg for read at channel registers.
        payload_read=[0x41]
        #Dummy data for reading 24x2 bits
        dummy=0
        payload_read+=list(dummy.to_bytes(6,'big'))
        if self.debug==True:
            print("Channel data read, payload")
            print([hex(byte) for byte in payload_read])
        read_list=self.SPI.xfer2(payload_read)
        if self.debug==True:
            print("Channel data read")
            print([hex(byte) for byte in read_list])
        dataCH0=int.from_bytes(read_list[1:4], 'big')
        dataCH1=int.from_bytes(read_list[4:7], 'big')
        return [dataCH0, dataCH1]
    
    def ConvertVin(self,dataCH0,dataCH1):
        """
        Function to convert binary data (previously read with ReadBinChannels) 
        into voltage at the converter inputs. NOTE: Oversampling (OSR) must 
        be >128

        Parameters
        ----------
        dataCH0 : Integer
            Binary ADC data from channel 1
        dataCH1 : Integer
            Binay ADC data from channel 2.

        Returns
        -------
        List: 
            VoltageCH0: Float
                Voltage data from channel 1.
            VoltageCH1: Float
                Voltage data from channel 2.
        """
        def twos_comp(val):
            """compute the 2's complement of int value val, 24 bits"""
            if (val & (1 << (24 - 1))) != 0: 
                # if sign bit is set 
                val = val - (1 << 24)        # compute negative value
            return val  
        
        VoltageCH0=twos_comp(dataCH0)*self.vref/(0x800000*self.gainCH0*1.5)
        VoltageCH1=twos_comp(dataCH1)*self.vref/(0x800000*self.gainCH1*1.5)
        return [VoltageCH0, VoltageCH1]  
    
    def ConvertPWRMETER2(self, dataCHO, dataCH1):
        """
        Function to convert binary data (previously read with ReadBinChannels) 
        into voltage and current as measured by the PWRMETER 2 click card.
        R2,R3 and R4 values are properties in the self and must be adjusted
        before calling this function.
        Parameters
        ----------
        dataCH0 : Integer
            Binary ADC data from channel 1
        dataCH1 : Integer
            Binary ADC data from channel 2.

        Returns
        -------
        list
            Voltage: Float
                Voltage measurement from the PWRmeter board.
            Current: Float
                Current measurement from the PWRmeter board.
        """
        [VoltageCH0,VoltageCH1]=self.ConvertVin(dataCHO, dataCH1)
        Voltage=VoltageCH0/((self.R3)/(self.R2+self.R3))
        Current=VoltageCH1/self.R4
        return [Voltage,Current]
    
        
if __name__ == '__main__' :
    #Example of class usage.
    import time
    ADC=MCP3910()
    #Optional debug printing..
    ADC.debug=True
    ADC.connect()
    ADC.configure()
    while(1):
        if ADC.waitDR()==True:
            print("*********************************")
            [ch0,ch1]=ADC.ReadBinChannels()
            print("Binary data: "+str(ch0)+" "+str(ch1))
            [v0,v1]=ADC.ConvertVin(ch0, ch1)
            print("Converter's input voltage: "+str(v0)+" "+str(v1))
            [voltage,current]=ADC.ConvertPWRMETER2(ch0, ch1)
            print("Card voltage and current: "+str(voltage)+" "+str(current))
            time.sleep(1);