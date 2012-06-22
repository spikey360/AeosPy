#Message.py

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
	
	def __init__(self):
		print "Initializing"
	
	def getName(self):
		return self.Name
	
	def establishConnection(self):
		print "Establishing connection"
	 
