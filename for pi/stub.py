from flask import Flask

import os
import subprocess
import re
import Queue

import json
import Queue
import re
import serial
import subprocess
import sys
import threading
import time
import traceback
import urllib2
import os
import urllib2
import httplib
import requests

from cookielib import CookieJar

app = Flask(__name__)


#setting up response queue for serial communication with modem
threadscreated = False
commandQueue = Queue.Queue()
responseQueue = Queue.Queue()

@app.route('/')
def hello_world():
        return 'Hello World!'

        

DErrorSet = False ##set this value to true if uploading partical information is acceptable##
DError = 0 ##if this value is 
OnlyOne = False

@app.route('/auto')
def auto():
	return 'auto'
	#******programflow***********#	
	#ModemDetect()#
	#detect serial communication between gps modem and the pi#
	#GetIMSI
	#GetIMEI
	#GetCPUID
	#GetGPSStatus
	#StartGPSTrack
	####Loop####
	#GetGPSLocation
	##GetGPSInfo
	##GetPICData
	#encode
	#postToFile
	###LoopEND###
	#getIP##
	#uploadFileToServer###andIP
	#updateLocalSettings
	#displayLCDMessage

@app.route('/ModemDetect')
def ModemDetect():
    commandresult, commanderror = SendOS('ls /dev/ttyUSB*')
    """Checks if wireless modem is plugged into USB port and detectedby RaspberryPi"""
    #print "[ -- ] Checking Modem Present"
    modemTTYinterface = re.search('ttyUSB3', commandresult)
    # If modem plugged in and detected there should be a ttyUSB3 interface to communicate AT commands
    if modemTTYinterface and not commanderror:
        #print "[ OK ] Modem ttyUSB3 AT interface detected"
        result = "True" #needed to change from bool to string for flask output might need to change back for program flow#
    else:
    	print "[FAIL] Modem ttyUSB3 interface is NOT detected, check sierra modem is plugged into USB port."
    	result = "False" #needed to change from bool to string for flask output might need to change back for program flow#
    return result
	#return 'ModemDetect'#
	        
@app.route('/setupSerial')
def setupSerial():
    print "[ -- ] System Initiating Setup"
    global startTime
    global threadscreated
    if (threadscreated == False):
    	try:
        	serialDevice = serial.Serial(port='/dev/ttyUSB3', timeout=1)
        except Exception:
        	print "error setting up serial"
        if serialDevice.isOpen():
            print "[ -- ] Serial port is already open"
        else:
        	serialDevice.open()
        
        ##start the threads for communication with the modem###
        if (threadscreated == False):   
        	try:
        		st = threading.Thread(target=sendThread, args=(serialDevice,))
        		rt = threading.Thread(target=receiveThread, args=(serialDevice,))
        		st.daemon = True
        		rt.daemon = True
        		st.start()
        		rt.start()
        		threadscreated = True
        	except Exception:
        		print "error setting up threads"
        else:
        	print "threads already started"
        startTime = time.time()
        print "[ OK ] System Setup Complete"
        print "*****************************"
        return 'setup done'
    else:
    	return 'already setup'

@app.route('/GetIMSI')
def GetIMSI():
	if (threadscreated):
		command= 'AT+CIMI'
		matchcommand = 'CIMI'
		response = '(\d+)'
		waitTime = 2 
		printgood = '[ OK ] SIM Card IMSI is' 
		printbad = '[FAIL] SIM Card IMSI Retrieval Failed'
		value = 0 
		stateCommand(command)
		time.sleep(2)
		r = responseQueue.get(block=True, timeout=1)
		matchcommand =  re.search(matchcommand, r)
		response = re.search(response, r)
		if matchcommand and response:
			return printgood + r 
		else: 
			return printbad + r
	else:
		return "serial com not set up"


@app.route('/startTrack')
def startTrack():
	if (threadscreated):
		command= 'AT!GPSTRACK=2,255,100,600,1'
		matchcommand = 'CIMI'
		response = '(\d+)'
		waitTime = 2 
		printgood = '[ OK ] SIM Card IMSI is' 
		printbad = '[FAIL] SIM Card IMSI Retrieval Failed'
		value = 0 
		stateCommand(command)
		time.sleep(2)
		r = responseQueue.get(block=True, timeout=1)
		matchcommand =  re.search(matchcommand, r)
		response = re.search(response, r)
		if matchcommand and response:
			return printgood + r 
		else: 
			return printbad + r
	else:
		return "serial com not set up"

@app.route('/gpsStat')
def gpsStat():
	if (threadscreated):
		command= 'AT!GPSSTATUS?'
		matchcommand = 'CIMI'
		response = '(\d+)'
		waitTime = 2 
		printgood = '[ OK ] SIM Card IMSI is' 
		printbad = '[FAIL] SIM Card IMSI Retrieval Failed'
		value = 0 
		stateCommand(command)
		time.sleep(2)
		r = responseQueue.get(block=True, timeout=1)
		matchcommand =  re.search(matchcommand, r)
		response = re.search(response, r)
		if matchcommand and response:
			return printgood + r 
		else: 
			return printbad + r
	else:
		return "serial com not set up"

