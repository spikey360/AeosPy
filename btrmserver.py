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
		self.remotesock.sendall(msg)
	
	def readFromRemote(self,size=512):
		return self.remotesock.recv(size) #1KB read
	
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
	
	def __init__(self):
		#self.generateDetails(startdir)
		self.oplist={}
		self.detlist={}
		self.thumblist={}
	
	def getOplist(self):
		return self.oplist
	
	def getDetail(self,opcode):
		return self.detlist[opcode]
	
	def addOperation(self, operation):
		#operation is a tuple of format (<operation>,<opcode>)
		(opname,opcode)=operation
		self.oplist[opcode]=opname
		
	def addDetails(self,details):
		#details is a tuple of format (<details>,<opcode>)
		#<details> is a dictionary
		(det,opcode)=details
		self.detlist[opcode]=det
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
	
	def sendOperationList(self,oplist,protocol="l"):
		msg=""
		w=0
		#oplist is a dictionary oplist[opcode]=parameter
				
		msg=""
		#self.server.writeToRemote(protocol)
		msg=msg+protocol
		for k in oplist:
			(title,opcode)=(oplist[k],k)
			msg=msg+";"+title+":"+opcode
		#self.server.writeToRemote("\0")
		msg=msg+";\0"
		self.server.writeToRemote(msg)
		if BTRMDEBUG:
			print ">"+msg
	
	def sendPictureDetails(self,name,size):
		msg="p;"+name+";"+size+"\0"
		self.server.writeToRemote(msg)
	
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
			#dat=self.oplist.getThumb(op)
			#write thumbnail to remote
			return True
		if p=="x":
			op=ps[2:]
			if BTRMDEBUG:
				print "Changing picture"
			self.controllable.opControl(int(op))
			#write an acknowledgement
			self.sendAcknowledgement(opc=op)
			return True
		if p=="q":
			#quit, release resources and wait for the next connection
			self.sendAcknowledgement(acktype="q")
			return False
		#d for details reply with p;<name>;<size in B>
		#f for fetching picture, to implement later
		#x for executing opcode coming with it
		
		###########
		self.server.writeToRemote("[w]\0") #[w] tells remote that server waiting for response
		msg=self.server.readFromRemote()
		#expected format "[r]<opcode>"
		return msg
