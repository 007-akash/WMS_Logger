#!/usr/bin/env python

# --------------------------------------------------------------------------- #
# import the modbus libraries we need
# --------------------------------------------------------------------------- #
from pymodbus.server.asynchronous import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer
from backports import configparser

# --------------------------------------------------------------------------- #
# import the twisted libraries we need
# --------------------------------------------------------------------------- #
from twisted.internet.task import LoopingCall

# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
import logging
logging.basicConfig(filename = '../error_log/error.log', filemode='a')
log = logging.getLogger()
log.setLevel(logging.ERROR)
# set up logging to console 
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
# add the handler to the root logger 
logging.getLogger('').addHandler(console) 


"""
Configuration Parameter 
"""
try:
    config = configparser.ConfigParser()
    config.read('../config/serverConfig.ini')
    if(len(config.sections()) == 0):
        print("Modbus_Server Configuration file is empty!\n")
        call(['cp','../backup/serverConfig.ini','../config/serverConfig.ini'])
        
##    print("Configuration file is not empty :)\n")
    modbus = config['server']
    #print(modbus)
    port =int( modbus['port'])
    print("Port: ",port)
    ip_address = modbus['ip_address']
    print("ip_adress: ",ip_address)
    MTAvailable = int(modbus['MTAvailable'])
    scan_interval = int(modbus['scan_interval'])

    mcp3208 = config['mcp3208']
    ChannelAvailable = int(mcp3208['channels'])

    configLogger = configparser.ConfigParser()
    configLogger.read('../config/LoggerConfig.ini')
    if(len(configLogger.sections()) == 0):
        print("Logger Configuration file is empty!\n")
        call(['cp','../backup/LoggerConfig.ini','../config/LoggerConfig.ini'])
    modbus = configLogger['modbus']
    mcp3208 = configLogger['mcp3208']
    BasicCONFIG = configLogger['basicconfig']
    
except Exception as e:
    print(e)
    log.error(e)



# --------------------------------------------------------------------------- #
# define your callback process
# --------------------------------------------------------------------------- #    
def updating_writer(a):
    try:
        log.debug("updating the context")
        context = a[0]
        #print(context)
##        context1 = a[0][1]
##        context2  = a[0][2]
##        context3 = a[0][3]
        register = 3
        slave_id = 0x00
        StartAddress = 0
        ValuesMCP3208 = []
        ValuesMINTAI08 = []
        for i in range(1,ChannelAvailable):
            ValuesMCP3208.append(0)
        for i in range(1,MTAvailable):    
            ValuesMINTAI08.append(0)
        ValuesMCP3208store = context[slave_id].getValues(register, StartAddress, count = ChannelAvailable)
        print("Modbus Stored vaueMCP3208: ",ValuesMCP3208store)
        ValuesMINTAI08store = context[slave_id].getValues(register, ChannelAvailable , count = MTAvailable)
        print("Modbus stored valueValuesMINTAI08: ",ValuesMINTAI08store)
        ValuesMCP3208Configstore = context[slave_id].getValues(register, 30 , count = 17)
        print("Modbus Stored ConfigValuesMCP3208: ",ValuesMCP3208Configstore)
        ValuesMINTAI08Configstore = context[slave_id].getValues(register, 50 , count = 16)
        print("Modbus Stored ConfigValuesMINTAI08: ",ValuesMINTAI08Configstore)
        BasicConfigStore = context[slave_id].getValues(register, 70 , count = 4)
        print("Modbus Stored BasicConfigValues: ",BasicConfigStore)
##        
        with open('../data_log/mcp3208_data.txt','r') as file:
            data = file.readline()
        print("MCP3208 Read File: ",data)
        if not (data == ''):
            data = data.split(',')
            intData = []
            for i in data:
                #print(i)
                intData.append(int(i))
                #print(intData)
            #print("here")
            ValuesMCP3208 = intData
            log.debug("MCP3208 values: " + str(ValuesMCP3208))
        with open('../data_log/mintai08_data.txt','r') as file:
            data1 = file.readline()
        print("Read MINTAI08 File", data1)
        if not (data1 == ''):       
            data1 = data1.split(',')
            intData1 = []
            for j in data1:
                intData1.append(int(j))
            ValuesMINTAI08 = intData1
        


        MCP3208ConfigData = []
        for key1 in list(mcp3208.keys()):
            #print(key1)
            
            if not(mcp3208[key1]):
                mcp3208[key1] = '0'
            #print(mcp3208[key1])
            decimalplace = mcp3208[key1][::-1].find('.')
            MCP3208ConfigData.append(int(float(mcp3208[key1]) * 100))
        print("MCP3208ConfigData: " + str(MCP3208ConfigData) )

        
        MINTAI08ConfigData = []
        for keys2 in list(modbus.keys()):
            #print(keys2)
            if not(keys2):
                modbus[keys2] = '0'
            #print(modbus[keys2])
            decimalplace = modbus[keys2][::-1].find('.')
            MINTAI08ConfigData.append(int(float(modbus[keys2]) * 100))
        print("MINTAI08ConfigData" + str(MINTAI08ConfigData))

        BasicConfigData = []
        record = 1 if BasicCONFIG['Disable_Record_save'] =='True' else 0
        upload = 1 if BasicCONFIG['Disable_Record_upload'] =='True' else 0
        BasicConfigData.append(record)
        BasicConfigData.append(upload)
        BasicConfigData.append(int(BasicCONFIG['Data_Record_Interval']))
        BasicConfigData.append(int(BasicCONFIG['Data_Scan_Interval']))
        print("BasicConfigData" + str(BasicConfigData))

