from backports import configparser
import socket
import requests
import urllib.request
import time
from subprocess import call
import logging


try:
    configLogger = configparser.ConfigParser()
    configLogger.read('../config/LoggerConfig.ini')
    if(len(configLogger.sections()) == 0):
        print("Logger Configuration file is empty!\n")
        call(['cp','../backup/LoggerConfig.ini','../config/LoggerConfig.ini'])
    BasicCONFIG = configLogger['basicconfig']
    uploadConfig = configLogger['uploadConfig']
except Exception as e:
    print(e)

logging.basicConfig(filename = "../error_log/error_upload.log",format='%(asctime)s %(message)s', filemode = 'a')
errlogger = logging.getLogger()
errlogger.setLevel(logging.ERROR)

def internet_on():
    try:
        response = urllib.request.urlopen('http://www.example.com/',timeout = 10)
        return True
    except urllib.request.URLError as err: pass
    except Exception as e:
        errlogger.error(e)
        return False
    return False

def lastUploadRow():
    try:
        with open("../data_log/LastUploadRow.csv", 'r') as rowFile:
            rownum = rowFile.readline()
        
        if not (rownum):
            print("Recovery of LastUploadRow")
            call(['cp', '../backup/LastUploadRow.csv','../data_log/LastUploadRow.csv'])
            with open("../data_log/LastUploadRow.csv", 'r') as rowFile:
                rownum = rowFile.readline()

        rownum = int(rownum)  
        print("Last Updated Row = ",rownum)
        return rownum
    except Exception as e:
        errlogger.error(e)

def updateRowNum(row):
    try:
        with open("../data_log/LastUploadRow.csv", 'w') as rowFile:
            rowFile.write(str(row))
        print("Row Updated")
    except Exception as e:
        errlogger.error(e)

def read_Upload(rowSent):
    try:
        headers = {'User-Agent': 'Chrome/50.0.2661.102'}
        with open('../data_log/LogData.txt','r') as file:
            data = file.readlines()
        my_list = list(data)
        totalRow = len(my_list)
        print("Total Row = ",totalRow)
        print(rowSent)
        if(rowSent < totalRow):
            data = my_list[rowSent]
            data = data.split(',')
            LD = data[0:6]
            ID = data[6:]
            ID_data = ''
            LD_Data = LD[0] + ',' + LD[1] + ',' + LD[2] + ',' + LD[3] + ',' + LD[4] + ',' + LD[5]
##            print(LD[4])
            LD_Data = LD_Data.replace('\x00','') 
            print("LD_Data",LD_Data)
            for x in ID:
                ID_data = ID_data + x + ','
            ID_data = ID_data[:-1]
            ID_data = ID_data.replace('\x00','')
            print("ID_data",ID_data)
            print("Type",LD[2])
            deviceType=int(LD[2])
            if((deviceType>= 1) and (deviceType<101)):
                paramsadata = {'LD': LD_Data, 'ID': ID_data}
                r = requests.get('http://13.234.86.197/phpApi/InsertData_INV.php', headers = headers, params= paramsadata,timeout = 10)
            if((deviceType>=101) and (deviceType<151)):
                paramsadata = {'LD': LD_Data, 'WD': ID_data}
                r = requests.get('http://13.234.86.197/phpApi/InsertData_WMS.php', headers = headers, params= paramsadata,timeout = 10)
            print('Response:',r.text)
            resp=r.text
            if(resp.find("ConnectedOKOK")>=0):
                print("Data Upload Successful")
                rowSent = rowSent + 1
                updateRowNum(rowSent)
    except Exception as e:
        errlogger.error(e)


def main():
    try:
##        with open("../config/upload_config.txt", 'r') as config:
##            config_data = config.readline()
##        if not (config_data):
##            call(['cp', '../backup/upload_config.txt','../config/upload_config.txt'])
##            with open("../config/upload_config.txt", 'r') as config:
##                config_data = config.readline()
                
##        config_data = config_data.split(',')
        uploadInterval = int(uploadConfig['timeInterval'])
        print("Upload Interval: ",uploadInterval)
        
        run = 1
        lastTime = time.time()
        count = 0
        call(["sudo", "pon","rnet"])
        time.sleep(20)
        retryWait = 10 #Set Retry wait in seconds
        lastTimeretry = time.tme()
        while True:
            if(run):
                print("Checking Internet Connection..........")
                
##                print("waiting for 20s")
                
                if(internet_on()):
                    print("Internet is OK")
                    rownum = lastUploadRow()
                    read_Upload(rownum)
                    run = 0
                    lastTime = time.time()
                    count = 0
                else:
                    #count = count + 1
                    if((time.time()- lastTimeretry > retryWait)):
                        count=0;
                        call(["sudo", "poff","rnet"])
                        time.sleep(5)
                        print("Restart internet ")
                        call(["sudo", "pon","rnet"])
                        time.sleep(5)
                        lastTimeretry = time.time()
                        
                time.sleep(1)
            if(run == 0 and ((time.time() - lastTime) > uploadInterval)):
                print("here")
                run = 1
    except Exception as e:
        errlogger.error(e)
        main()

if __name__ == '__main__':
    if(BasicCONFIG['Disable_Record_upload'] == 'True'):
        main()

