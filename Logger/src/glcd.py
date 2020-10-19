from luma.core.render import canvas
from luma.oled.device import sh1106
from luma.core.interface.serial import i2c
import os.path
from PIL import Image, ImageFont, ImageDraw
from backports import configparser
import time

serial = i2c(port=1, address=0x3C)

def main():
##    img_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
##         'pi_logo.png'))
    logo = Image.open('../images/logo.png').convert("1")
    background = Image.new("1", device.size, "black")
    posn = (32, 0)
    background.paste(logo,posn)
    device.display(background.convert(device.mode))

def displayParameter(key,value):
    font=ImageFont.truetype(r'../fonts/calibri.ttf',15)
    with canvas(device) as draw:
        draw.rectangle([(1,15),(127,62)], outline="black", fill="white")
        w, h = draw.textsize(key)
        draw.text(((128-w)/2, 25), key, fill="black",font=font)
        w, h = draw.textsize(value)
        draw.text(((128-w)/2, 42), value, fill="black",font=font)
        draw.polygon([(85,4), (79, 11), (85,11)], fill = "white")
        draw.polygon([(107,4),(115,4),(118,6),(118,9),(115,11),(107, 11)], fill = "white")
        curTime = time.localtime()
        time_string = time.strftime("%H : %M", curTime)
        fontHeader = ImageFont.truetype(r'../fonts/calibri.ttf',10)
        draw.text((5, 4), time_string, fill="white",font=fontHeader) 

##def displayIcons():
##    with canvas(device) as draw:


##def updateTime():
##    with canvas(device) as draw:
                 
    
def model_info():
    configinfo = configparser.ConfigParser()
    configinfo.read('../config/model.ini')
    info = configinfo['model_info']
    info_productName = info['product_name']
    info_modelNo = info['mdoel_no']
    updateRate = info['updateRate']
    return info_productName,info_modelNo,updateRate

def writeScreen():
    with open('../data_log/oled_data.txt','r') as parameter:
        dataParameter = parameter.read()
        dataParameter = dataParameter.split(',')
    index = 0
    lengthParameter = len(dataParameter)
    if(lengthParameter<11):
        for x in range(lengthParameter,11):
            dataParameter.append('NA')
    for key in listParameter:
        displayParameter(key,dataParameter[index])
        time.sleep(1)
        index = index + 1
        #device.clear()

if __name__ == "__main__":
    try:
        device = sh1106(serial,width=128,height=64,rotate=2)
        #print(device.width)
        device.clear()
        main()
        time.sleep(2)
        device.clear()
        time.sleep(1.5)
        info = model_info()
        displayParameter(info[0],info[1])
        time.sleep(1.5)
        listParameter = ['GHI',
             'G.T.I.',
             'W.S.',
             'W.D.',
             'A.T.',
             'R.H.',
             'M.T1(Celsius)',
             'M.T2(Celsius)',
             'M.T3(Celsius)',
             'M.T4(Celsius)',
             'M.T5(Celsius)']
        print(info[2])

        updateRate = int(info[2])
        
        #One Time Run
##        displayIcons()
##        time.sleep(2)
##        updateTime()
        lastUpdatedClock = time.time()
        writeScreen()
        lastUpdatedTime = time.time()
        
        #Entered in Loop
        while True:
            if((time.time() - lastUpdatedTime)>updateRate):
                writeScreen()
                lastUpdatedTime = time.time()
##            if((time.time() - lastUpdatedClock)>60):
##                updateTime()
##                lastUpdatedClock = time.time()

    except KeyboardInterrupt:
        pass








