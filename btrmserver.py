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
	
	def getDock():
		global connd
		if state==connd:
			if BTRMDEBUG:
				print "Creating remote dock"
			return RemoteDock(self)
			
		return None
	
	#here's where the real fun begins
	
	def writeToRemote(self,msg):
		remotesock.send(msg)
	
	def readFromRemote(self):
		return remotesock.recv(1024) #1KB read
	
	def handshake(self):
		global connd
		if self.state!=connd:
			return None #should ideally throw an exception
		#challenge with a nonce
		nonce="Nonce"
		writeToRemote(nonce)
		back=readFromRemote()
		if nonce!=back:
			return 0
		return 1 #handshake done

class RemoteDock:
	server=None
	def __init__(self,server):
		self.server=server
	
	def sendOperation(self,oplist):
		msg=""
		#oplist is a 3-tuple (image,title,opcode)
		(image,title,opcode)=oplist
		msg="[i]"+image+"[t]"+title+"[o]"+opcode+"[e]\0" #[e] signifies end of tuple
		server.writeToRemote(msg)
	
	def waitForOpcode():
		server.writeToRemote("[w]\0") #[w] tells remote that server waiting for response
		msg=server.readFromRemote()
		#expected format "[r]<opcode>"
		return msg[3:]