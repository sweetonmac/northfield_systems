from flask import Flask
from flask import render_template, request
from time import sleep
from VSMSapp import VSMSapp

import RPi.GPIO as GPIO
import spidev

from VSMS_LCD import VSMS_CharLCD
from VSMS_NET import VSMS_NET


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

#VSMS = VSMS_NET()

#VSMSapp = Flask(__name__)

VSMS = VSMS_NET()
print "init happened"
VSMS.lcd.clear()

if(VSMS.read_status() & 0b00000001):
	VSMS.lcd.message ("VSMS is ready!")

VSMS.beep()
VSMS.set_WarningLED(VSMS.WARN_TEMP_G | VSMS.WARN_TREAD_G)


@VSMSapp.route('/',methods=['GET', 'POST'])
def hello_world():
	global VSMS
	#lcd = VSMS_CharLCD()
	VSMS.lcd.clear()
	VSMS.lcd.message("Hello World!\2OWEN SMELLS BAD")
	return 'Hello World!'
	
@VSMSapp.route('/stat', methods=['GET', 'POST'])
def stat():
	if request.method =='POST':
		message = request.form['message']
		#lcd = VSMS_CharLCD()
		VSMS.lcd.clear()
		VSMS.lcd.message(message)
	try:
		file = open("dump.txt","r")
		r = file.read()
		file.close()
		stringArray = r.split("###")
		global imsiStat
		imsiStat = stringArray[0]
		global imeiStat
		imeiStat = stringArray[1]
		global modemStat
		modemStat = stringArray[2]
		global serialStat
		serialStat = stringArray[3]
		global trackingStat
		trackingStat = stringArray[4]
		global gpsStat
		gpsStat = stringArray[5]
		global satStat
		satStat = stringArray[6]
		global locationStat
		locationStat = stringArray[7]
		global CPUIDStat
		CPUIDStat = stringArray[8]
		global extIpStat
		extIpStat = stringArray[9]
		global locationStat
		locationStat = stringArray[10]
		global headingStat
		headingStat = stringArray[11]
		global velVertStat
		velVertStat  = stringArray[12]
		global velHorizStat
		velHorizStat  = stringArray[13]
		global altStat
		altStat  = stringArray[14]
		global timeUTCStat
		timeUTCStat = stringArray[15]
		global latitudeStat
		latitudeStat = stringArray[16]
		global longitudeStat
		longitudeStat = stringArray[17]
	except Exception:
		pass	
	return render_template("stat.html",**globals())

@VSMSapp.route('/SendOS')
def SendOS(OScom):
    """Sends commands to Raspberry OS and returns output. """
    #print "[ -- ] Sending OS command:", OScom
    commandoutput = subprocess.Popen([OScom], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    commandresult, commanderror = commandoutput.communicate()
    return commandresult, commanderror
    
	
def NETMAIN():	
	VSMS.lcd.clear()

	if(VSMS.read_status() & 0b00000001):
		VSMS.lcd.message ("VSMS is ready!")

	VSMS.beep()
	VSMS.set_WarningLED(VSMS.WARN_TEMP_G | VSMS.WARN_TREAD_G)


	sleep(.5)

