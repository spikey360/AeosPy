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

import wx
import os

class PicturePanel(wx.Panel):
	bmp=None
	drawLabel=True
	presentZoomLevel=1.00
	#tuple describing point from where viewport has its origin
	viewpoint=(0,0)
	def __init__(self,parent):
		wx.Panel.__init__(self,parent,size=(890,500))
		self.frame=parent
		self.Bind(wx.EVT_PAINT,self.onPaint)
		
	def onPaint(self, evt):
		"""
		Add a picture to the background
		"""
		# yanked from ColourDB.py
		dc = None
		if not dc:
			dc = wx.ClientDC(self)
			rect = self.GetUpdateRegion().GetBox()
			dc.SetClippingRect(rect)
		##now draw image
		img=wx.Image(self.bmp)
		iw=img.GetWidth()
		ih=img.GetHeight()
		nw=iw
		nh=ih
		ar=(iw+0.0)/(ih+0.0)
		w,h=dc.GetSize()
		if iw>=w:
			nw=w
			nh=w/ar
		if nh>h:
			nh=h
			nw=h*ar
		sw=iw*self.presentZoomLevel
		sh=ih*self.presentZoomLevel
		(sx,sy)=self.viewpoint
		#check ranges before painting
		if (sx+sw)>iw or (sy+sh)>ih:
			self.vpReset()
			sw=iw*self.presentZoomLevel
			sh=ih*self.presentZoomLevel
			(sx,sy)=self.viewpoint
		bmp=img.GetSubImage((sx,sy,sw,sh)).Scale(nw,nh).ConvertToBitmap()
		self.SetSize((bmp.GetWidth(),bmp.GetHeight()))
		presentZoomLevel=1
		dc.Clear()
		dc.DrawBitmap(bmp, w/2-nw/2, h/2-nh/2)
		#draw label
		dc.SetTextForeground(wx.Colour(255,255,255))
		if self.drawLabel:
			tw,th=dc.GetTextExtent(self.bmp)
			dc.DrawText(self.bmp,(iw/2-tw/2),5)
		#change the window title
		self.frame.SetLabel("AeosPy Viewer"+self.bmp)
		
	def setImage(self,bmp):
		self.bmp=bmp
		
	def showZoomedImage(self,zoom=True):
		#decrease zoom level
		if zoom==True:
			if self.presentZoomLevel>0.2:
				self.presentZoomLevel-=0.1
		else:
			if self.presentZoomLevel<1:
				self.presentZoomLevel+=0.1
				#need to calculate viewpoint again
	
	def setDirection(self,direction="u"):
		#(u)p, (d)own, (l)eft, (r)ight are the directions available
		step=50
		img=wx.Image(self.bmp)
		iw=img.GetWidth()
		ih=img.GetHeight()
		(vx,vy)=self.viewpoint
		vw=self.presentZoomLevel*iw
		vh=self.presentZoomLevel*ih
		#viewpoint is dependent upon presentZoomLevel
		if direction=="u":
			if (vy-step)>=0:
				vy-=step
				
			else:
				vy=0
		elif direction=="d":
			if (vy+step+vh)<=ih:
				vy+=step
				
			else:
				u=ih-vh-1
				vy=u
		elif direction=="l":
			if (vx-step)>=0:
				vx-=step
				
			else:
				vx=0
		elif direction=="r":
			if (vx+step+vw)<=iw:
				vx+=step
			else:
				u=iw-vw-1
				vx=u
		self.viewpoint=(vx,vy)
		#print vx,vy,vw,vh
	
	def vpReset(self):
		self.presentZoomLevel=1
		self.viewpoint=(0,0)

