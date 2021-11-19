#! /usr/local/bin/python3.6

'''
##########################################
# Traffic Light PLC
# Version: 1.7
# Date: 04/2018
# License: MIT
# Description: This python script operates as a Traffic Light PLC system
# simulating modbus style registers and coils to loop through traffic light logic.
# Additionally, it hosts a TCP modbus listener that responds to modbus queries. 
# Source code for the modbus implementation is here: https://github.com/riptideio/pymodbus.
# 4 PLC's are threaded and listen on 4 separate interfaces
# Python version: 3.6
# Author: Matthew
#########################################
'''



# --------------------------------------------------------------------------- # 
# import the various server implementations
# --------------------------------------------------------------------------- # 
from pymodbus.server.asynchronous  import StartTcpServer
from pymodbus.server.asynchronous  import StartUdpServer
from pymodbus.server.asynchronous  import StartSerialServer
from pymodbus.server.asynchronous  import ModbusServerFactory

from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.transaction import ModbusRtuFramer, ModbusAsciiFramer
from twisted.internet import protocol
from twisted.internet.protocol import ServerFactory
from twisted.internet import reactor
from pymodbus.constants import Defaults
from pymodbus.factory import ServerDecoder
from pymodbus.datastore import ModbusServerContext
from pymodbus.device import ModbusControlBlock
from pymodbus.device import ModbusAccessControl
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.exceptions import NoSuchSlaveException
from pymodbus.transaction import ModbusSocketFramer, ModbusAsciiFramer
from pymodbus.pdu import ModbusExceptions as merror
from pymodbus.internal.ptwisted import InstallManagementConsole
from pymodbus.compat import byte2int
from pymodbus.compat import IS_PYTHON3
import signal, sys, time, threading, random, os