#-----------------------------------------------------------------------------#
#  Configuration Check
#-----------------------------------------------------------------------------#
        comparisonConfigValueMCP3208 = ComprisonValuesList(MCP3208ConfigData,ValuesMCP3208Configstore)
        print("Comparison Configuration Values MCP3208 : ", comparisonConfigValueMCP3208)
#            
        comparisonConfigValueMINTAI08 = ComprisonValuesList(MINTAI08ConfigData,ValuesMINTAI08Configstore)
        print("Comparison Configuration Values MINTAI08 : ", comparisonConfigValueMINTAI08)
#
#
        if(comparisonConfigValueMCP3208 == False):
            print("Changing Configuration MCP3208")
            setConfig('mcp3208', ValuesMCP3208Configstore)
            context[slave_id].setValues(register, 30, ValuesMCP3208Configstore)
        else:
            context[slave_id].setValues(register, 30, MCP3208ConfigData)
#    
        context[slave_id].setValues(register, StartAddress, ValuesMCP3208)
        context[slave_id].setValues(register, ChannelAvailable, ValuesMINTAI08)
#
        if(comparisonConfigValueMINTAI08 == False):
            print("Changing Configuration MINTAI08")
            setConfig('modbus', ValuesMINTAI08Configstore)
            context[slave_id].setValues(register, 50, ValuesMINTAI08Configstore)
        else:
            context[slave_id].setValues(register, 50, MINTAI08ConfigData)

        ComparisonBasicConfig = ComprisonValuesList(BasicConfigData, BasicConfigStore)
        if(ComparisonBasicConfig == False):
            print("Changing Basic Configuration Data")
            context[slave_id].setValues(register, 70, BasicConfigStore)
            BasicConfigStore[0] = 'True' if BasicConfigStore[0] == 1 else 'False'
            BasicConfigStore[1] = 'True' if BasicConfigStore[1] == 1 else 'False'
            setConfig('basicconfig', BasicConfigStore)
            
        else:
            context[slave_id].setValues(register, 70, BasicConfigData)
#----------------------------------------------------------------------------#
        print("************End of Transaction***************")
            
    except Exception as errUpdate:
        print(errUpdate)
        print("!!Error Updating the context\n")
        log.error(errUpdate)
        log.error("!!Error Updating the context")

def ComprisonValuesList(PrevValue, CurrentValue):
    if(len(PrevValue) == len(CurrentValue)):
        set1 = set(PrevValue)
        set2 = set(CurrentValue)
        if(set1 == set2):
            return True
        else:
            return False
        
def setConfig(section, valueList):
    i = 0
    for keys,value in configLogger.items(section):
        if(section == 'mcp3208'):
            configLogger.set(section, keys, str(round(valueList[i]/100,2)))
        else:
            configLogger.set(section, keys, str(valueList[i]))                         
                             
        i = i + 1
    with open('../config/LoggerConfig.ini', 'w') as configfile:
        configLogger.write(configfile)

def CheckInitialValues():
    ValueList = []
    MCP3208ConfigData = []
    for key1 in list(mcp3208.keys()):
        print(key1)
        
        if not(mcp3208[key1]):
            mcp3208[key1] = '0'
        print(mcp3208[key1])
        decimalplace = mcp3208[key1][::-1].find('.')
        MCP3208ConfigData.append(int(float(mcp3208[key1]) * 100))
    print("MCP3208ConfigData: " + str(MCP3208ConfigData))
    ValueList = ValueList + MCP3208ConfigData + [0,0,0]
    #ValueList.append[]

    
    MINTAI08ConfigData = []
    for keys2 in list(modbus.keys()):
        #print(keys2)
        if not(keys2):
            modbus[keys2] = '0'
        #print(modbus[keys2])
        decimalplace = modbus[keys2][::-1].find('.')
        MINTAI08ConfigData.append(int(float(modbus[keys2]) * 100))
    print("MINTAI08ConfigData" + str(MINTAI08ConfigData))
    ValueList = ValueList + MINTAI08ConfigData + [0,0,0,0]

    BasicConfigData = []
    record = 1 if BasicCONFIG['Disable_Record_save'] =='True' else 0
    upload = 1 if BasicCONFIG['Disable_Record_upload'] =='True' else 0
    BasicConfigData.append(record)
    BasicConfigData.append(upload)
    BasicConfigData.append(int(BasicCONFIG['Data_Record_Interval']))
    BasicConfigData.append(int(BasicCONFIG['Data_Scan_Interval']))
    print("BasicConfigData" + str(BasicConfigData))
    ValueList = ValueList + BasicConfigData
    print(ValueList)
    return ValueList
    

def run_updating_server():
    # ----------------------------------------------------------------------- # 
    # initialize your data store
    # ----------------------------------------------------------------------- #
    InitialValueList = [0]*29 + CheckInitialValues()
     
    
    store = ModbusSlaveContext(hr=ModbusSequentialDataBlock(0, InitialValueList))
    context = ModbusServerContext(slaves=store, single=True)
    
    
    # ----------------------------------------------------------------------- # 
    # initialize the server information
    # ----------------------------------------------------------------------- # 
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/bashwork/pymodbus/'
    identity.ProductName = 'pymodbus Server'
    identity.ModelName = 'pymodbus Server'
    identity.MajorMinorRevision = '2.3.0'
    
    # ----------------------------------------------------------------------- # 
    # run the server you want
    # ----------------------------------------------------------------------- # 
    time = scan_interval   # 5 seconds delay
    loop = LoopingCall(f=updating_writer, a=(context,))
    loop.start(time, now=False) # initially delay by time
    StartTcpServer(context, identity=identity, address=(ip_address, port))


if __name__ == "__main__":
    run_updating_server()
