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

import btrmserver
import os
import view
import wx
import thread
import sys
import tempfile

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
if len(sys.argv)>1:
	dirpath=sys.argv[1]

if os.access(dirpath,os.R_OK)==True:
	z=os.listdir(dirpath)
	opc=1
	if dirpath.endswith("/")==False:
		dirpath=dirpath+"/"
	for y in z:
		y=y.lower()
		if y.endswith(".jpg") or y.endswith(".gif") or y.endswith(".png"):
			#add operation
			rd.oplist.addOperation((y[:16],str(opc)))
			#add detail
			w,h=wx.Image(dirpath+y).GetSize()
			rd.oplist.addDetails(({dirpath+y:"Location",str(w)+"x"+str(h):"Size"},str(opc)))
			#add thumb
			"""thumb=wx.Image(dirpath+y).Scale(64,64)
			data=None
			tempf=tempfile.NamedTemporaryFile()
			try:
				thumb.SaveFile(tempf.name,wx.BITMAP_TYPE_PNG)
				tempf.seek(0)
				data=tempf.read()
				
			finally:
				tempf.close()
			rd.oplist.addThumb((data,str(opc)))"""
			opc+=1
else:
	print "Unable to load file list from folder"

app=wx.App(redirect=False)	
rd.controllable=view.Viewer(title="AeosPy Viewer",winsize=(900,650),folder=dirpath)
##NOW ADD SOME CONTROLS
for m in rd.controllable.conlist:
	(code,nf)=(str(m),rd.controllable.conlist[m])
	(name,func)=nf
	rd.oplist.addControl((name,code))
##START SENDING OPLIST##
rd.sendOperationList(rd.oplist.getOplist())
rd.readProtocolString()
#also send control list
rd.sendOperationList(rd.oplist.getConlist(),protocol="c")
rd.readProtocolString()
##SETUP VIEWER#



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

print "Starting thread"
thread.start_new_thread(appLoop,())
	
remoteLoop()
###############
#app.MainLoop()