@app.route('/getLoc')
def getLoc():
	if (threadscreated):
		command= 'AT!GPSLOC?'
		matchcommand = 'CIMI'
		response = '(\d+)'
		waitTime = 2 
		printgood = '[ OK ] SIM Card IMSI is' 
		printbad = '[FAIL] SIM Card IMSI Retrieval Failed'
		value = 0 
		stateCommand(command)
		time.sleep(2)
		r = responseQueue.get(block=True, timeout=1)
		matchcommand =  re.search(matchcommand, r)
		response = re.search(response, r)
		if matchcommand and response:
			return printgood + r 
		else: 
			return printbad + r
	else:
		return "serial com not set up"

		
@app.route('/testAT')
def testAT():
	if (threadscreated):
		command= 'AT!RESET'
		matchcommand = 'CIMI'
		response = '(\d+)'
		waitTime = 2 
		printgood = '[ OK ] SIM Card IMSI is' 
		printbad = '[FAIL] SIM Card IMSI Retrieval Failed'
		value = 0 
		stateCommand(command)
		time.sleep(2)
		r = responseQueue.get(block=True, timeout=1)
		matchcommand =  re.search(matchcommand, r)
		response = re.search(response, r)
		if matchcommand and response:
			return printgood + r 
		else: 
			return printbad + r
	else:
		return "serial com not set up"

@app.route('/GetCPUid')
def GetCPUid():
	commandoutput = subprocess.Popen(["/bin/cat", "/proc/cpuinfo"], stdout=subprocess.PIPE)
	commandresult = commandoutput.communicate()[0]
	z =  re.search('Serial\s+\:(.*)$', commandresult, re.MULTILINE)
	return commandresult

@app.route('/Getextip')
def Getextip():
	commandresult = subprocess.Popen( ['curl', 'ipecho.net/plain'], stdout=subprocess.PIPE ).communicate()[0]
	return commandresult
    	
def stateCommand(command):
    """Based on current state send appropriate AT command."""
    #print "[ -- ] Sending AT command", command
    commandQueue.put(command + "\r\n", block=True, timeout=1)
    ##startTime = time.time()
    return True

def sendThread(serialDevice):
    """Send AT to modem by placing in commandQueue"""
    global commandQueue
    while True:
        # Block to avoid a busy-wait.
    	serialDevice.write(commandQueue.get(block=True))
    	
def receiveThread(serialDevice):        
    global responseQueue
    """Read AT response from modem by checking responseQueue"""
    lineBuffer = ""
    lineGroup = []
    nextChar = None
    char_recieved = False
    while True:
        nextChar = serialDevice.read()
        lineBuffer += nextChar
        if nextChar:
            # If data comes in then set timer alarm to send to response queue even if end of line is not received.
            char_recieved = True
            last_char_recieved = time.time()
            # Wait 2 seconds after last recieved modem char before raising timeout alarm
        if nextChar == '\n':   # Assume \r\n line termination
            lineGroup.append(lineBuffer)
            lineBuffer = ""
            if (''.join(lineGroup[-1]) == 'ERROR\r\n') or (''.join(lineGroup[-1]) == 'OK\r\n') or (''.join(lineGroup[-1]) == '+CME ERROR: no network service\r\n'):
                responseQueue.put(''.join(lineGroup), block=True)
                del lineGroup[:]
                char_recieved = False
                last_char_recieved = time.time()
        if char_recieved and (time.time() - last_char_recieved) > 2: 
            # Push data to responseQueue if last recieved char was more than more than 2 seconds ago
            #print "[ -- ] receiveThread timeout occured so put what has been recieved into the responseQueue and reset receiveThread"
            responseQueue.put(''.join(lineGroup), block=True)
            del lineGroup[:]
            char_recieved = False
            last_char_recieved = time.time()
        
        
@app.route('/encode')
def encode(imei, imsi , datetime, cpuID, latitude, longitude, alt, speed, rcount, temp, spare, spare2):
	return 'encode'
@app.route('/getPic')
def getPic():
	return 'encode'
@app.route('/post')
def postJsonM2MServer(targetUrl, latitude, longitude, timedateUTC, imei, imsi, cpuID, displayString, alt,speed):
	return 'postJsonM2MServer'
@app.route('/upl')
def upl():
	print "************UPLOAD FILE TO SERVER****************"
@app.route('/lcdWrite')
def lcdWrite(r):
	return 'lcdWrite'
	#STUB#
	#add code to output to LCD screen on hardware#
	#print r.text
@app.route('/getHeading')
def getHeading(r):
	return 'getHeading'
@app.route('/getVelVert')
def getVelVert(r):
	return 'getVelVert'
@app.route('/getVelHoriz')
def getVelHoriz(r):
	return 'getVelHoriz'
@app.route('/getAlt')
def getAlt(r):
	return 'getAlt'
@app.route('/getTimeUTC')
def getTimeUTC(r):
	return 'getTimeUTC'
@app.route('/getLatitude')
def getLatitude(r):
	return 'getLatitude'
@app.route('/getLongitude')
def getLongitude(r):
	return 'getLongitude'

	

	
	
@app.route('/SendOS')
def SendOS(OScom):
    """Sends commands to Raspberry OS and returns output. """
    #print "[ -- ] Sending OS command:", OScom
    commandoutput = subprocess.Popen([OScom], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    commandresult, commanderror = commandoutput.communicate()
    return commandresult, commanderror

if __name__ == '__main__':
        app.run(host='0.0.0.0',port=80,debug=True)
