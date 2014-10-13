from VSMS_LCD import VSMS_CharLCD
import RPi.GPIO as GPIO
import spidev
from time import sleep

class VSMS_NET:

	#! Regs
	SPI_PACKETBUFFERSTART		= 0x00
	SPI_STATUS			= 0x06
	SPI_BATVOLT			= 0x09
	SPI_TEMP			= 0x07
	SPI_NUMNFCCONNECTED		= 0x0B

	#! Debug LEDs
	LED_STAT	= 30
	LED_NET		= 31

	#! Warning LEDS
	WARN_TEMP_G	= 0b0010
	WARN_TEMP_Y	= 0b0011
	WARN_TEMP_R	= 0b0001
	WARN_TREAD_G	= 0b1000
	WARN_TREAD_Y	= 0b1100
	WARN_TREAD_R	= 0b0100
	
	def __init__(self):
		#! intiialise variables
		self.GPIO = GPIO
		self.GPIO.setmode(GPIO.BCM)
		self.SendCount = 0
		self.SensTemp = 0
		self.SensWire = 0
		self.SensMID = 0
		self.SensDID = 0
		self.Status = 0
		self.BatVolt = 0
		self.NumNFCConnected = 0
		self.AmbientTemp = 0

		# Status register is 8 bits, the structure is shown below
		# bit 0 (LSB) 	= (read only) VSMS main board is redy
		# bit 1		= (read only) reserved
		# bit 2		= (read only) packet ready
		# bit 3		= (read/write) buzzer on
		# bit 4-7	= (read only) reserved

		#! Prevent GPIO warning
		self.GPIO.setwarnings(False)

		#! Setup LED GPIO as outputs
		self.GPIO.setup(self.LED_STAT, GPIO.OUT)
		self.GPIO.setup(self.LED_NET, GPIO.OUT)
		
		#! Setup the GPIO interrupts
		self.GPIO.setup(03, GPIO.IN)
		self.GPIO.add_event_detect(03, GPIO.FALLING, callback=self.button_1, bouncetime=300)
		self.GPIO.setup(17, GPIO.IN)
		self.GPIO.add_event_detect(17, GPIO.FALLING, callback=self.button_2, bouncetime=300)
		self.GPIO.setup(27, GPIO.IN)
		self.GPIO.add_event_detect(27, GPIO.FALLING, callback=self.button_3, bouncetime=300)
		self.GPIO.setup(22, GPIO.IN)
		self.GPIO.add_event_detect(22, GPIO.FALLING, callback=self.button_4, bouncetime=300)
		
		self.lcd = VSMS_CharLCD()	# initialise the LCD

		#! Setup SPI
		self.spi = spidev.SpiDev()
		self.spi.open(0,0)

		#! Display the flash
		self.lcd.clear()

		self.lcd.message(" Northfield Systems\2========VSMS========\3 The Vehicle Safety\4 Monitoring System")


	def button_1(self, chan):
		self.lcd.clear()

		self.lcd.message("         BUTTON_1! >")

	def button_2(self, chan):
		self.lcd.clear()

		self.lcd.message("\2         BUTTON_2! >")

	def button_3(self, chan):
		self.lcd.clear()

		self.lcd.message("\3         BUTTON_3! >")

	def button_4(self, chan):
		self.lcd.clear()
		self.lcd.message("\4         BUTTON_4! >")

	def read_status (self):		# get the status reg on the main board
		self.spi.writebytes([self.SPI_STATUS])
		retVal = self.spi.readbytes(1)[0]
		self.Status = retVal
		return (retVal)

	def read_batteryVoltage (self):	# get the battery voltage
		self.spi.writebytes([self.SPI_BATVOLT])
		retValH = self.spi.readbytes(1)[0]
		self.spi.writebytes([self.SPI_BATVOLT+1])
		retVal = self.spi.readbytes(1)[0]
		self.BatVolt = (retValH & 0x03) << 8 | retVal
		return (self.BatVolt)

	def read_ambientTemp (self):	# get the ambient temperature
		self.spi.writebytes([self.SPI_TEMP])
		retValH = self.spi.readbytes(1)[0]
		self.spi.writebytes([self.SPI_TEMP+1])
		retVal = self.spi.readbytes(1)[0]
		self.AmbientTemp = (retValH & 0x03) << 8 | retVal
		return (self.AmbientTemp)

	def read_numNFCConnected (self):# get the number of NFCs connected
		self.spi.writebytes([self.SPI_NUMNFCCONNECTED])
		self.NumNFCConnected = self.spi.readbytes(1)[0]
		return (self.NumNFCConnected)

	def readin_packet (self):	# get most recent packet from the main board
		self.spi.writebytes([self.SPI_PACKETBUFFERSTART+0])
		self.SensMID = self.spi.readbyes(1)[0]			# Mfg ID

		self.spi.wrtiebytes([self.SPI_PACKETBUFFERSTART+1])
		DIDH = self.spi.readbyes(1)[0]
		self.spi.wrtiebytes([self.SPI_PACKETBUFFERSTART+2])
		DIDM = self.spi.readbyes(1)[0]
		self.spi.wrtiebytes([self.SPI_PACKETBUFFERSTART+3])
		DIDLWirTemp = self.spi.readbyes(1)[0]
		
		self.SensDID = (DIDH<<12)|(DIDM<<4)|(DIDLWirTemp>>4)	# Device ID (sensor ID)
		self.SensWire = (SISLWirTemp >> 2) & 0x03		# Wire 0=all good, 1 = one cut, 2 = two cut, 3 = all cut

		self.spi.wrtiebytes([self.SPI_PACKETBUFFERSTART+4])
		tempL = self.spi.readbyes(1)[0]
		self.SensTemp = ((DIDLWirTemp & 0x03)<<8) | tempL	# Will need some tweeking

		self.spi.writebytes([self.SPI_PACKETBUFFERSTART+5])
		self.SendCount = self.spi.readbytes(1)[0]		# number of revolutions since last measurement
	
	def SPIWrite(self, reg, data):
		if (reg == self.SPI_STATUS):
			stat = self.read_status();
			self.spi.writebytes([reg | 0b10000000, (data & 0b11111000) | (stat& 0b00000111)])

	def beep(self):
		self.SPIWrite(self.SPI_STATUS, 0b00001000)

	def LED(self, led, onOff):
		self.GPIO.output(led, onOff)
		return onOff

	def set_WarningLED(self, led):
		self.SPIWrite(self.SPI_STATUS, (led & 0x0F) << 4)
	
if __name__ == '__main__':
	
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

		sleep(0.5)				# slow the loop down
