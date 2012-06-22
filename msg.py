#Message.py

##DEVICE#STATES##
init=0x01 #initialized
conni=0x10 #connecting
connd=0x100 #connected
ready=0x1000 #ready
busy=0x100000 #busy
dead=0x1000000 #closed
#################
class Message:
	numbers=[]
	message=""
	device=None
	
	def __init__(self,numbers,message,device):
		self.numbers=numbers
		self.message=message
		self.device=device
	def addNumber(self,number):
		return self.numbers;

	def removeNumber(self,Number):
		return 0
	def getMessage(self):
		return self.message
		
	def setMessage(self,x):
		self.message=x


class Device:
	devnum=0
	devaddr=None
	name=""
	sock=None
	state=0
	
	def __init__(self):
		global init
		print "Initializing"
		state=init
	
	def getName(self):
		return self.Name
	
	def acceptConnection(self):
		global conni, connd
		state=conni
		print "Accepting connection"
		state=connd
	
	def getClient(self):
		print "returning instance of Client"
	
	def write(bytes):
		print "Write bytes to output"
	
	def read(bytes):
		print "Read bytes from input"

class Client:
	dev=None
	def __init__(self,dev):
		print "Client initialized now"
	def sendPicture(self,imgfile):
		print "Send imgfile to app":
	def getResponse(self):
		print "return Response by reading from ip"
