"""
AeosPy
======
    Python application to use mobile device as remote control for browsing through picture album.
    Copyright (C) 2012  Spikey360

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
    You can mail me at spikey360@yahoo.co.in
"""

import bluetooth

##debug#flag
BTRMDEBUG=0
############
##states
init=0x01
listn=0x02
connd=0x03
########

class Server:
	state=0
	sock=None
	port=0
	uuid="ae05a5ea-459d-4225-9385-28f7ee7fa848"
	remotesock=None
	remoteaddr=None
	def startServer(self):
		global BTRMDEBUG, init
		if BTRMDEBUG:
			print "Initializing server"
		self.sock=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
		self.port=bluetooth.PORT_ANY
		self.sock.bind(("",self.port))
		if BTRMDEBUG:
			print "Bound to port",self.port
		self.sock.listen(1) #only one connection at a time
		if BTRMDEBUG:
			print "Advertising server"
		bluetooth.advertise_service(self.sock,"Aeos Bluetooth Remote Server",self.uuid)
		self.state=init #initialized
		if BTRMDEBUG:
			print "Initialized"
	def listenForRemote(self):
		global BTRMDEBUG, listn,connd
		self.state=listn
		if BTRMDEBUG:
			print "Listening for remote"
		self.remotesock,self.remoteaddr=self.sock.accept() #blocks
		self.state=connd
		if BTRMDEBUG:
			print "Connected to remote",self.remoteaddr
	
	def closeServer(self):
		self.sock.close()
		if BTRMDEBUG:
			print "Closed server socket"
		self.remotesock.close()
		if BTRMDEBUG:
			print "Closed client socket"
	
	def getDock(self):
		global connd, BTRMDEBUG
		if self.state==connd:
			if BTRMDEBUG:
				print "Creating remote dock"
			return RemoteDock(self)
			
		return None
	
	#here's where the real fun begins
	
	def writeToRemote(self,msg):
		try:
			self.remotesock.sendall(msg)
		except:
			self.closeServer()
	
	def readFromRemote(self,size=512):
		try:
			return self.remotesock.recv(size) #1KB read
		except:
			self.closeServer()
	
	def handshake(self):
		global connd
		if self.state!=connd:
			return None #should ideally throw an exception
		#challenge with a nonce
		nonce="Nonce\0"
		self.writeToRemote(nonce)
		if BTRMDEBUG:
			print "Nonce thrown"
		back=self.readFromRemote()
		print "Nonce received",back
		if nonce!=back:
			return 0
		return 1 #handshake done
################################################
class OperatorStore:
	oplist=None
	detlist=None
	thumblist=None
	conlist=None
	
	def __init__(self):
		#self.generateDetails(startdir)
		self.oplist={}
		self.detlist={}
		self.thumblist={}
		self.conlist={}
	
	def getOplist(self):
		return self.oplist
	
	def getDetail(self,opcode):
		return self.detlist[opcode]
	
	def getThumb(self,opcode):
		return self.thumblist[opcode]
	
	def getConlist(self):
		return self.conlist;
	
	def addOperation(self, operation):
		#operation is a tuple of format (<operation>,<opcode>)
		(opname,opcode)=operation
		self.oplist[opcode]=opname
		
	def addDetails(self,details):
		#details is a tuple of format (<details>,<opcode>)
		#<details> is a dictionary
		(det,opcode)=details
		self.detlist[opcode]=det
		
	def addThumb(self,thumbtup):
		#thumbtup is a tuple of format (<thumbnail data>,<opcode>)
		(thdata,opcode)=thumbtup
		self.thumblist[opcode]=thdata
	
	def addControl(self,control):
		(condata,concode)=control
		self.conlist[concode]=condata
################################################

class RemoteDock:
	server=None
	oplist=None
	controllable=None
	def __init__(self,server):
		self.server=server
		self.oplist=OperatorStore()
		
	def setControllable(self,ct):
		self.controllable=ct
	
	def sendOperationList(self,oplist,protocol="l",sendTitle=False):
		msg=""
		w=0
		#oplist is a dictionary oplist[opcode]=parameter
				
		msg=""
		#self.server.writeToRemote(protocol)
		msg=msg+protocol
		for k in oplist:
			(title,opcode)=("","")
			if sendTitle:
				(title,opcode)=(oplist[k],k)
			else:
				(title,opcode)=(k,k)
			msg=msg+";"+title+":"+opcode
		#self.server.writeToRemote("\0")
		msg=msg+";\0"
		self.server.writeToRemote(msg)
		if BTRMDEBUG:
			print ">"+msg
	
	def sendPictureMetadata(self,name,size):
		global BTRMDEBUG
		msg="n;"+name+";"+size+";\0"
		self.server.writeToRemote(msg)
		if BTRMDEBUG:
			print ">"+msg

	def sendAcknowledgement(self,acktype="x",opc="0"):
		global BTRMDEBUG
		msg="ack"+acktype+";"+opc+"\0"
		self.server.writeToRemote(msg)
		if BTRMDEBUG:
			print ">"+msg

	def readProtocolString(self):
		global BTRMDEBUG
		###########
		ps=self.server.readFromRemote()
		if BTRMDEBUG:
			print "<"+ps
		p=ps[:1] #the type of query
		if p=="d":
			op=ps[2:]
			det=self.oplist.getDetail(op)
			self.sendOperationList(det,protocol="p")
			#write a protocol string
			return True
		if p=="f":
			op=ps[2:]
			dat=self.oplist.getThumb(op)
			self.server.writeToRemote(dat)
			if BTRMDEBUG:
				print "Picture bytes written"
			return True
		if p=="x":
			op=ps[2:]
			if BTRMDEBUG:
				print "Changing picture"
			self.controllable.opControl(int(op))
			#write an acknowledgement
			self.sendAcknowledgement(opc=op)
			return True
		if p=="m":
			op=ps[2]
			if BTRMDEBUG:
				print "Sending metadata"
			dat=self.oplist.getThumb(op)
			self.sendPictureMetadata("Preview",str(len(dat)))
			return True
		if p=="c":
			op=ps[2]
			if BTRMDEBUG:
				print "Executing control"
			#do it
			self.controllable.conControl(int(op))
			self.sendAcknowledgement(acktype="c",opc=op)
			return True
		if p=="a":
			#acknowledgement
			return True
		if p=="q":
			#quit, release resources and wait for the next connection
			self.sendAcknowledgement(acktype="q")
			return False
		#d for details reply with p;<name>;<size in B>
		#f for fetching picture, to implement later
		#x for executing opcode coming with it
		
		###########
		return None
