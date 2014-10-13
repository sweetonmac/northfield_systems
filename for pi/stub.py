from time import sleep
from multiprocessing import Process


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

from VSMS_LCD import VSMS_CharLCD
#from VSMS_NET import VSMS_NET
lcd = VSMS_CharLCD()



#state Variables
imsiStat = "not yet initialised"
imeiStat = "not yet initialised"
modemStat = "not yet initialised"
serialStat = "not yet initialised"
trackingStat = "not Tracking"
gpsStat = "not yet initialised"
satStat = "not yet initialised"
locationStat = "not yet initialised"
CPUIDStat = "not yet initialised"
extIpStat = "not yet initialised"
locationStat = "not yet initalised"
headingStat = "not yet initalised"
velVertStat = "not yet initalised"
velHorizStat = "not yet initalised"
altStat = "not yet initalised"
timeUTCStat = "not yet initalised"
latitudeStat = "not yet initalised"
longitudeStat = "not yet initalised"
gpsFixBool = 0
trackstarted = 0
wait =False

lcd.clear()
lcd.message(" Northfield Systems\2========VSMS========\3 The Vehicle Safety\4 Monitoring System")

#setting up response queue for serial communication with modem
threadscreated = False
autostarted = False
commandQueue = Queue.Queue()
responseQueue = Queue.Queue()


def hello_world():
	lcd = VSMS_CharLCD()
	lcd.clear()
	lcd.message("Hello World!\2OWEN SMELLS BAD")
	return 'Hello World!'


def stat():
	return render_template("stat.html",**globals())


def VSMSNET():
	VSMS = VSMS_NET()
	VSMS.lcd.clear()

	if(VSMS.read_status() & 0b00000001):
		VSMS.lcd.message ("VSMS is ready!")

	VSMS.beep()
	VSMS.set_WarningLED(VSMS.WARN_TEMP_G | VSMS.WARN_TREAD_G)


	led = 0
	while True:
		led = VSMS.LED(VSMS.LED_STAT, ~led)	# flash status LED

		if (VSMS.read_numNFCConnected() > 0):	# turn on network LED if an NFC is connected
			VSMS.LED(VSMS.LED_NET, 1)

		sleep(0.5)  


DErrorSet = False ##set this value to true if uploading partical information is acceptable##
DError = 0 ##if this value is 
OnlyOne = False


def auto():
	global gpsFixBool
		
	global imsiStat
	global imeiStat
	global modemStat
	global serialStat
	global trackingStat
	global gpsStat
	global satStat
	global locationStat
	global CPUIDStat
	global extIpStat
	global locationStat
	global headingStat
	global velVertStat
	global velHorizStat
	global altStat
	global timeUTCStat
	global latitudeStat
	global longitudeStat
	
	if serialStat != "ACTIVE":
		setupSerial()
	if modemStat != "Connected":
		ModemDetect()
	print "server started"
	#******programflow***********#	
	#detect serial communication between gps modem and the pi#
	if imsiStat == "not yet initialised":
		GetIMSI()
	if imeiStat == "not yet initialised":
		GetIMEI()
	if CPUIDStat == "not yet initialised":
		GetCPUid()
	startTrack()
	r =  getLoc()
	if gpsFixBool == 1:
		getHeading(r)
		getVelVert(r)
		getVelHoriz(r)
		getAlt(r)
		getLatitude(r)
		getLongitude(r)
	getGpsSat()
	gpsStat = getGpsStat()
	getTimeUTC(gpsStat)
	
	##Dump Data
	file = open("dump.txt","w")
	file.write(imsiStat + "###" + imeiStat + "###" +modemStat + "###" +serialStat + "###" +trackingStat + "###" + gpsStat + "###" + satStat + "###" + locationStat+ "###" + CPUIDStat+ "###" + extIpStat + "###" + locationStat+ "###" +headingStat+ "###" + velVertStat+ "###" + velHorizStat + "###" + altStat + "###" + timeUTCStat + "###" + latitudeStat+ "###" + longitudeStat)
	file.close;
	return 'auto'


def ModemDetect():
	global modemStat
	commandresult, commanderror = SendOS('ls /dev/ttyUSB*')
	"""Checks if wireless modem is plugged into USB port and detectedby RaspberryPi"""
	#print "[ -- ] Checking Modem Present"
	modemTTYinterface = re.search('ttyUSB3', commandresult)
	# If modem plugged in and detected there should be a ttyUSB3 interface to communicate AT commands
	if modemTTYinterface and not commanderror:
		#print "[ OK ] Modem ttyUSB3 AT interface detected"
		result = "True" #needed to change from bool to string for flask output might need to change back for program flow#
		modemStat = "Connected"
	else:
		print "[FAIL] Modem ttyUSB3 interface is NOT detected, check sierra modem is plugged into USB port."
		result = "False" #needed to change from bool to string for flask output might need to change back for program flow#
		modemStat = "modemNotConnected"
	return result
	#return 'ModemDetect'#
	        

