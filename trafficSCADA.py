#! /usr/local/bin/python3.6

'''
##########################################
# Traffic Light SCADA
# Version: 1.7.0   
# Date: 04/2018
# License: MIT
# Description: This python script operates as a Traffic Light SCADA system that
# queries 4 MODBUS PLC's using pymodbus from https://github.com/riptideio/pymodbus.
# These 4 PLC's follow traffic light style logic
# Additionally, hosts a websocket listener to interface with a web based HMI and report the PLC status
# to the HMI
# Python version: 3.6
# Author: Matthew
# Makes use of the pymodbus and twisted python packages
#########################################
'''

import socket, hashlib, base64, threading, time
import re, random
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.transaction import  ModbusTransactionManager as tranManager
from autobahn.twisted.websocket import WebSocketServerProtocol
from twisted.internet.task import LoopingCall
import sys, signal, os, math
from twisted.python import log
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerFactory
from threading import Thread
import numpy

import logging
logging.basicConfig()
log = logging.getLogger()
#log.setLevel(logging.DEBUG)
webSocketStatus = ''
operatorMessages = []
clock = 0

class MyServerProtocol(WebSocketServerProtocol):
	###The Websocket Listener that interfaces with the WEB HMI
	def onConnect(self, request):
		updateWebSocketStatus("Client connecting: {}".format(request.peer))
		#updateWebSocketStatus("WebSocket connection open")
		registerSocket(self)
		
	def onOpen(self):
		#updateWebSocketStatus("WebSocket connection open")
		#respond with traffic light tags (names of each intersection)
		sendPLCNames()
	def onMessage(self, payload, isBinary):
		if isBinary:
			addToScadaMessageQueue("Binary message received: {} bytes".format(len(payload)))
		else:
			addToScadaMessageQueue("Text message received: {}".format(payload.decode('utf8')))
		processMessage(format(payload.decode('utf8')))
	def sendAMessage(self,msg):
		self.sendMessage(msg, isBinary=False)

	def onClose(self, wasClean, code, reason):
		updateWebSocketStatus("WebSocket connection closed: {}".format(reason))
		unRegisterSocket(self)
		
