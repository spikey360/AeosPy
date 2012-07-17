import btrmserver
import os
import view
import wx
import thread

cc=0 #command count
btrmserver.BTRMDEBUG=1 #debug flag

serv=btrmserver.Server()
serv.startServer()
serv.listenForRemote()
hd=serv.handshake()
if hd==1:
	print "Handshake successful"
else:
	print "Handshake failed"
rd=serv.getDock()
oplist={"-1":"Default"}
detlist={}
##set operation list here
dirpath="/home/riju/Pictures/wallpaper/"
if os.access(dirpath,os.R_OK)==True:
	z=os.listdir(dirpath)
	opc=1
	if dirpath.endswith("/")==False:
		dirpath=dirpath+"/"
	for y in z:
		if y.endswith(".jpg") or y.endswith(".gif") or y.endswith(".png"):
			#add operation
			rd.oplist.addOperation((y[:16],str(opc)))
			#add detail
			rd.oplist.addDetails(({dirpath+y:"Location"},str(opc)))
			opc+=1
else:
	print "Unable to load file list from folder"
rd.sendOperationList(rd.oplist.getOplist())
##SETUP VIEWER#
app=wx.App(redirect=False)

rd.controllable=view.Viewer(title="AeosPy Viewer",winsize=(500,400),folder=dirpath)
rd.controllable.Show()


###############
def remoteLoop():
	global rd, cc, serv
	print "reading from remote..."
	while (rd.readProtocolString()==True):
		#do something
		cc+=1
	#x=raw_input("Press enter...")
	serv.closeServer()
def appLoop():
	global app
	app.MainLoop()

print "Strating thread"
thread.start_new_thread(appLoop,())
	
remoteLoop()
###############
#app.MainLoop()