def setupSerial():
    print "[ -- ] System Initiating Setup"
    global startTime
    global threadscreated
    global serialStat
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
        		autoT = threading.Thread(target=autoWrap)
        		autoT.daemon = False
        		st.daemon = True
        		rt.daemon = True
        		rt.start()
        		st.start()
        		autoT.start()
        		threadscreated = True
        	except Exception:
        		print "error setting up threads"
        else:
        	print "threads already started"
        startTime = time.time()
        print "[ OK ] System Setup Complete"
        print "*****************************"
        serialStat = "ACTIVE"
        return 'setup done'
    else:
    	serialStat="ACTIVE"
    	return 'already setup'


def GetIMSI():
	global imsiStat
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
		while responseQueue.empty():
			pass
		r = responseQueue.get(block=True, timeout=1)
		matchcommand =  re.search(matchcommand, r)
		time.sleep(1)
		response = re.search(response, r)
		if matchcommand and response:
			imsiStat = r
			return printgood + r 
		else: 
			imsiStat = r
			return printbad + r
	else:
		return "serial com not set up"


def GetIMEI():
	global imeiStat
	if (threadscreated):
		command= 'AT+CGSN'
		matchcommand = 'CGSN'
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
			imeiStat = r
			
			return printgood + r 
		else: 
			imeiStat = r
			return printbad + r
	else:
		return "serial com not set up"


def startTrack():
	global trackingStat
	global trackstarted
	if (threadscreated):
		command= 'AT!GPSTRACK=1,255,100,600,1'
		matchcommand = 'GPSTRACK'
		response = 'OK'
		waitTime = 2 
		printgood = '[ OK ] Started GPS Tracking Session' 
		printbad = '[FAIL]'
		value = 0 
		stateCommand(command)
		time.sleep(2)
		r = responseQueue.get(block=True, timeout=1)
		matchcommand =  re.search(matchcommand, r)
		response = re.search(response, r)
		if matchcommand and response:
			trackstarted = 1
			trackingStat = printgood + r
			return r 
		else: 
			trackstarted = 0
			trackingStat = printbad + r
			return printbad + r
	else:
		return "serial com not set up"


def getGpsStat():
	global gpsStat
	if (threadscreated):
		command= 'AT!GPSSTATUS?'
		matchcommand = 'GPSSTATUS'
		response = 'Fix Session Status = ACTIVE'
		waitTime = 2 
		printgood = '[ OK ]' 
		printbad = '[FAIL] Retrieval Failed'
		value = 0 
		stateCommand(command)
		time.sleep(2)
		r = responseQueue.get(block=True, timeout=1)
		matchcommand =  re.search(matchcommand, r)
		response = re.search(response, r)
		if matchcommand and response:
			gpsStat = printgood + r
			return r 
		else: 
			gpsStat = printbad
			return printbad + r
	else:
		return "serial com not set up"

def getGpsSat():
	global satStat
	if (threadscreated):
		command= 'AT!GPSSATINFO?'
		matchcommand = 'GPSSATINFO'
		response = 'Satellites in view'
		waitTime = 2 
		printgood = '[ OK ]' 
		printbad = '[ -- ] NO SAT INFO'
		value = 0 
		stateCommand(command)
		time.sleep(2)
		r = responseQueue.get(block=True, timeout=1)
		matchcommand =  re.search(matchcommand, r)
		response = re.search(response, r)
		if matchcommand and response:
			satStat = printgood + r
			return r 
		else: 
			satStat = printbad
			return printbad + r
	else:
		return "serial com not set up"


def getLoc():
	global gpsFixBool
	global locationStat
	if (threadscreated):
		command= 'AT!GPSLOC?'
		matchcommand = 'GPSLOC'
		response = '(\d+)'
		waitTime = 2 
		printgood = '[ OK ] GPS Fix OK' 
		printbad = '[FAIL] No Fix Yet'
		value = 0 
		stateCommand(command)
		time.sleep(2)
		r = responseQueue.get(block=True, timeout=1)
		matchcommand =  re.search(matchcommand, r)
		response = re.search(response, r)
		if matchcommand and response:
			gpsFixBool = 1
			locationStat = printgood + r
			return printgood + r 
		else: 
			gpsFixBool = 0
			locationStat = printbad + r
			return printbad + r
	else:
		return "serial com not set up"


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


def GetCPUid():
	global CPUIDStat
	commandoutput = subprocess.Popen(["/bin/cat", "/proc/cpuinfo"], stdout=subprocess.PIPE)
	commandresult = commandoutput.communicate()[0]
	z =  re.search('Serial\s+\:(.*)$', commandresult, re.MULTILINE)
	CPUIDStat = commandresult
	return commandresult


def Getextip():
	global extIpStat
	commandresult = subprocess.Popen( ['curl', 'ipecho.net/plain'], stdout=subprocess.PIPE ).communicate()[0]
	extIpStat = commandresult
	return commandresult
    	
def stateCommand(command):
    """Based on current state send appropriate AT command."""
    #print "[ -- ] Sending AT command", command
    commandQueue.put(command + "\r\n", block=True, timeout=1)
    ##startTime = time.time()
    return True

