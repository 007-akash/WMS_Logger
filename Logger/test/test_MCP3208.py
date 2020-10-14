#from gpiozero import MCP3208
channel_available = 6
def ReadMCP3208():
    try:
        print("\nReading MCP3208......\n")
        dataString = ''
        Channel = []
        value = []
        returnFloatVal = ''
        for count in range(0,channel_available):
            print("Count Channel: ",count)
            Scale = 'scale' + str(count + 1)
            Offset = 'offset' + str(count + 1)
            try:
                Channel.append(MCP3208(channel = count, clock_pin = ClockPin, mosi_pin = MosiPin, select_pin = SelectPin))
                #print(Scale)
                #print(mcp3208[Scale])
                #print(Channel[count].value)
                FloatValue = round(float(((Channel[count].value) - float(mcp3208[Offset])) * float(mcp3208[Scale])),2)
            except Exception as gpioErr:
                print(gpioErr)
                FloatValue = 0.00
            returnFloatVal = returnFloatVal + str(FloatValue) + ','
            value.append(int(FloatValue *100))
            #print("Value of Channel no {} is" .format(value[count]))
            dataString = dataString + (str(value[count])) + ','
        print("DataString of MCP3208 = " + dataString + '\n')
        return dataString,returnFloatVal
    except Exception as errADC:
        print(errADC)
        dataString = ''
        returnFloatVal = ''
        return dataString,returnFloatVal


print(ReadMCP3208())
