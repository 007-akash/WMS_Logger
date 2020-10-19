import pymodbus
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from gpiozero import MCP3208
from backports import configparser
import time
import logging
from subprocess import call

logging.basicConfig(filename = "../error_log/error.log",format='%(asctime)s %(message)s', filemode = 'a')
errlogger = logging.getLogger()
errlogger.setLevel(logging.ERROR)

"""
Configuration Parameter 
"""
try:
    config = configparser.ConfigParser()
    config.read('../config/LoggerConfig.ini')
    if(len(config.sections()) == 0):
        print("Logger Configuration file is empty!\n")
        call(['cp','../backup/LoggerConfig.ini','../config/LoggerConfig.ini'])
##    print("Configuration file is not empty :)\n")
    default = config['default']
    modbus = config['modbus']
    mcp3208 = config['mcp3208']
    basicConfig = config['basicconfig']
    
    portID = default['port']
    Baudrate = int(default['baudrate'])
    Method = default['method']

    
    channel_available = int(default['channels'])
    ClockPin = int(default['clock_pin'])
    MosiPin = int(default['mosi_pin'])
    SelectPin = int(default['select_pin'])
    dataRecordIntv = int(basicConfig['Data_Record_Interval'])
    scan_Intv = int(basicConfig['Data_Scan_Interval'])
    dataRecord = basicConfig['Disable_Record_save']
        
except Exception as e:
    print(e)

def ReadMCP3208():
    try:
        print("\nReading MCP3208......\n")
        dataString = ''
        Channel = []
        value = []
        returnFloatVal = ''
        print("Channel Available: ",channel_available)
        for count in range(0,channel_available):
            
            Scale = 'scale' + str(count + 1)
            Offset = 'offset' + str(count + 1)
            try:
                Channel.append(MCP3208(channel = count, clock_pin = ClockPin, mosi_pin = MosiPin, select_pin = SelectPin))
                #print(Scale)
                #print(mcp3208[Scale])
                #print(Channel[count].value)
                FloatValue = round(float(((Channel[count].value * float((mcp3208['CalibrationFactor']))) - float(mcp3208[Offset])) * float(mcp3208[Scale])),2)
            except Exception as gpioErr:
                print(gpioErr)
                FloatValue = 0.00
            returnFloatVal = returnFloatVal + str(FloatValue) + ','
            decimalPlace = str(FloatValue)[::-1].find('.')
            value.append(int(FloatValue *10))
            #print("Value of Channel no {} is" .format(value[count]))
            dataString = dataString + (str(value[count])) + ','
            #print("Count Channel: ",count)
            #print(dataString)
        print("DataString of MCP3208 = " + dataString + '\n')
        return dataString,returnFloatVal
    except Exception as errADC:
        print(errADC)
        dataString = ''
        returnFloatVal = ''
        return dataString,returnFloatVal
    
def ReadMINTAI08():
    print("\nReading MINTAI08.........\n")
    dataString = ''
    dataStringActual = ''
    try:
        client = ModbusClient(method = 'rtu', port = portID, baudrate = 9600, timeout = 2, parity = 'N')
        print(client.connect())
        if(client.connect()):
            x = client.read_holding_registers(0,5,unit = 1)
            print(x)
            MT1 = ((x.getRegister(0) - int(modbus['offset9'])) * int(modbus['scale9'])) 
            MT2 = ((x.getRegister(1) - int(modbus['offset10'])) * int(modbus['scale10'])) 
            MT3 = ((x.getRegister(2) - int(modbus['offset11'])) * int(modbus['scale11']))
            MT4 = ((x.getRegister(3) - int(modbus['offset12'])) * int(modbus['scale12'])) 
            MT5 = ((x.getRegister(4) - int(modbus['offset13'])) * int(modbus['scale13'])) 
            dataString = str(MT1) + ',' + str(MT2) + ',' + str(MT3) + ',' + str(MT4) + ',' + str(MT5)
            dataStringActual = str(MT1/10) + ',' + str(MT2/10) + ',' + str(MT3/10) + ',' + str(MT4/10) + ',' + str(MT5/10)
            print("MINTAI08 Data : " + dataString + '\n' )
        return dataString,dataStringActual
    except Exception as errMOD:
        print(errMOD)
        return dataString,dataStringActual

def TimeStamp():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

def SaveData():
    print("Recording Data")
    try:
        dataStringMCP3208,dataStringMCP3208Actual = ReadMCP3208()    
        dataStringMCP3208Actual = dataStringMCP3208Actual[:-1]
        dataStringMINTAI08, dataStringMINTAI08Actual = ReadMINTAI08()
    ##    print(type(dataStringMCP3208Actual))
        print("Data String MCP3208: ", dataStringMCP3208Actual)
        print("Data String MINTAI08: ", dataStringMINTAI08Actual)

        errFlag = '0'
        BufferData = ''
        print(len(dataStringMINTAI08Actual))
        
        if not (len(dataStringMCP3208Actual)>0 and len(dataStringMINTAI08Actual)>0):
            errFlag = '1'
            print("Error Flag 1")
        
        LD_Data = default['Logger_ID'] + ',' + default['Site_Id'] + ',' + default['Device_Type'] + ',' + default['Device_No'] + ',' + errFlag + ',' + TimeStamp() 
        BufferData = LD_Data + ',' + dataStringMINTAI08Actual + ',' + dataStringMCP3208Actual + '\n'
        print("BufferData: ",BufferData)
        with open('../data_log/LogData.txt', 'a') as fileLog:
            fileLog.write(BufferData)
    except Exception as errSave:
        print(errSave)
    
def ScanData():
    print("Scanning")
    try:
        dataStringMCP3208,dataStringMCP3208Actual = ReadMCP3208() 
        dataStringMCP3208 = dataStringMCP3208[:-1]
        dataStringMCP3208Actual = dataStringMCP3208Actual[:-1]
        dataStringMINTAI08, dataStringMINTAI08Actual = ReadMINTAI08()
    ##    print(type(dataStringMCP3208))
        print("Data String MCP3208: ", dataStringMCP3208)
        print("Data String MINTAI08: ", dataStringMINTAI08Actual)
        
        with open('../data_log/mcp3208_data.txt', 'w') as fileMCP:
            fileMCP.write(dataStringMCP3208)
        with open('../data_log/mintai08_data.txt', 'w') as fileMINT:
            fileMINT.write(dataStringMINTAI08)
        with open('../data_log/oled_data.txt', 'w') as fileOLED:
            fileOLED.write(dataStringMCP3208Actual+','+dataStringMINTAI08Actual)
    except Exception as errScan:
        print(errScan)

        
def main():    
    try:
        print("Run First Time")
        SaveData()
        time.sleep(1)
        ScanData()
        prevTimeRecord = time.time()
        prevTimeScan = time.time() + 1
        while True:
            #print("Entered in loop")
            
            if(((time.time() - prevTimeRecord) > dataRecordIntv) and dataRecord =='True'):
                print("Record Time = ",(time.time() - prevTimeRecord))
                SaveData()
                prevTimeRecord = time.time()
            
            if((time.time() - prevTimeScan) > scan_Intv):
                print("Scan Time: ",(time.time() - prevTimeScan))
                ScanData()
                prevTimeScan = time.time()
    except Exception as err:
        print(err)
        main()

main()
        




