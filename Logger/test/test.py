import pymodbus
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import time

client = ModbusClient(method = 'rtu', port = '/dev/usb2485', baudrate = 9600, timeout = 2, parity = 'N')
print(client.connect())
length = 6
while True:
    x = client.read_holding_registers(0,length,unit = 1)
    #print(x.getRegister(0))
    ##print(x.getRegister(1))
    ##print(x.getRegister(2))
    ##print(x.getRegister(3))
    ##print(x.getRegister(4))
    ##print(x.getRegister(5))
    datawrite = ''
    for i in range(0,length-1):
        datawrite = datawrite + str(x.getRegister(i)) + '\t'
        print(datawrite)

    datawrite = datawrite[:-1]
    print(type(datawrite))
    print(datawrite)
##    with open('/home/pi/Desktop/Logger_New/sensor_data.txt', 'w') as filesensor:
##        filesensor.write(datawrite)
##    time.sleep(30)