class Viewer(wx.Frame):
	picPanel=None
	dash=None
	nextButton=None
	prevButton=None
	fsButton=None
	piclist=None
	albumSize=0
	curr=0
	isFs=False
	conlist={}
	def __init__(self,title,winsize,folder):
		
		wx.Frame.__init__(self,None,title=title+" "+folder,size=winsize)
		self.Bind(wx.EVT_CLOSE,self.onClose)
		self.setAlbumFolder(folder)
		dpanel=wx.Panel(self)
		panel=wx.Panel(self)
		self.picPanel=PicturePanel(self)
		dash=wx.BoxSizer(wx.HORIZONTAL)
		nextButton=wx.Button(dpanel,label=">")
		nextButton.Bind(wx.EVT_BUTTON,self.onNext)
		prevButton=wx.Button(dpanel,label="<")
		prevButton.Bind(wx.EVT_BUTTON,self.onPrev)
		fsButton=wx.Button(dpanel,label="Fullscreen")
		fsButton.Bind(wx.EVT_BUTTON,self.onFullScreen)
		zoomButton=wx.Button(dpanel,label="+")
		zoomButton.Bind(wx.EVT_BUTTON,self.onZoomed)
		moozButton=wx.Button(dpanel,label="-")
		moozButton.Bind(wx.EVT_BUTTON,self.onMoozed)
		aboutButton=wx.Button(dpanel,label="About")
		aboutButton.Bind(wx.EVT_BUTTON,self.onAbout)
		dash.Add(prevButton)
		dash.Add(nextButton)
		dash.Add(fsButton)
		dash.Add(zoomButton)
		dash.Add(moozButton)
		dash.Add(aboutButton)
		dpanel.SetSizer(dash)
		dpanel.Layout()
		mainBox=wx.BoxSizer(wx.VERTICAL)
		mainBox.Add(self.picPanel)
		mainBox.Add(dpanel)
		panel.SetSizer(mainBox)
		panel.Layout()
		panel.SetAutoLayout(True)
		self.picPanel.setImage(self.piclist[self.curr])
		self.Center()
		#add all controls to conlist
		self.conlist[1]=("Fullscreen",self.toggleFullScreen)
		self.conlist[2]=("Zoom",self.zoom)
		self.conlist[3]=("Mooz",self.mooz)
		self.conlist[4]=("-Up",self.goUp)
		self.conlist[5]=("-Down",self.goDown)
		self.conlist[6]=("-Left",self.goLeft)
		self.conlist[7]=("-Right",self.goRight)
		self.conlist[8]=("Toggle Label",self.toggleLabel)
		
	def onClose(self,event):
		self.Destroy()
		
	def onAbout(self, event):
		dlg=wx.MessageDialog(self,"About AeosPy v1.2","Python application to use mobile device as remote control for browsing through picture album.\nCopyright (C) 2012  Spikey360\nThis program comes with ABSOLUTELY NO WARRANTY.\nThis is free software, and you are welcome to redistribute it",wx.OK|wx.ICON_INFORMATION)
		dlg.Center()
		dlg.ShowModal()
	def onNext(self,event):
		if self.curr<(self.albumSize-1):
			self.curr+=1
		self.picPanel.vpReset()
		self.picPanel.setImage(self.piclist[self.curr])
		self.picPanel.Refresh()
	def onPrev(self,event):
		if self.curr>=1:
			self.curr-=1
		self.picPanel.vpReset()
		self.picPanel.setImage(self.piclist[self.curr])
		self.picPanel.Refresh()
	
	def onFullScreen(self,event):
		self.toggleFullScreen()
	
	def onZoomed(self,event):
		self.zoom()
	
	def onMoozed(self,event):
		self.mooz()
		
	def onGoUp(self,event):
		self.goUp()
	def onGoDown(self,event):
		self.goDown()
	def onGoLeft(self,event):
		self.goLeft()
	def onGoRight(self,event):
		self.goRight()
	def onToggleLabel(self,event):
		self.toggleLabel()
	########################################################
	def toggleFullScreen(self):
		if self.isFs==False:
			self.ShowFullScreen(True,style=wx.FULLSCREEN_ALL)
			self.picPanel.SetSize(wx.DisplaySize())
			self.isFs=True
		else:
			self.ShowFullScreen(False)
			self.picPanel.SetSize((890,500))
			self.isFs=False
		self.picPanel.Refresh()
	
	def zoom(self):
		self.picPanel.showZoomedImage()
		self.picPanel.Refresh()
	
	def mooz(self):
		self.picPanel.showZoomedImage(zoom=False)
		self.picPanel.Refresh()
		
	def goUp(self):
		self.picPanel.setDirection(direction="u")
		self.picPanel.Refresh()
	def goDown(self):
		self.picPanel.setDirection(direction="d")
		self.picPanel.Refresh()
	def goLeft(self):
		self.picPanel.setDirection(direction="l")
		self.picPanel.Refresh()
	def goRight(self):
		self.picPanel.setDirection(direction="r")
		self.picPanel.Refresh()
	def toggleLabel(self):
		if self.picPanel.drawLabel:
			self.picPanel.drawLabel=False
		else:
			self.picPanel.drawLabel=True
		self.picPanel.Refresh()
	#########################################################
	def opControl(self,op):
		#op an integer
		self.curr=op-1
		#change self.curr accordingly
		self.picPanel.vpReset()
		self.picPanel.setImage(self.piclist[self.curr])
		self.picPanel.Refresh()
		
	def conControl(self,op):
		(n,f)=self.conlist[op]
		f()
		
	def setAlbumFolder(self,x):
		if os.access(x,os.R_OK)==False:
			return
		z=os.listdir(x)
		if x.endswith("/")==False:
			x=x+"/"
		self.piclist={}
		self.albumSize=0
		for y in z:
			l=y.lower()
			if l.endswith(".jpg") or l.endswith(".gif") or l.endswith(".png"):
				self.piclist[self.albumSize]=x+y
				self.albumSize=self.albumSize+1

#app=wx.App(redirect=False)

#view=Viewer(title="AeosPy Viewer",winsize=(500,400),folder="/home/riju/Pictures/wallpaper/")
#view.Show()

#app.MainLoop()