class plcInterrogator(threading.Thread):
        
	def __init__(self, plcIP, plcPort, plcName):
			self.plcIP=plcIP
			self.plcPort=plcPort
			self.registers = [0] * 10
			self.coils = [0]*10
			self.plcName = plcName
			self.client = ModbusClient(self.plcIP)
			threading.Thread.__init__(self)
			self.errorFlag = False 
			self.errorMsg = ''
			self.reportedMode = 'NORMAL'
			
	def manageTransactionCounter(self):
		#checks with the Transaction Manager to ensure we don't go above 
		#255 transactions. Bug in pymodbus allows it to go to 256 and errors out
		#any transaction requests
		if self.client.transaction.tid > 225: #about to go over 255, reset it
			self.client.transaction.reset()

	def getHoldingRegisters(self, startByte, bytesCount):
		regs = self.client.read_holding_registers(address=startByte,count=bytesCount)
		self.manageTransactionCounter()
		return regs.registers	
	def getCoils(self, startBit, bitCount):
		plcStatus = self.client.read_coils(address=startBit,count=bitCount)
		self.manageTransactionCounter()
		return plcStatus.bits
	def setCoils(self, address, values):
		self.client.write_coils(address, values)
		self.manageTransactionCounter()
	def getMaintenanceCode(self):
		
		if self.coils[1] == True:	#0 = normal mode
			return 0
		elif self.coils[5] == True: #1 = mainteannce
			return 1
		elif self.coils[7] == True: #2 = testing
			return 2
		return 9
	
	def queueUpdate(self):
		lightData = ''
		for x in self.registers[0:4]:
			lightData = lightData + str(x) + "\n"		
		returnData = "LightData90210\n" + self.plcName + "\n" + lightData + str(self.getMaintenanceCode())
		#addToScadaMessageQueue(returnData)
		broadCastMessage(returnData)
		
	def handleRunningConnectionError(self, e):
		#take care of a connecion issue to this plc. Report the Error to any websockets and retry in 5 seconds
		
		self.errorMsg = "The following error occured: " + str(e) + "\nTrying again in 5 seconds"
		self.errorFlag = True
		broadCastMessage("ERROR: No connection to : " + self.plcName)
		time.sleep(5)
		self.errorMsg = ''
		self.errorFlag = False
		self.run()
	def run(self):
		while True:
			try:
				self.coils = self.getCoils(0,10)
				rr = self.getHoldingRegisters(0,10)
				#a = self.registers
				#registerIsSame = len(a)==len(rr) and len(a)==sum([1 for i,j in zip(a,rr) if i==j]) #Compares the 2 lists
				#if registerIsSame == False: #registers have changed. update all websocket clients
						#self.registers = rr
						#send an update to the websocket
						
						
				time.sleep(1.0)
				self.registers = rr
				self.queueUpdate()
			except Exception as e:
				self.handleRunningConnectionError(e)
				


	def setNormalModeCommand(self):
		#sets the plc to normal operation
		
		addToScadaMessageQueue("Putting " + self.plcName + " into Normal mode");
		try:
			rq = self.setCoils(0,[1,0])
			status = self.getCoils(0,10)
			success = status[0] or status[1]
			if success:
				pass
			else:
				addToScadaMessageQueue("Unable to put " + self.plcName + " into NORMAL mode")
				broadCastMessage("Error code 4: Unable to put " + self.plcName + " into NORMAL mode")
		except Exception as e:
				addToScadaMessageQueue(e)
				broadCastMessage("Error code 5: The connection with " + self.plcName + " has been lost")
		
	def setTestMode(self):
		#sets the plc to TEST operation
		addToScadaMessageQueue("Putting " + self.plcName + " into TEST mode");
		
		try:
			rq = self.setCoils(6,[1])
			status = self.getCoils(0,10)
			success = status[6] or status[7]
			if success:
				pass
			else:
				addToScadaMessageQueue("Unable to put " + self.plcName + " into TEST mode")
				broadCastMessage("Error code 4: Unable to put " + self.plcName + " into TEST mode")
		except Exception as e:
				addToScadaMessageQueue(e)
				broadCastMessage("Error code 5: The connection with " + self.plcName + " has been lost")
	def setMaintenanceMode(self):
		#sets the plc to Maintenance Mode
		addToScadaMessageQueue("Putting " + self.plcName + " into maintenance mode");
		
		try:
			rq = self.setCoils(4,[1])
			status = self.getCoils(0,10)
			success = status[4] or status[5]
			if success:
				pass
			else:
				addToScadaMessageQueue("Unable to put " + self.plcName + " into MAINTENANCE mode")
				broadCastMessage("Error code 4: Unable to put " + self.plcName + " into MAINTENANCE mode")
		except Exception as e:
				addToScadaMessageQueue(e)
				broadCastMessage("Error code 5: The connection with " + self.plcName + " has been lost")
			
def sendPLCNames():
	#sends the names of the PLC's to the websocket for human display
	strMessage = 'NAMES'
	for plc in plcs:
		strMessage = strMessage + "\n" + plc.plcName
		plc.queueUpdate()
	broadCastMessage(strMessage)
	

def registerSocket(sock):
	socks.append(sock)

def unRegisterSocket(sock):
	if sock in socks:
		socks.remove(sock)
def broadCastMessage(msg):
	for sock in socks:
		sock.sendAMessage(msg.encode('utf8'))

		
