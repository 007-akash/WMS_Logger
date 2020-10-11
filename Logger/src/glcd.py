from luma.core.render import canvas
from luma.oled.device import sh1106
from luma.core.interface.serial import i2c
import os.path
from PIL import Image, ImageFont, ImageDraw
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
    font=ImageFont.truetype(r'../fonts/OpenSans-Regular.ttf',15)
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((10, 0), key, fill="white",font=font,align="center")
        draw.text((30, 0), value, fill="white",font=font,align="center")

def model_info():
    config_info = configparser.ConfigParser()
    configinfo.read('../config/model.ini')
    info = configinfo['model_info']
    info_productName = info['product_name']
    info_modelNo = info['mdoel_no']
    return info_productName,info_modelNo

if __name__ == "__main__":
    try:
        device = sh1106(serial,width=128,height=64,rotate=2)
        print(device.width)
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
        with open('../data_log/oled_data.txt','r') as parameter:
            dataParameter = parameter.read()
            dataParameter = dataParameter.split(',')
        index = 0
            
        for key in listParameter:
            displayParameter(key,dataParameter[index])
            time.sleep(1)
            index = index + 1
            device.clear()
        
        
    except KeyboardInterrupt:
        pass