def sendThread(serialDevice):
    """Send AT to modem by placing in commandQueue"""
    global wait
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
        
        

def encode(imei, imsi , datetime, cpuID, latitude, longitude, alt, speed, rcount, temp, spare, spare2):
	return 'encode'

def getPic():
	return 'encode'

def postJsonM2MServer(targetUrl, latitude, longitude, timedateUTC, imei, imsi, cpuID, displayString, alt,speed):
	return 'postJsonM2MServer'

def upl():
	print "************UPLOAD FILE TO SERVER****************"

def lcdWrite(r):
	return 'lcdWrite'
	#STUB#
	#add code to output to LCD screen on hardware#
	#print r.text

def getHeading(r):
	global headingStat
	"""Extract Heading from GPSLOC response and format for transmission to server"""
	z =  re.search('Heading: ([\.\d]+)', r)
	if not z:
		headingStat = "no heading -- " + r
		return None
	else:
		Heading = float(z.group(1))
		print '####Heading####' + str(Heading) + '########'
		headingStat = str(Heading)
		return headingStat


def getVelVert(r):
	global velVertStat
	"""Extract VelHoriz from GPSLOC response and format for transmission to server"""
	z =  re.search('VelVert: ([\.\d]+)', r)
	if not z:
		return 0
	else:
		VelVert = float(z.group(1))
		print '####VelVert####' + str(VelVert) + '########'
		velVertStat = str(VelVert)
		return velVertStat


def getVelHoriz(r):
	global velHorizStat
	"""Extract VelHoriz from GPSLOC response and format for transmission to server"""
	z =  re.search('VelHoriz: ([\.\d]+)', r)
	if not z:
		return 0
	else:
		VelHoriz = float(z.group(1))
		print '####VelHoriz####' + str(VelHoriz) + '########'
		velHorizStat = str(VelHoriz)
		return velHorizStat
	

def getAlt(r):
	global altStat
	"""Extract altitude from GPSLOC response and format for transmission to server"""
	z =  re.search('Altitude: (\d+)', r)
	if not z:
		return None
	else:
		alt = float(z.group(1))
		altStat = str(alt)
		print '####alt####' + str(alt) + '########'
		return altStat
	

def getTimeUTC(r):
	global timeUTCStat
	"""Extract time from GPSLOC response and format for transmission to server"""
	#print "Extracting time from GPSLOC response"
	# Example Time: 2013 04 16 1 03:15:16 (GPS)
	z =  re.search('time: (\d+) (\d+) (\d+) (\d+) ([\:\:\d]+)', r)
	if not z:
		return None
	else:
		# Now convert.
		yearUTC = z.group(1)
		monthUTC = z.group(2)
		dayUTC = z.group(3)
		timeUTC = z.group(5)
		timedateUTC = str(yearUTC) + "-" + str(monthUTC)  + "-" + str(dayUTC) + " " + str(timeUTC)
		# Example timedateUTC = 2013-04-16 03:15:16
		timeUTCStat = timedateUTC
		return timeUTCStat

def getLatitude(r):
	global latitudeStat
	"""Extract latitude from response and format for transmission to server"""
	z =  re.search('Lat: (\d+) Deg (\d+) Min ([\.\d]+) Sec (\w)', r)
	if not z:
		return None
	else:
		# Now convert.
		degrees = int(z.group(1))
		minutes = int(z.group(2))
		seconds = float(z.group(3))
		hemisphere = str(z.group(4))
		# FIX bearing.
		if (hemisphere == 'N'):
			latitudeStat = degrees + ( ( minutes + (seconds / 60) ) / 60)
			return latitudeStat
		elif (hemisphere == 'S'):
			latitudeStat = (degrees + ( ( minutes + (seconds / 60) ) / 60))*-1
			return latitudeStat
		else:
			latitudeStat = 'Failure to parse latitude'
		raise Exception('Failure to parse latitude')

	

def getLongitude(r):
	global longitudeStat
	"""Extract longitude from response and format for transmission to server"""
	z =  re.search('Lon: (\d+) Deg (\d+) Min ([\.\d]+) Sec (\w)', r)
	if not z:
		return None
	else:
		# Now convert.
		degrees = int(z.group(1))
		minutes = int(z.group(2))
		seconds = float(z.group(3))
		primeMeridian = str(z.group(4))
		if (primeMeridian == 'E'):
			longitudeStat = degrees + ( ( minutes + (seconds / 60) ) / 60)
			return longitudeStat
		elif (primeMeridian == 'W'):
			longitudeStat = (degrees + ( ( minutes + (seconds / 60) ) / 60))*-1
			return longitudeStat
		else:
			longitudeStat = 'Failure to parse longitude'
			raise Exception('Failure to parse longitude')
	

def SendOS(OScom):
    """Sends commands to Raspberry OS and returns output. """
    #print "[ -- ] Sending OS command:", OScom
    commandoutput = subprocess.Popen([OScom], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    commandresult, commanderror = commandoutput.communicate()
    return commandresult, commanderror

def autoWrap():
	while True:
		sleep(1)
		auto()
	return
	
if __name__ == '__main__':
	autoWrap()