def processMessage(msg):
	#process message from the HMI
	for plc in plcs:
		if plc.plcName in msg:
			#message for this plc
			if "MAINTENANCE" in msg:		#put it in maintenance mode
				plc.setMaintenanceMode()
			elif "TEST" in msg:			#put it in TEST mode
				plc.setTestMode()
			elif "NORMAL" in msg:				#put it in normal mode
				plc.setNormalModeCommand()
			else:
				addToScadaMessageQueue("received command for: " + plc.plcName + " but I don't know what to do")

#################################
		# coils[0] = 1 - machine initialization
		# coils[1] = 1 - run normal operations
		# coils[2] = 1 - east/west side is green or yellow
		# coils[3] = 1 - north/south side is green yellow
		# coils[4] = 1 - put the machine into maintenancemode (ALL FLASHING RED LIGHTS)
		# coils[5] = 1 - machine moved to mainteance mode
		# coils[6] = 1 - puts the machine into TEST Mode (ALL LIGHTS ON)
		# coils[7] = 1 - machine moved to TEST mode
		# holdingRegister[0,2] - north/south light state	-0 = red, 1 = yellow, 2 = green, 3 = ALL OFF, 4 = ALL ON
		# holdingRegister[1,3] - east/west light state
		# holdingRegister [4] - timer/counter
		# holdingRegisters [5,6,7] - timer values that cause an increment in logic
################


def signal_handler(signal, frame):
    print ('You pressed Ctrl+C!')
    reactor.stop()
    sys.exit(0)

def updateWebSocketStatus(msg):
	global webSocketStatus 
	webSocketStatus = msg

def addToScadaMessageQueue(msg):
	#########
	###holds up to 5 mesages for the showDisplay method to display to an
	### operator
	global operatorMessages
	if len(operatorMessages) >= 5:
		operatorMessages.pop(0)
	operatorMessages.append(msg)
	
		

def showDisplay(args):
	global clock
	messageQueueTimer = 5
	
	while True:
		os.system('cls' if os.name == 'nt' else 'clear')
		print('*' * 120)
		print(' ' * 30 + " Welcome to the CPT 154 Traffic Light SCADA" + "\t" + "UPTIME: " + str(int(clock/60)) + ":" 
			+ str(int(math.fmod(clock,60))) + ' ' * 20 + '\n')
		for plc in plcs:
			print('\t' + plc.plcName + "@" + str(plc.plcIP) + ":" + str(plc.plcPort))
			if plc.errorFlag == False:
				print("Registers: " + str(plc.registers))
				coilint = numpy.multiply(plc.coils,1)
				print("Coils: " + str(coilint)+"\n\n")
			else:
				print("\t!!!! Connection Error !!!!\n\n")
			
		print("HMI Websocket status: "  + str(webSocketStatus)+"\n\n")
		print("\t\t\tMESSAGES\n")
		
		for x in operatorMessages:
			print(x)
		print('*' * 120)
		clock = clock + 1
		if len(operatorMessages) > 0:
			messageQueueTimer -= 1
			if messageQueueTimer == 0:
				messageQueueTimer = 5
				operatorMessages.pop(0)
		time.sleep(1)

if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	socks = []
	plcs = []
	
	plcInt = plcInterrogator('10.0.0.10', 502, "NW Street")
	plcs.append(plcInt)
	plcInt = plcInterrogator('10.0.0.20', 502, "SW Street")
	plcs.append(plcInt)
	plcInt = plcInterrogator('10.0.0.30', 502, "NE Street")
	plcs.append(plcInt)
	plcInt = plcInterrogator('10.0.0.40', 502, "SE Street")
	plcs.append(plcInt)
	
	#start the PLC interrogation threads
	for plcInt in plcs:
		plcInt.start()
		
	factory = WebSocketServerFactory()
	factory.protocol = MyServerProtocol

	#continuously update the terminal
	thread = Thread(target = showDisplay, args =(plcs,))
	thread.start()

	#start the websocket listener
	port = 9999
	reactor.listenTCP(port, factory)
	print("Websocket server is listening on: " + str(port))
	reactor.run()