class plcSlave():
	def __init__(self, plcIP, plcPort, initialRegisters, plcName):
		self.plcIP=plcIP
		self.plcPort=plcPort
		self.dataStore = 0
		self.context = 0
		self.identity = 0
		self.initialRegisters =  initialRegisters
		self.plcName = plcName
		self.run_async_server(address=(self.plcIP,self.plcPort))
	def run_async_server(self, address):
		# ----------------------------------------------------------------------- # 
		# initialize your data store
		# ----------------------------------------------------------------------- # 
		# The datastores only respond to the addresses that they are initialized to
		# Therefore, if you initialize a DataBlock to addresses from 0x00 to 0xFF,
		# a request to 0x100 will respond with an invalid address exception.
		# This is because many devices exhibit this kind of behavior (but not all)
		#
		#     block = ModbusSequentialDataBlock(0x00, [0]*0xff)
		#
		# Continuing, you can choose to use a sequential or a sparse DataBlock in
		# your data context.  The difference is that the sequential has no gaps in
		# the data while the sparse can. Once again, there are devices that exhibit
		# both forms of behavior::
		#
		#     block = ModbusSparseDataBlock({0x00: 0, 0x05: 1})
		#     block = ModbusSequentialDataBlock(0x00, [0]*5)
		#
		# Alternately, you can use the factory methods to initialize the DataBlocks
		# or simply do not pass them to have them initialized to 0x00 on the full
		# address range::
		#
		#     store = ModbusSlaveContext(di = ModbusSequentialDataBlock.create())
		#     store = ModbusSlaveContext()
		#
		# Finally, you are allowed to use the same DataBlock reference for every
		# table or you you may use a seperate DataBlock for each table.
		# This depends if you would like functions to be able to access and modify
		# the same data or not::
		#
		#     block = ModbusSequentialDataBlock(0x00, [0]*0xff)
		#     store = ModbusSlaveContext(di=block, co=block, hr=block, ir=block)
		#
		# The server then makes use of a server context that allows the server to
		# respond with different slave contexts for different unit ids. By default
		# it will return the same context for every unit id supplied (broadcast
		# mode).
		# However, this can be overloaded by setting the single flag to False
		# and then supplying a dictionary of unit id to context mapping::
		#
		#     slaves  = {
		#         0x01: ModbusSlaveContext(...),
		#         0x02: ModbusSlaveContext(...),
		#         0x03: ModbusSlaveContext(...),
		#     }
		#     context = ModbusServerContext(slaves=slaves, single=False)
		#
		# The slave context can also be initialized in zero_mode which means that a
		# request to address(0-7) will map to the address (0-7). The default is
		# False which is based on section 4.4 of the specification, so address(0-7)
		# will map to (1-8)::
		#
		#     store = ModbusSlaveContext(..., zero_mode=True)
		# ----------------------------------------------------------------------- # 
		self.dataStore = ModbusSlaveContext(
			di=ModbusSequentialDataBlock(0, [17]*100),
			co=ModbusSequentialDataBlock(0, [17]*100),
			hr=ModbusSequentialDataBlock(0, [17]*100),
			ir=ModbusSequentialDataBlock(0, [17]*100))
		self.context = ModbusServerContext(slaves=self.dataStore, single=True)
		
		# ----------------------------------------------------------------------- # 
		# initialize the server information
		# ----------------------------------------------------------------------- # 
		# If you don't set this or any fields, they are defaulted to empty strings.
		# ----------------------------------------------------------------------- # 
		self.identity = ModbusDeviceIdentification()
		self.identity.VendorName = 'Pymodbus'
		self.identity.ProductCode = 'PM'
		self.identity.VendorUrl = 'http://github.com/bashwork/pymodbus/'
		self.identity.ProductName = 'Pymodbus Server'
		self.identity.ModelName = 'Pymodbus Server'
		self.identity.MajorMinorRevision = '1.0'
		
		# ----------------------------------------------------------------------- # 
		# run the server (listener)
		# ----------------------------------------------------------------------- # 

		framer  = ModbusSocketFramer
		factory = ModbusServerFactory(self.context, framer, self.identity)
		reactor.listenTCP(address[1], factory, interface=address[0])

	def start(self):
		coil_list = 1
		holdregister = 3

		self.setCoils(0x00,[1,0,0,0,0,0,0,0,0,0,0,0,0])
		self.setHoldingRegisters(0x00,self.initialRegisters) 
		threading.Thread(target = self.operateLightTimer).start()

	def getHoldingRegisters(self, startByte, bytesCount):
	    return self.dataStore.getValues(3, startByte,count=bytesCount)
		
	def getCoils(self, startBit, bitCount):
	    return self.dataStore.getValues(1,startBit,count=bitCount)

	def setHoldingRegisters(self,address,values):
		
		self.dataStore.setValues(3,address,values)
	def setCoils(self, address, values):
		self.dataStore.setValues(1,address,values)
	
	def changeLightColor(self,northsouth, color):
		
	    registers = self.getHoldingRegisters(0x00,4)
	    if northsouth == 1:
		    registers[0] = color
		    registers[2] = color
	    else:
		    registers[1] = color
		    registers[3] = color
	    self.dataStore.setValues(3,0x00,registers)
	    
	def operateLightTimer(self):
		#################################
		# coils[0] = 1 - machine initialization (move to normal operations)
		# coils[1] = 1 - machine moved to normal operations
		# coils[2] = 1 - east/west side is green or yellow
		# coils[3] = 1 - north/south side is green yellow
		# coils[4] = 1 - put the machine into maintenancemode (ALL FLASHING RED LIGHTS)
		# coils[5] = 1 - machine moved to mainteance mode
		# coils[6] = 1 - puts the machine into TEST Mode (ALL LIGHTS ON)
		# coils[7] = 1 - machine moved to TEST mode
		# holdingRegister[0,2] - north/south light state	0 = red, 1 = yellow, 2 = green, 3 = ALL OFF, 4 = ALL ON
		# holdingRegister[1,3] - east/west light state
		# holdingRegister [4] - timer/counter
		# holdingRegisters [5,6,7] - timer values that cause an increment in logic
		################
		
		coils = self.getCoils(0,10)
		
		#this is the main operation loop
		while True:
			coils = self.getCoils(0,10)
			regs = self.getHoldingRegisters(0,10)

			if coils[0] == 1: 			#initialize NORMAL OPS
				print("The traffic light at: " + str(self.plcName) + " is starting")
				self.setCoils(0x00,[0,1,1,0,0,0,0,0,0])
				self.setHoldingRegisters(0x00,[0,2,0,2,0,10,12,14]) 
			elif coils[4] == 1:			#move into MAINTENANCE
				print("The traffic light at: " + str(self.plcName) + " is going into MAINTENANCE")
				self.setCoils(0x00,[0,0,0,0,0,1,0,0,0])
				self.setHoldingRegisters(0x00,[0,0,0,0,0])
			elif coils[6] == 1:			#move into TEST
				print("The traffic light at: " + str(self.plcName) + " is going into TEST mode")
				self.setCoils(0x00,[0,0,0,0,0,0,0,1,0])
				self.setHoldingRegisters(0x00,[0,0,0,0,0])
			counter = regs[4]
			print(self.plcName + "....Coils: " + str(coils[0:10]) +"\t\tRegisters: " + str(regs[0:10]))
			if coils[1] == True:						##standard traffic light operation		
				
				self.setHoldingRegisters(4,[counter + 1])
				if counter == regs[5]: #change the green to yellow
					sys.stdout.write("X")
					sys.stdout.flush() 
					if coils[2] == 1:
						self.changeLightColor(0, 1)		#change the east west side to yellow
					if coils[3] == 1:
						self.changeLightColor(1,1)		#change the north/south side to yellow
						
				elif counter == regs[6]: #everyone goes to red
					sys.stdout.write("X")
					sys.stdout.flush()
					self.changeLightColor(1,0)
					self.changeLightColor(0,0)
					
				elif counter == regs[7]: #change the red light to green (for the favored side)
					sys.stdout.write("X")
					sys.stdout.flush()
					if coils[2] == 1:	#east/west was green, change it to red
						self.setCoils(0x02,[0,1])
						self.changeLightColor(1,2)
					elif coils[3] == 1:	#north/south was green, change it to red
						self.setCoils(0x02,[1,0])
						self.changeLightColor(0,2)
					self.setHoldingRegisters(0x04,[0])
				else:
					sys.stdout.write(".")
					sys.stdout.flush()
				time.sleep(1)
			elif coils[5] == True:							##maintenance
				if regs[0] == 0: 	#displaying a red light, make it flash
					self.setHoldingRegisters(0,[3,3,3,3])
				elif regs[0] == 3:							#blank light, change to red
					self.setHoldingRegisters(0,[0,0,0,0])
				else:
					self.setHoldingRegisters(0,[3,3,3,3])
				time.sleep(1)
			elif coils[7] == True:						#test mode
				if regs[0] == 3: 	#displaying a red light, make it flash
					self.setHoldingRegisters(0,[4,4,4,4])
				elif regs[0] == 4:							#blank light, change to red
					self.setHoldingRegisters(0,[3,3,3,3])
				else:
					self.setHoldingRegisters(0,[3,3,3,3])
				time.sleep(1)

def signal_handler(signal, frame):
	print('interrupt')
	print('hello world')
	try:
		reactor.stop()
		sys.exit(0)
	except Exception as e:
		print(e)
	# try:
	# 	reactor.stop()
	# 	sys.exit(0)
	# except Exception as e:
	# 	print(e)
	# 	print("trying to quit")
	# 	reactor.stop()
	# 	sys.exit(0)

if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	try:
		plc1 = plcSlave("127.0.0.1", 502, initialRegisters=[0,2,0,2,10,12,14], plcName="NW Street")
		plc1.start()
		plc2 = plcSlave("127.0.0.1", 503, initialRegisters=[0,2,0,2,10,12,14],plcName= "SW Street")
		plc2.start()
		plc3 = plcSlave("127.0.0.1", 504, initialRegisters=[0,2,0,2,10,12,14], plcName="NE Street")
		plc3.start()
		plc4 = plcSlave("127.0.0.1", 505, initialRegisters=[0,2,0,2,2,4,6], plcName="SE Street")
		plc4.start()
		
		reactor.run()
	except Exception as e:
		print("An Error Occured. It is likely that you don't have an interface to bind to interfaces available:\n\t" +
				"Configure these interfaces on your machine or modify the script")
		print(e)
	